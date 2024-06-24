import argparse
from langchain_community.document_loaders.pdf import PyPDFDirectoryLoader


def main():

    arg_parser = argparse.ArgumentParser();
    arg_parser.add_argument("-p", required=True, help="PDF folder")
    args = arg_parser.parse_args();

    print(args.p)

    doc_loader = PyPDFDirectoryLoader(args.p)
    docs = doc_loader.load()
    

if __name__ == "__main__":
    main()