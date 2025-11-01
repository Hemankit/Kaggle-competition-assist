# routing/dynamic_orchestrator.py

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

from .intent_router import parse_user_intent
from .capability_scoring import find_agents_by_subintent
from .registry import AGENT_CAPABILITY_REGISTRY, get_agent
# from orchestrators.reasoning_orchestrator import ReasoningOrchestrator
# from orchestrators.expert_orchestrator_langgraph import ExpertSystemOrchestratorLangGraph

logger = logging.getLogger(__name__)

class InteractionPattern(Enum):
    """Types of agent interactions possible"""
    SEQUENTIAL = "sequential"  # Agent A → Agent B → Agent C
    PARALLEL = "parallel"      # Agent A & B run simultaneously, then Agent C
    HIERARCHICAL = "hierarchical"  # Agent A coordinates Agents B & C
    COLLABORATIVE = "collaborative"  # Agents A & B work together iteratively
    CONSULTATIVE = "consultative"    # Agent A consults Agent B for advice
    CONVERSATIONAL = "conversational" # Natural conversation between agents
    VALIDATION = "validation"        # Agent A produces, Agent B validates
    EXPANSION = "expansion"          # Agent A produces, Agent B expands/refines

class FrameworkCapability(Enum):
    """Framework strengths for different interaction patterns"""
    CREWAI = "crewai"           # Best for: collaborative, hierarchical
    AUTOGEN = "autogen"         # Best for: conversational, consultative  
    LANGGRAPH = "langgraph"     # Best for: sequential, parallel, validation

@dataclass
class AgentSelection:
    """Represents a selected agent with metadata"""
    name: str
    framework: str
    confidence: float
    reasoning: str
    capabilities: List[str]

@dataclass
class InteractionPlan:
    """Complete plan for agent interactions"""
    pattern: InteractionPattern
    agents: List[AgentSelection]
    execution_order: List[int]  # Indexes into agents list
    expected_duration: str
    complexity_score: float

