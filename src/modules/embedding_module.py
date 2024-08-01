"""Module to generate embeddings."""

# pylint: disable=W0613
# pylint: disable=C0116
# pylint: disable=C0301
# pylint: disable=C0115
# pylint: disable=W0511
# pylint: disable=R0903

from langchain_community.embeddings import OllamaEmbeddings


class Embeddings:

    def __init__(self, model: str) -> None:
        self.model = model

    def embedding_function(self):
        embeddings = OllamaEmbeddings(model="llama3:8b")
        return embeddings
