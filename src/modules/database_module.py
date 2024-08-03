"""Module to store embeddings."""

# pylint: disable=W0613
# pylint: disable=C0116
# pylint: disable=C0301
# pylint: disable=C0115
# pylint: disable=W0511
# pylint: disable=R0903

from langchain.schema.document import Document
from langchain.vectorstores.chroma import Chroma

class EmbeddingDb:

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path

    def add_to_db(self, chunks: list[Document], embedding_function):

        db = Chroma(
            persist_directory=self.db_path, embedding_function=embedding_function
        )

        # generate ids for each chunk and store

        db.persist()
