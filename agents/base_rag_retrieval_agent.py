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
        # Use ChromaDB's retrieve_and_rerank method
        docs = self.retriever.rerank_document_store(
            query=cleaned_query,
            top_k_retrieval=20,
            top_k_final=top_k
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

    def run(self, structured_query: Dict[str, Any]) -> Dict[str, Any]:
        try:
            metadata = structured_query.get("metadata", {})
            chunks = self.fetch_sections(structured_query)
            relevant_chunks = self.extract_relevant_sections(chunks, structured_query)
            final_response = self.explain_sections(relevant_chunks, metadata)
            return {"agent_name": self.name, "response": final_response}
        except Exception as e:
            return {"agent_name": self.name, "response": f"{self.name} failed: {str(e)}"}
