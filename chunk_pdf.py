import argparse
from langchain_community.document_loaders.pdf import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import fitz
import os
from tqdm import tqdm
import re

def main():

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-p", required=True, help="PDF folder")
    args = arg_parser.parse_args()

    print(args.p)   

    #extract_text_chunks(args.p)
    extract_images(args.p)

def extract_text_chunks(folder_path):
    doc_loader = PyPDFDirectoryLoader(folder_path)
    docs = doc_loader.load()
    chunkifier = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=80,
        length_function=len,
        is_separator_regex=False
    )

    chunks = chunkifier.split_documents(docs)
    print("Chunks: ", len(chunks))


def extract_images(folder_path):
    for path in os.listdir(folder_path):        
        if path.endswith(".pdf"):
            print(path)
            doc = fitz.Document(os.path.join(folder_path, path))
            
            for page_num in tqdm(range(len(doc)), desc="pages"):
                img_num = 0
                img_xrefs = []

                for img in doc.get_page_images(page_num):
                    xref =img[0]                    
                    pix = fitz.Pixmap(doc, xref)
                    pix.save(os.path.join(folder_path, "images/" "%s_p%s-%s.png" % (path[:-4], page_num, xref)))
                    img_num += 1
                    img_xrefs.append(xref)

                if img_num > 0:
                    # Get captions
                    pattern = re.compile(r'\n(Fig\.\s\d+.*?)\n', re.IGNORECASE)

                    page = doc.load_page(page_num)
                    text = page.get_text("text")
                    
                    for match in pattern.findall(text):
                        caption_num = 0                        
                        
                        caption_path = os.path.join(folder_path, "images/" "%s_p%s-%s.txt" % (path[:-4], page_num, img_xrefs[caption_num]))
                        with open(caption_path, "w") as file:
                            caption =match.strip()
                            file.write(caption)
                        caption_num += 1




if __name__ == "__main__":
    main()