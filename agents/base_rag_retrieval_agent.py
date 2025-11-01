# agents/base/base_rag_retrieval_agent.py

from typing import Dict, Any, List
from RAG_pipeline_chromadb.rag_pipeline import ChromaDBRAGPipeline  # import your working pipeline
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain

class BaseRAGRetrievalAgent:
    def __init__(self, agent_name: str, prompt_template: str, section: str = "code", retriever=None, llm=None):
        self.name = agent_name
        self.section = section
        self.retriever = retriever or ChromaDBRAGPipeline()
        self.llm = llm
        self.chain = self._build_chain(prompt_template) if llm else None

    def _build_chain(self, template: str) -> LLMChain:
        prompt = PromptTemplate.from_template(template)
        return LLMChain(llm=self.llm, prompt=prompt)

    def fetch_sections(self, query: Dict[str, Any], top_k: int = 5) -> List:
        cleaned_query = query.get("cleaned_query", "")
        metadata = query.get("metadata", {})
        competition_slug = metadata.get("competition_slug") or metadata.get("competition")
        
        # Use ChromaDB's retrieve_and_rerank method with competition filter
        docs = self.retriever.rerank_document_store(
            query=cleaned_query,
            top_k_retrieval=20,
            top_k_final=top_k,
            competition_slug=competition_slug  # CRITICAL: Filter by current competition!
        )
        return docs

    def extract_relevant_sections(self, chunks: List, query: Dict[str, Any]) -> List:
        question = query.get("cleaned_query", "")
        # ChromaDB returns dicts with 'content' key
        return [chunk.get("content", "") for chunk in chunks if any(word in chunk.get("content", "").lower() for word in question.split())][:5]

    def explain_sections(self, sections: List, metadata: Dict[str, Any]) -> str:
        explanations = []
        for section_content in sections:
            prompt_input = {
                "section_content": section_content,
                "user_level": metadata.get("user_level", "beginner"),
                "tone": metadata.get("tone", "friendly"),
                "competition": metadata.get("competition", "Unknown Competition")
            }
            explanation = self.chain.run(prompt_input)
            explanations.append(explanation)
        return "\n\n".join(explanations)
    
    def summarize_sections(self, sections: List[Dict[str, str]], metadata: Dict[str, Any]) -> str:
        """
        Consolidate multiple sections into one explanation to avoid repetition.
        Combines all section content first, then generates a single unified response.
        """
        if not self.chain:
            return "Agent not configured with LLM"
        
        # Combine all section content
        combined_content = "\n\n---\n\n".join([
            section.get("content", "") 
            for section in sections 
            if section.get("content")
        ])
        
        # If no content, return empty
        if not combined_content.strip():
            return "No relevant information found"
        
        # Generate a single consolidated explanation
        prompt_input = {
            "section_content": combined_content,
            "user_level": metadata.get("user_level", "beginner"),
            "tone": metadata.get("tone", "friendly"),
            "competition": metadata.get("competition", "Unknown Competition"),
            "metric": metadata.get("metric", ""),  # ✅ FIX: Pass metric for evaluation prompt
            "details": metadata.get("details", "")  # ✅ FIX: Pass details for evaluation prompt
        }
        
        return self.chain.run(prompt_input)

    def run(self, structured_query: Dict[str, Any]) -> Dict[str, Any]:
        try:
            metadata = structured_query.get("metadata", {})
            chunks = self.fetch_sections(structured_query)
            
            # CRITICAL FIX: Use summarize_sections to avoid repetition!
            # This combines all chunks into ONE unified response instead of separate responses per chunk
            final_response = self.summarize_sections(chunks, metadata)
            
            return {"agent_name": self.name, "response": final_response}
        except Exception as e:
            return {"agent_name": self.name, "response": f"{self.name} failed: {str(e)}"}
