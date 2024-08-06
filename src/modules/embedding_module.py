"""Module to generate embeddings."""

# pylint: disable=W0613
# pylint: disable=C0116
# pylint: disable=C0301
# pylint: disable=C0115
# pylint: disable=W0511
# pylint: disable=R0903

from langchain_community.embeddings import OllamaEmbeddings

class Embeddings:

    def __init__(self, model: str, version: str, url: str) -> None:
        self.model = model
        self.version = version
        self.url = url

    def get_embedding_function(self):
        embedding_func = OllamaEmbeddings(base_url = self.url, model = f"{self.model}:{self.version}")
        return embedding_func
