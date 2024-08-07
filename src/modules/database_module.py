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
        #refrenced from: https://github.com/pixegami/rag-tutorial-v2/blob/main/populate_database.py

        db = Chroma(
            persist_directory=self.db_path, embedding_function=embedding_function
        )

        chunks_with_ids = self.generate_chunk_ids(chunks)

        # Add or Update the documents.
        existing_items = db.get(include=[])  # IDs are always included by default
        existing_ids = set(existing_items["ids"])
        print(f"Number of existing documents in DB: {len(existing_ids)}")

        # Only add documents that don't exist in the DB.
        new_chunks = []
        for chunk in chunks_with_ids:
            if chunk.metadata["id"] not in existing_ids:
                new_chunks.append(chunk)

        if len(new_chunks) > 0:
            print(f"👉 Adding new documents: {len(new_chunks)}")
            new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
            db.add_documents(new_chunks, ids=new_chunk_ids)            
        else:
            print("✅ No new documents to add")        

    def generate_chunk_ids(self, chunks: list[Document]) -> list[Document]:
        #refrenced from: https://github.com/pixegami/rag-tutorial-v2/blob/main/populate_database.py

        last_page_id = None
        current_chunk_index = 0

        for chunk in chunks:
            source = chunk.metadata.get("source")
            page = chunk.metadata.get("page")
            current_page_id = f"{source}:{page}"

            if current_page_id == last_page_id:
                current_chunk_index += 1
            else:
                current_chunk_index = 0

            chunk_id = f"{current_page_id}:{current_chunk_index}"
            last_page_id = current_page_id

            chunk.metadata["id"] = chunk_id

        return chunks
