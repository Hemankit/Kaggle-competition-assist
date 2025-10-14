from .expert_orchestrator_langgraph import ExpertSystemOrchestratorLangGraph
from .reasoning_orchestrator import ReasoningOrchestrator
from routing.dynamic_orchestrator import DynamicCrossFrameworkOrchestrator

class ComponentOrchestrator:
    def __init__(self):
        self.langgraph_orchestrator = ExpertSystemOrchestratorLangGraph()
        self.multi_agent_orchestrator = ReasoningOrchestrator()
        self.dynamic_orchestrator = DynamicCrossFrameworkOrchestrator()
        self.last_trace = {}

    def run(self, inputs: dict) -> dict:
        """
        Master run() method to dispatch to the appropriate orchestrator.
        Inputs:
            {
                "query": "user query here",
                "mode": "crewai" | "autogen" | "langgraph" | "dynamic",  # optional
                "debug": True or False                      # optional
            }
        
        Modes:
            - "dynamic": Autonomous cross-framework agent selection and interaction
            - "crewai": CrewAI-based multi-agent collaboration
            - "autogen": AutoGen conversational agents
            - "langgraph": LangGraph workflow-based orchestration
        """
        query = inputs.get("query", "")
        mode = inputs.get("mode", "langgraph")
        debug = inputs.get("debug", False)

        if not query:
            return {"error": "Missing 'query' in input."}

        if mode == "crewai" or mode == "autogen":
            result = self.multi_agent_orchestrator.run({
                "query": query,
                "mode": mode
            })
            if debug:
                self.last_trace = {
                    "type": "multi_agent",
                    "trace": self.multi_agent_orchestrator.get_last_execution_trace()
                }
            return result

        elif mode == "langgraph":
            result = self.langgraph_orchestrator.run_graph_debug(query) if debug else \
                     self.langgraph_orchestrator.run({"query": query})
            if debug:
                self.last_trace = {
                    "type": "langgraph",
                    "trace": result.get("execution_trace", [])
                }
                return result.get("result", result)
            return result

        elif mode == "dynamic":
            # Use the new dynamic cross-framework orchestrator
            result = self.dynamic_orchestrator.run(query)
            if debug:
                self.last_trace = {
                    "type": "dynamic_cross_framework",
                    "trace": result.get("execution_summary", {}),
                    "plan": result.get("plan")
                }
            return result

        else:
            return {"error": f"Unsupported mode: {mode}. Use 'crewai', 'autogen', 'langgraph', or 'dynamic'"}

    def get_debug_trace(self) -> dict:
        """
        Returns the last execution trace for developer debugging.
        """
        return self.last_trace
    
    def run_with_debug(self, query: str) -> dict:
        """
        Run with debug mode enabled.
        """
        return self.run({"query": query, "debug": True})