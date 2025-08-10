from app.config.tools import SELECTED_RAG_PROVIDER, RAGProvider
from app.agents.rag.ragflow import RAGFlowProvider
from app.agents.rag.vikingdb_knowledge_base import VikingDBKnowledgeBaseProvider
from app.agents.rag.state import Retriever


def build_retriever() -> Retriever | None:
    if SELECTED_RAG_PROVIDER == RAGProvider.RAGFLOW.value:
        return RAGFlowProvider()
    elif SELECTED_RAG_PROVIDER == RAGProvider.VIKINGDB_KNOWLEDGE_BASE.value:
        return VikingDBKnowledgeBaseProvider()
    elif SELECTED_RAG_PROVIDER:
        raise ValueError(f"Unsupported RAG provider: {SELECTED_RAG_PROVIDER}")
    return None
