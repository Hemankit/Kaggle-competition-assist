from crewai import Crew, Task, Agent
from typing import Dict, Any
from routing.intent_router import parse_user_intent
from routing.capability_scoring import find_agents_by_subintent
from routing.registry import AUTOGEN_AGENT_REGISTRY
from .orchestrator_base import BaseOrchestratorUtils
from agents.base_agent import BaseAgent
from autogen import GroupChat, GroupChatManager
from llms.llm_loader import get_llm_from_config

class ReasoningOrchestrator:
    def __init__(self):
        self.utils = BaseOrchestratorUtils()
        self.agent_registry = AUTOGEN_AGENT_REGISTRY
        self.STRATEGY_PROMPT = (
            "Act like an expert Kaggle competitor. Prioritize stable CV, avoid overfitting to public LB, "
            "track experiments, and push back if the user skips key phases (like EDA or validation)."
        )

    def _instantiate_agent(self, agent_name: str) -> BaseAgent:
        entry = self.agent_registry.get(agent_name)
        if not entry:
            raise ValueError(f"Agent '{agent_name}' not found in AUTOGEN_AGENT_REGISTRY.")
        
        agent_class = entry.get("agent_class")
        if not issubclass(agent_class, BaseAgent):
            raise TypeError(f"Agent '{agent_name}' does not implement BaseAgent.")
        
        return agent_class()

    def route_and_create_crew(self, user_query: str, mode: str = None) -> dict:
        parsed_intent = parse_user_intent(user_query)
        reasoning_style = parsed_intent.get("reasoning_style")
        subintents = parsed_intent.get("sub_intents", [])

        # Auto-select mode if not provided
        mode = mode or parsed_intent.get("recommended_mode", "crewai")

        matched_agents = set()
        for subintent in subintents:
            matches = find_agents_by_subintent(
                subintent=subintent,
                reasoning_style=reasoning_style
            )
            for match in matches:
                matched_agents.add(match["agent"])

        # Log execution trace (activated agents) for this query
        self.utils.log_execution_trace(list(matched_agents))

        if not matched_agents:
            return {"error": "No agents matched. Please rephrase your query."}

        agent_objs = []

        # === CrewAI mode ===
        if mode == "crewai":
            tasks = []
            for agent_name in matched_agents:
                agent_instance = self._instantiate_agent(agent_name)
                crewai_agent = agent_instance.to_crewai()

                task = Task(
                    description=f"{self.STRATEGY_PROMPT}\n\nUser query: {user_query}",
                    expected_output="Detailed response with best practices and reasoning steps.",
                    agent=crewai_agent
                )
                agent_objs.append(crewai_agent)
                tasks.append(task)

            crew = Crew(agents=agent_objs, tasks=tasks)
            final_output = crew.run()

            return {
                "structured_intent": parsed_intent,
                "selected_agents": list(matched_agents),
                "selected_mode": mode,
                "final_response": final_output,
                "execution_trace": self.get_last_execution_trace()
            }

        # === AutoGen mode ===
        elif mode == "autogen":
            autogen_agents = []
            for agent_name in matched_agents:
                agent_instance = self._instantiate_agent(agent_name)
                agent = agent_instance.to_autogen()
                agent.system_message += f"\n\n{self.STRATEGY_PROMPT}"
                autogen_agents.append(agent)

            # Use Perplexity for AutoGen orchestration
            llm = get_llm_from_config(section="reasoning_and_interaction")
            
            group_chat = GroupChat(agents=autogen_agents, messages=[], max_round=8)
            # Note: AutoGen GroupChatManager will use the individual agent configs
            # which we already set to use Perplexity via llm_loader
            manager = GroupChatManager(groupchat=group_chat, llm_config={"config_list": [{"model": "sonar", "temperature": 0.3}]})
            final_output = manager.run(user_query)

            return {
                "structured_intent": parsed_intent,
                "selected_agents": list(matched_agents),
                "selected_mode": mode,
                "final_response": final_output,
                "execution_trace": self.get_last_execution_trace()
            }

        else:
            return {"error": f"Unsupported mode '{mode}'. Use 'crewai' or 'autogen'."}

    def get_last_execution_trace(self) -> list:
        """
        Returns the list of activated agents for the last query.
        """
        return self.utils.get_last_execution_trace()

    def run_single_agent(self, agent_name: str, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Run a single agent instead of a full crew/group"""
        context = context or {}
        
        try:
            # Get agent instance
            agent_instance = self._instantiate_agent(agent_name)
            
            # Create a simple task for the single agent
            task = Task(
                description=f"{self.STRATEGY_PROMPT}\n\nUser query: {query}",
                expected_output="Detailed response with best practices and reasoning steps.",
                agent=agent_instance.to_crewai()
            )
            
            # Create a crew with just this one agent and task
            crew = Crew(
                agents=[agent_instance.to_crewai()],
                tasks=[task],
                verbose=False
            )
            
            result = crew.kickoff()
            
            return {
                "agent_name": agent_name,
                "response": str(result),
                "updated_context": context
            }
            
        except Exception as e:
            return {
                "agent_name": agent_name,
                "error": str(e),
                "updated_context": context
            }

    def run(self, inputs: dict) -> dict:
        """
        Standardized run method for orchestrator interoperability.
        Accepts:
            {
                "query": "Your user query",
                "mode": "crewai" or "autogen" (optional)
            }
        Returns:
            {
                "structured_intent": ...,
                "selected_agents": [...],
                "selected_mode": ...,
                "final_response": ...,
                "execution_trace": [...]
            }
        """
        user_query = inputs.get("query", "")
        mode = inputs.get("mode")

        if not user_query:
            return {"error": "Missing 'query' in input."}

        return self.route_and_create_crew(user_query, mode)