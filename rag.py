"""RAG pipeline: chunk profile content, embed, and retrieve relevant passages."""

import os
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

_ROOT = Path(__file__).resolve().parent


class ProfileRAG:
    """Vector store over summary and resume; retrieves relevant chunks for a query."""

    def __init__(
        self,
        summary_path: str,
        resume_pdf: str,
        chunk_size: int = 600,
        chunk_overlap: int = 100,
    ):
        self.summary_path = str(_ROOT / summary_path)
        self.resume_pdf = str(_ROOT / resume_pdf)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        if not os.path.isfile(self.resume_pdf):
            raise FileNotFoundError(f"Resume PDF not found at {self.resume_pdf}.")
        if not os.path.isfile(self.summary_path):
            raise FileNotFoundError(f"Summary file not found at {self.summary_path}.")

        self._vectorstore = self._build_index()

    def _build_index(self):
        documents = []

        loader = TextLoader(self.summary_path, encoding="utf-8")
        docs = loader.load()
        for d in docs:
            d.metadata["source"] = "summary"
        documents.extend(docs)

        loader = PyPDFLoader(self.resume_pdf)
        docs = loader.load()
        for d in docs:
            d.metadata["source"] = "resume"
        documents.extend(docs)

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""],
        )
        splits = splitter.split_documents(documents)

        persist_dir = _ROOT / ".chroma_profile"
        persist_dir.mkdir(exist_ok=True)
        return Chroma.from_documents(
            documents=splits,
            embedding=OpenAIEmbeddings(),
            persist_directory=str(persist_dir),
        )

    def search(self, query: str, k: int = 5) -> str:
        """Retrieve top-k relevant chunks and return as a single string."""
        docs = self._vectorstore.similarity_search(query, k=k)
        if not docs:
            return ""
        return "\n\n---\n\n".join(d.page_content for d in docs)
