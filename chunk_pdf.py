import argparse
from langchain_community.document_loaders.pdf import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import fitz
import os
from tqdm import tqdm

def main():

    arg_parser = argparse.ArgumentParser();
    arg_parser.add_argument("-p", required=True, help="PDF folder")
    args = arg_parser.parse_args();

    print(args.p)

    # doc_loader = PyPDFDirectoryLoader(args.p)
    # docs = doc_loader.load()
    
    # chunkifier = RecursiveCharacterTextSplitter(
    #     chunk_size=800,
    #     chunk_overlap=80,
    #     length_function=len,
    #     is_separator_regex=False
    # )

    # chunks = chunkifier.split_documents(docs)
    # print("Chunks: ", len(chunks))

    for path in os.listdir(args.p):        
        if ".pdf" in path:
            print(path)
            doc = fitz.Document(os.path.join(args.p, path))

            for page_num in tqdm(range(len(doc)), desc="pages"):
                for img in doc.get_page_images(page_num):
                    xref =img[0]
                    image = doc.extract_image(xref)
                    pix = fitz.Pixmap(doc, xref)
                    pix.save(os.path.join(args.p, "images/" "%s_p%s-%s.png" % (path[:-4], page_num, xref)))

if __name__ == "__main__":
    main()