class DynamicCrossFrameworkOrchestrator:
    """
    Autonomous orchestrator that dynamically selects agents and frameworks
    based on query analysis, without hardcoded sequences.
    """
    
    def __init__(self):
        # Lazy imports to avoid circular dependencies
        self.crewai_orchestrator = None
        self.autogen_orchestrator = None 
        self.langgraph_orchestrator = None
        
        # Framework capability mapping
        self.framework_capabilities = {
            FrameworkCapability.CREWAI: {
                "patterns": [InteractionPattern.COLLABORATIVE, InteractionPattern.HIERARCHICAL],
                "strengths": ["task_delegation", "role_based_work", "structured_outputs"]
            },
            FrameworkCapability.AUTOGEN: {
                "patterns": [InteractionPattern.CONSULTATIVE, InteractionPattern.CONVERSATIONAL],
                "strengths": ["natural_conversation", "context_awareness", "flexible_responses"]
            },
            FrameworkCapability.LANGGRAPH: {
                "patterns": [InteractionPattern.SEQUENTIAL, InteractionPattern.PARALLEL, InteractionPattern.VALIDATION],
                "strengths": ["workflow_control", "state_management", "conditional_routing"]
            }
        }
    
    def _get_orchestrator(self, framework: FrameworkCapability):
        """Lazy initialization of orchestrators to avoid circular imports."""
        if framework == FrameworkCapability.CREWAI:
            if self.crewai_orchestrator is None:
                from orchestrators.reasoning_orchestrator import ReasoningOrchestrator
                self.crewai_orchestrator = ReasoningOrchestrator()
            return self.crewai_orchestrator
        elif framework == FrameworkCapability.AUTOGEN:
            if self.autogen_orchestrator is None:
                from orchestrators.reasoning_orchestrator import ReasoningOrchestrator
                self.autogen_orchestrator = ReasoningOrchestrator()
            return self.autogen_orchestrator
        elif framework == FrameworkCapability.LANGGRAPH:
            if self.langgraph_orchestrator is None:
                from orchestrators.expert_orchestrator_langgraph import ExpertSystemOrchestratorLangGraph
                self.langgraph_orchestrator = ExpertSystemOrchestratorLangGraph()
            return self.langgraph_orchestrator
        return None

    def analyze_query_complexity(self, parsed_intent: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze query to determine complexity and interaction needs"""
        # CRITICAL DEBUG: Log what we received
        print(f"[DEBUG] analyze_query_complexity received type: {type(parsed_intent)}")
        print(f"[DEBUG] analyze_query_complexity received value: {parsed_intent}")
        
        # Safety check: ensure parsed_intent is a dict
        if not isinstance(parsed_intent, dict):
            print(f"[DEBUG] NOT A DICT! Converting to dict...")
            logger.warning(f"analyze_query_complexity received {type(parsed_intent)}, expected dict. Using defaults.")
            parsed_intent = {
                "intent": "general",
                "sub_intents": parsed_intent if isinstance(parsed_intent, list) else [],
                "reasoning_style": "default",
                "metadata_flags": {}
            }
            print(f"[DEBUG] After conversion: {parsed_intent}")
        
        # Handle metadata_flags - it can be a dict or a list
        metadata_flags = parsed_intent.get("metadata_flags", {})
        if isinstance(metadata_flags, list):
            metadata_flags = {}  # Convert list to empty dict
        
        complexity_indicators = {
            "multi_intent": len(parsed_intent.get("sub_intents", [])) > 2,
            "multi_step": "step" in str(parsed_intent.get("reasoning_style", "")).lower(),
            "cross_domain": len(set(parsed_intent.get("sub_intents", []))) > 1,
            "ambiguous": metadata_flags.get("ambiguity", False),
            "urgent": metadata_flags.get("urgency", False),
            "validation_needed": any(tag in ["code", "model", "analysis"] for tag in parsed_intent.get("sub_intents", []))
        }
        
        complexity_score = sum(complexity_indicators.values()) / len(complexity_indicators)
        
        return {
            "score": complexity_score,
            "indicators": complexity_indicators,
            "needs_validation": complexity_indicators["validation_needed"],
            "needs_collaboration": complexity_indicators["multi_intent"] or complexity_indicators["cross_domain"]
        }

    def select_optimal_framework(self, interaction_pattern: InteractionPattern) -> str:
        """Select best framework for given interaction pattern"""
        for framework, capabilities in self.framework_capabilities.items():
            if interaction_pattern in capabilities["patterns"]:
                return framework.value
        
        # Default fallback
        return FrameworkCapability.CREWAI.value

    def determine_interaction_pattern(self, complexity_analysis: Dict[str, Any], 
                                   selected_agents: List[AgentSelection]) -> InteractionPattern:
        """Dynamically determine best interaction pattern based on query analysis"""
        
        if complexity_analysis["needs_validation"] and len(selected_agents) >= 2:
            return InteractionPattern.VALIDATION
        
        if complexity_analysis["needs_collaboration"] and len(selected_agents) > 2:
            return InteractionPattern.COLLABORATIVE
            
        if len(selected_agents) == 1:
            return InteractionPattern.SEQUENTIAL
            
        if any("timeline" in agent.capabilities for agent in selected_agents):
            return InteractionPattern.HIERARCHICAL
            
        if any("conversational" in agent.capabilities for agent in selected_agents):
            return InteractionPattern.CONSULTATIVE
            
        # Default to sequential for simplicity
        return InteractionPattern.SEQUENTIAL

    def select_agents_dynamically(self, parsed_intent: Dict[str, Any]) -> List[AgentSelection]:
        """Dynamically select agents based on query analysis"""
        # Safety check: ensure parsed_intent is a dict
        if not isinstance(parsed_intent, dict):
            logger.warning(f"select_agents_dynamically received {type(parsed_intent)}, expected dict. Using defaults.")
            parsed_intent = {
                "intent": "general",
                "sub_intents": parsed_intent if isinstance(parsed_intent, list) else [],
                "reasoning_style": "default",
                "metadata_flags": {}
            }
        
        subintents = parsed_intent.get("sub_intents", [])
        reasoning_style = parsed_intent.get("reasoning_style", "")
        
        selected_agents = []
        used_capabilities = set()
        
        # For each subintent, find best matching agents
        for subintent in subintents:
            matches = find_agents_by_subintent(
                subintent=subintent,
                reasoning_style=reasoning_style,
                min_score_threshold=0.3
            )
            
            for match in matches[:2]:  # Top 2 matches per subintent
                agent_name = match["agent"]
                score = match["score"]
                
                # Avoid duplicate agents
                if any(agent.name == agent_name for agent in selected_agents):
                    continue
                
                # Check if agent capabilities overlap significantly
                agent_caps = set(AGENT_CAPABILITY_REGISTRY[agent_name].get("capabilities", []))
                if len(agent_caps.intersection(used_capabilities)) > 2:
                    continue  # Skip if too much overlap
                
                # Select optimal framework for this agent
                framework = self._select_framework_for_agent(agent_name, reasoning_style)
                
                selected_agents.append(AgentSelection(
                    name=agent_name,
                    framework=framework,
                    confidence=score,
                    reasoning=f"Matched {subintent} with {match['explanation']}",
                    capabilities=agent_caps
                ))
                
                used_capabilities.update(agent_caps)
        
        # Ensure we have at least one agent
        if not selected_agents and subintents:
            # Fallback to best overall match
            fallback_match = find_agents_by_subintent(subintents[0], min_score_threshold=0.1)
            if fallback_match:
                agent_name = fallback_match[0]["agent"]
                selected_agents.append(AgentSelection(
                    name=agent_name,
                    framework=self._select_framework_for_agent(agent_name, reasoning_style),
                    confidence=fallback_match[0]["score"],
                    reasoning="Fallback selection",
                    capabilities=AGENT_CAPABILITY_REGISTRY[agent_name].get("capabilities", [])
                ))
        
        return selected_agents

    def _select_framework_for_agent(self, agent_name: str, reasoning_style: str) -> str:
        """Select optimal framework for a specific agent"""
        agent_metadata = AGENT_CAPABILITY_REGISTRY.get(agent_name, {})
        agent_reasoning_styles = agent_metadata.get("reasoning_styles", [])
        
        # Framework selection logic based on agent capabilities and reasoning style
        if "conversational" in agent_reasoning_styles or reasoning_style == "conversational":
            return FrameworkCapability.AUTOGEN.value
        elif "hierarchical" in agent_reasoning_styles or "planning" in agent_metadata.get("capabilities", []):
            return FrameworkCapability.CREWAI.value
        elif "stepwise" in agent_reasoning_styles or reasoning_style == "multi-hop":
            return FrameworkCapability.LANGGRAPH.value
        else:
            # Default based on agent type
            if agent_name in ["multi_hop_reasoning", "error_diagnosis"]:
                return FrameworkCapability.LANGGRAPH.value
            elif agent_name in ["timeline_coach", "code_feedback"]:
                return FrameworkCapability.CREWAI.value
            else:
                return FrameworkCapability.AUTOGEN.value

    def _get_llm_config_for_agent(self, agent_name: str) -> str:
        """Get the appropriate LLM configuration section for an agent"""
        # RAG-based retrieval agents use Gemini Flash
        if agent_name in ["competition_summary", "notebook_explainer", "discussion_helper"]:
            return "retrieval_agents"
        # Reasoning agents use DeepSeek
        elif agent_name in ["multi_hop_reasoning", "error_diagnosis", "code_feedback"]:
            return "reasoning_and_interaction"
        # Timeline and progress agents use Gemini Flash (retrieval-focused)
        elif agent_name in ["timeline_coach", "progress_monitor"]:
            return "retrieval_agents"
        else:
            return "default"

    def create_interaction_plan(self, query: str) -> InteractionPlan:
        """Create complete interaction plan for a query"""
        logger.info(f"Creating interaction plan for query: {query}")
        
        # 1. Parse user intent
        parsed_intent = parse_user_intent(query)
        
        # Safety check: ensure parsed_intent is a dict
        if not isinstance(parsed_intent, dict):
            logger.error(f"parse_user_intent returned {type(parsed_intent)}, expected dict. Wrapping in dict.")
            parsed_intent = {
                "intent": "general",
                "sub_intents": parsed_intent if isinstance(parsed_intent, list) else [],
                "reasoning_style": "default",
                "metadata_flags": {}
            }
        
        # 2. Analyze complexity
        complexity_analysis = self.analyze_query_complexity(parsed_intent)
        
        # 3. Select agents dynamically
        selected_agents = self.select_agents_dynamically(parsed_intent)
        
        # 4. Determine interaction pattern
        interaction_pattern = self.determine_interaction_pattern(complexity_analysis, selected_agents)
        
        # 5. Create execution order
        execution_order = self._create_execution_order(selected_agents, interaction_pattern)
        
        # 6. Estimate duration
        expected_duration = self._estimate_duration(len(selected_agents), interaction_pattern, complexity_analysis)
        
        plan = InteractionPlan(
            pattern=interaction_pattern,
            agents=selected_agents,
            execution_order=execution_order,
            expected_duration=expected_duration,
            complexity_score=complexity_analysis["score"]
        )
        
        logger.info(f"Created plan: {interaction_pattern.value} with {len(selected_agents)} agents")
        return plan

    def _create_execution_order(self, agents: List[AgentSelection], 
                              pattern: InteractionPattern) -> List[int]:
        """Create execution order based on interaction pattern"""
        if pattern == InteractionPattern.SEQUENTIAL:
            return list(range(len(agents)))
        elif pattern == InteractionPattern.PARALLEL:
            return [0] + list(range(1, len(agents)))  # First agent, then parallel
        elif pattern == InteractionPattern.HIERARCHICAL:
            # Find coordinator agent first
            coordinator_idx = next((i for i, agent in enumerate(agents) 
                                  if "planning" in agent.capabilities or "timeline" in agent.capabilities), 0)
            others = [i for i in range(len(agents)) if i != coordinator_idx]
            return [coordinator_idx] + others
        elif pattern == InteractionPattern.VALIDATION:
            # Producer first, then validator
            producer_idx = next((i for i, agent in enumerate(agents) 
                               if "code" in agent.capabilities or "model" in agent.capabilities), 0)
            validator_idx = next((i for i, agent in enumerate(agents) 
                                if i != producer_idx and "error" in agent.capabilities), 1)
            return [producer_idx, validator_idx]
        else:
            return list(range(len(agents)))

    def _estimate_duration(self, num_agents: int, pattern: InteractionPattern, 
                          complexity: Dict[str, Any]) -> str:
        """Estimate execution duration"""
        base_time = num_agents * 30  # 30 seconds per agent
        
        if pattern == InteractionPattern.PARALLEL:
            base_time *= 0.7  # Parallel is faster
        elif pattern == InteractionPattern.COLLABORATIVE:
            base_time *= 1.5  # Collaboration takes longer
        
        if complexity["score"] > 0.7:
            base_time *= 1.5  # Complex queries take longer
            
        if base_time < 60:
            return f"{base_time}s"
        else:
            return f"{base_time//60}m {base_time%60}s"

    def execute_plan(self, plan: InteractionPlan, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute the interaction plan"""
        logger.info(f"Executing {plan.pattern.value} plan with {len(plan.agents)} agents")
        
        context = context or {}
        results = []
        shared_context = context.copy()
        
        # Execute based on interaction pattern
        if plan.pattern == InteractionPattern.SEQUENTIAL:
            results = self._execute_sequential(plan, query, shared_context)
        elif plan.pattern == InteractionPattern.PARALLEL:
            results = self._execute_parallel(plan, query, shared_context)
        elif plan.pattern == InteractionPattern.HIERARCHICAL:
            results = self._execute_hierarchical(plan, query, shared_context)
        elif plan.pattern == InteractionPattern.VALIDATION:
            results = self._execute_validation(plan, query, shared_context)
        elif plan.pattern == InteractionPattern.COLLABORATIVE:
            results = self._execute_collaborative(plan, query, shared_context)
        else:
            results = self._execute_sequential(plan, query, shared_context)
        
        return {
            "query": query,
            "plan": plan,
            "results": results,
            "execution_summary": {
                "pattern": plan.pattern.value,
                "agents_used": [agent.name for agent in plan.agents],
                "frameworks_used": list(set(agent.framework for agent in plan.agents)),
                "total_agents": len(plan.agents)
            }
        }

    def _execute_sequential(self, plan: InteractionPlan, query: str, context: Dict) -> List[Dict]:
        """Execute agents in sequence, passing context forward"""
        results = []
        current_context = context.copy()
        
        for idx in plan.execution_order:
            agent_selection = plan.agents[idx]
            result = self._execute_single_agent(agent_selection, query, current_context)
            results.append(result)
            current_context.update(result.get("updated_context", {}))
            
        return results

    def _execute_parallel(self, plan: InteractionPlan, query: str, context: Dict) -> List[Dict]:
        """Execute agents in parallel where possible"""
        # For now, implement as sequential but with shared context
        # In production, this would use asyncio or threading
        return self._execute_sequential(plan, query, context)

    def _execute_hierarchical(self, plan: InteractionPlan, query: str, context: Dict) -> List[Dict]:
        """Execute with coordinator agent first, then others"""
        results = []
        coordinator_idx = plan.execution_order[0]
        coordinator = plan.agents[coordinator_idx]
        
        # Coordinator runs first
        coordinator_result = self._execute_single_agent(coordinator, query, context)
        results.append(coordinator_result)
        
        # Other agents run with coordinator's output as context
        enhanced_context = context.copy()
        enhanced_context.update(coordinator_result.get("updated_context", {}))
        
        for idx in plan.execution_order[1:]:
            agent_selection = plan.agents[idx]
            result = self._execute_single_agent(agent_selection, query, enhanced_context)
            results.append(result)
            
        return results

    def _execute_validation(self, plan: InteractionPlan, query: str, context: Dict) -> List[Dict]:
        """Execute producer agent, then validator"""
        results = []
        producer_idx, validator_idx = plan.execution_order[0], plan.execution_order[1]
        
        # Producer creates content
        producer = plan.agents[producer_idx]
        producer_result = self._execute_single_agent(producer, query, context)
        results.append(producer_result)
        
        # Validator reviews and improves
        validator = plan.agents[validator_idx]
        validation_query = f"Please review and validate this output: {producer_result.get('response', '')}"
        validator_result = self._execute_single_agent(validator, validation_query, context)
        results.append(validator_result)
        
        return results

    def _execute_collaborative(self, plan: InteractionPlan, query: str, context: Dict) -> List[Dict]:
        """Execute agents collaboratively (simplified version)"""
        # For now, implement as sequential with enhanced context sharing
        # In production, this would involve iterative collaboration
        return self._execute_sequential(plan, query, context)

    def _execute_single_agent(self, agent_selection: AgentSelection, query: str, context: Dict) -> Dict:
        """Execute a single agent using its selected framework"""
        try:
            # Get agent instance
            agent_instance = get_agent(agent_selection.name, mode="default")
            
            # Execute based on framework
            if agent_selection.framework == FrameworkCapability.CREWAI.value:
                result = self.crewai_orchestrator.run_single_agent(
                    agent_selection.name, query, context
                )
            elif agent_selection.framework == FrameworkCapability.AUTOGEN.value:
                result = self.autogen_orchestrator.run_single_agent(
                    agent_selection.name, query, context
                )
            elif agent_selection.framework == FrameworkCapability.LANGGRAPH.value:
                result = self.langgraph_orchestrator.run_single_agent(
                    agent_selection.name, query, context
                )
            else:
                # Fallback to direct agent execution
                result = agent_instance.run(query, context)
            
            return {
                "agent_name": agent_selection.name,
                "framework": agent_selection.framework,
                "confidence": agent_selection.confidence,
                "result": result,
                "updated_context": result.get("updated_context", context)
            }
            
        except Exception as e:
            logger.error(f"Failed to execute agent {agent_selection.name}: {e}")
            return {
                "agent_name": agent_selection.name,
                "framework": agent_selection.framework,
                "error": str(e),
                "updated_context": context
            }

    def run(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Main entry point - creates and executes dynamic interaction plan"""
        plan = self.create_interaction_plan(query)
        return self.execute_plan(plan, query, context)
