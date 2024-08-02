"""Module to generate embeddings."""

# pylint: disable=W0613
# pylint: disable=C0116
# pylint: disable=C0301
# pylint: disable=C0115
# pylint: disable=W0511
# pylint: disable=R0903

from langchain_community.embeddings import OllamaEmbeddings


class Embeddings:

    def __init__(self, model: str, version: str) -> None:
        self.model = model
        self.version = version

    def get_embedding(self):
        match self.model:
            case "llama3":
                return self.ollama_embedding_function()
        return None

    def ollama_embedding_function(self):
        embeddings = OllamaEmbeddings(model=f"{self.model}:{self.version}") #e.g. llama3:8b
        return embeddings
