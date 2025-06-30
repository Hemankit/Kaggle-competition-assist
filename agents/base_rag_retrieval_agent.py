# agents/base/base_rag_retrieval_agent.py

from typing import Dict, Any, List
from RAG_pipeline.rag_pipeline import HaystackRAGPipeline  # import your pipeline
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain

class BaseRAGRetrievalAgent:
    def __init__(self, agent_name: str, prompt_template: str, section: str = "code", retriever=None, llm=None):
        self.name = agent_name
        self.section = section
        self.retriever = retriever or HaystackRAGPipeline()
        self.llm = llm
        self.chain = self._build_chain(prompt_template)

    def _build_chain(self, template: str) -> LLMChain:
        prompt = PromptTemplate.from_template(template)
        return LLMChain(llm=self.llm, prompt=prompt)

    def fetch_sections(self, query: Dict[str, Any], top_k: int = 5) -> List:
        cleaned_query = query.get("cleaned_query", "")
        docs = self.retriever.retriever.retrieve(
            query=cleaned_query,
            top_k=20,
            filters={"section": self.section}
        )
        reranked = self.retriever.reranker.predict(query=cleaned_query, documents=docs)
        return reranked[:top_k]

    def extract_relevant_sections(self, chunks: List, query: Dict[str, Any]) -> List:
        question = query.get("cleaned_query", "")
        return [chunk.content for chunk in chunks if any(word in chunk.content.lower() for word in question.split())][:5]

    def explain_sections(self, sections: List, metadata: Dict[str, Any]) -> str:
        explanations = []
        for section_content in sections:
            prompt_input = {
                "section_content": section_content,
                "user_level": metadata.get("user_level", "beginner"),
                "tone": metadata.get("tone", "friendly")
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
