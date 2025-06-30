# orchestrators/expert_orchestrator_langgraph.py

import json
from typing import Dict, Any, Optional, List

from langchain.chains.router import RouterChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

from llms.gemini_llm import ChatGoogleGenerativeAI
from routing.intent_router import MULTI_PROMPT_ROUTER_TEMPLATE
from routing.registry import AGENT_REGISTRY
from workflows.graph_workflow import compiled_graph


class ExpertSystemOrchestratorLangGraph:
    def __init__(self):
        self.routing_llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.2)

        # Dynamically generate destinations from AGENT_REGISTRY
        self.destinations = {
            agent_name: {
                "name": agent_obj.get_agent_id(),
                "description": agent_obj.get_description(),
                "chain": agent_obj
            }
            for agent_name, agent_obj in AGENT_REGISTRY.items()
        }

        self.destination_chains = {
            key: value["chain"] for key, value in self.destinations.items()
        }

        router_prompt = PromptTemplate.from_template(MULTI_PROMPT_ROUTER_TEMPLATE)

        self.router_chain = RouterChain.from_names_and_descriptions(
            names_and_descriptions=[
                (v["name"], v["description"]) for v in self.destinations.values()
            ],
            llm=self.routing_llm,
            prompt=router_prompt
        )

        self.aggregation_chain = LLMChain(
            llm=ChatOpenAI(
                model_name="mistralai/Mixtral-8x7b-Instruct-v0.1",
                openai_api_base="https://api.together.xyz/v1",
                openai_api_key="..."  # TODO: Replace with settings.yaml
            ),
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

        self.graph = compiled_graph

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
        from routing.capability_scoring import find_agents_by_subintent

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
        final_state = self.graph.invoke(initial_state, return_intermediate_steps=debug)
        return final_state if debug else final_state.get("final_response", "[No response generated]")

    def run_graph_debug(self, user_query: str):
        return self.handle_query(user_query, debug=True)


