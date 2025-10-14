# orchestrators/expert_orchestrator_langgraph.py

import json
from typing import Dict, Any, Optional, List

# from langchain.chains.router import RouterChain  # Not available in current version
# from langchain_community.chat_models import ChatHuggingFace  # Not needed
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# from langchain_google_genai import ChatGoogleGenerativeAI  # Temporarily disabled due to metaclass conflict
from routing.registry import AGENT_CAPABILITY_REGISTRY
# from workflows.graph_workflow import compiled_graph  # Commented out to avoid circular import
from dotenv import load_dotenv
load_dotenv()

class ExpertSystemOrchestratorLangGraph:
    def __init__(self):
        # Use Perplexity for reasoning and routing
        from llms.llm_loader import get_llm_from_config
        self.routing_llm = get_llm_from_config(section="reasoning_and_interaction")

        # Dynamically generate destinations from AGENT_CAPABILITY_REGISTRY
        self.destinations = {
            agent_name: {
                "name": agent_name,
                "description": agent_obj.get("description", ""),
                "chain": agent_obj.get("agent_class")
            }
            for agent_name, agent_obj in AGENT_CAPABILITY_REGISTRY.items()
        }

        self.destination_chains = {
            key: value["chain"] for key, value in self.destinations.items()
        }

        # Simple router prompt template
        router_prompt = PromptTemplate.from_template("""
Given the user query, select the most appropriate agent from the available options:

Available agents:
{names_and_descriptions}

Query: {input}

Select the most appropriate agent name:
""")

        # Simplified router - just use a basic LLM chain for routing
        self.router_chain = self.routing_llm

        # Use Perplexity for aggregation (reasoning + search-augmented context)
        self.aggregation_chain = LLMChain(
            llm=self.routing_llm,  # Use the same Perplexity LLM for aggregation
            prompt=PromptTemplate.from_template(
                """
                You are a smart AI orchestrator. Several expert agents have responded to a user's question.

                Here are their responses:
                {agent_responses}

                Based on these, synthesize a coherent and helpful answer. Make sure to:
                - Combine overlapping insights
                - Prioritize concrete suggestions
                - Omit redundant explanations
                - Be concise, clear, and actionable
                """
            )
        )

        # Import compiled_graph lazily to avoid circular imports
        from workflows.graph_workflow import compiled_graph
        self.graph = compiled_graph
        self.last_execution_trace = []  # Stores the last execution trace (list of activated nodes)

    def route_to_agents(self, original_query: str) -> Dict[str, Any]:
        few_shot_prompt = f"""
You are an expert query router. Given a user query, extract:

- intent
- sub_intents
- input_references
- reasoning_style
- preferred_agents
- metadata_flags
- confidence_score
- uncertain_parse
- query_mode

Q: "{original_query}"
A:
"""

        router_output = self.routing_llm(few_shot_prompt)

        try:
            structured_query = json.loads(router_output)
        except Exception as e:
            structured_query = {
                "intent": "reasoning",
                "sub_intents": [],
                "input_references": [],
                "reasoning_style": "default",
                "preferred_agents": [],
                "metadata_flags": {},
                "confidence_score": 0.0,
                "uncertain_parse": True,
                "query_mode": "exploration",
                "llm_parse_error": str(e),
                "raw_output": router_output
            }

        intent = structured_query.get("intent", "reasoning")

        if structured_query.get("uncertain_parse", False):
            structured_query["destination_chain_name"] = "multi_hop_reasoning"
        else:
            structured_query["destination_chain_name"] = (
                intent if intent in self.destination_chains else None
            )

        return structured_query

    def explain_agent_routing(self, structured_query: Dict[str, Any]) -> List[str]:
        from ..routing.capability_scoring import find_agents_by_subintent

        subintents = structured_query.get("sub_intents", [])
        style = structured_query.get("reasoning_style")
        explanations = []

        for subintent in subintents:
            matches = find_agents_by_subintent(subintent, style)
            for match in matches:
                explanations.append(f"{match['agent']} matched for {subintent} ({match['explanation']})")

        return explanations

    def aggregate_response(self, agent_responses: List[Dict[str, str]]) -> str:
        responses_text = "\n\n".join(
            [f"{i+1}. {resp['agent_name']}: {resp['response']}" for i, resp in enumerate(agent_responses)]
        )
        return self.aggregation_chain.run(agent_responses=responses_text)

    def handle_query(self, user_query: str, debug: bool = False) -> str:
        initial_state = {"original_query": user_query}
        # Remove return_intermediate_steps parameter (not supported in newer LangGraph versions)
        final_state = self.graph.invoke(initial_state)
        
        if debug:
            # For debug mode, use stream to capture intermediate steps
            try:
                # Use stream with debug mode to capture intermediate steps
                stream_results = list(self.graph.stream(initial_state, stream_mode="debug"))
                self.last_execution_trace = []
                
                for mode, data in stream_results:
                    if mode == "debug" and isinstance(data, dict) and "node" in data:
                        self.last_execution_trace.append(data["node"])
            except Exception as e:
                # Fallback if streaming fails
                print(f"Debug streaming failed: {e}")
                self.last_execution_trace = []
            
            return final_state
        else:
            self.last_execution_trace = []
            return final_state.get("final_response", "[No response generated]")

    def get_last_execution_trace(self) -> List[str]:
        """
        Returns the list of activated nodes for the last query (if debug mode was used).
        """
        return self.last_execution_trace

    def run_graph_debug(self, user_query: str):
        """
        Runs the graph in debug mode and returns both the final state and execution trace.
        """
        result = self.handle_query(user_query, debug=True)
        trace = self.get_last_execution_trace()
        return {"result": result, "execution_trace": trace}
    
    

    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Standardized run method to be used by orchestrators.
        Executes the LangGraph workflow with optional debug mode.
        Returns final response and optionally the execution trace.
        """
        user_query = inputs.get("query", "")
        debug = inputs.get("debug", False)
        if not user_query:
            return {"error": "Missing 'query' in input."}

        final_output = self.handle_query(user_query, debug=debug)
        if debug:
            return {
                "result": final_output,
                "execution_trace": self.get_last_execution_trace()
            }

        return {
            "result": final_output
        }

    def run_single_agent(self, agent_name: str, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Run a single agent using LangGraph workflow"""
        context = context or {}
        
        try:
            # Get agent instance from registry
            if agent_name not in AGENT_CAPABILITY_REGISTRY:
                raise ValueError(f"Agent '{agent_name}' not found in registry")
            
            agent_class = AGENT_CAPABILITY_REGISTRY[agent_name]["agent_class"]
            agent_instance = agent_class()
            
            # Execute agent directly (since we're running single agent, not full workflow)
            result = agent_instance.run(query, context)
            
            return {
                "agent_name": agent_name,
                "response": result.get("response", str(result)),
                "updated_context": result.get("updated_context", context)
            }
            
        except Exception as e:
            return {
                "agent_name": agent_name,
                "error": str(e),
                "updated_context": context
            }