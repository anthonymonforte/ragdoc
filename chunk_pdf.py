import argparse
from langchain_community.document_loaders.pdf import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

def main():

    arg_parser = argparse.ArgumentParser();
    arg_parser.add_argument("-p", required=True, help="PDF folder")
    args = arg_parser.parse_args();

    print(args.p)

    doc_loader = PyPDFDirectoryLoader(args.p)
    docs = doc_loader.load()
    
    chunkifier = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=80,
        length_function=len,
        is_separator_regex=False
    )

    chunks = chunkifier.split_documents(docs)
    print("Chunks: ", len(chunks))

if __name__ == "__main__":
    main()