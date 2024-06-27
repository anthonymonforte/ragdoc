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
            fig_captions = []

            for page_num in tqdm(range(len(doc)), desc="pages"):
                img_num = 0
                img_xrefs = []

                for img in doc.get_page_images(page_num):
                    xref =img[0]
                    #image = doc.extract_image(xref)
                    pix = fitz.Pixmap(doc, xref)
                    pix.save(os.path.join(args.p, "images/" "%s_p%s-%s.png" % (path[:-4], page_num, xref)))
                    img_num += 1
                    img_xrefs.append(xref)

                if img_num > 0:
                    # Get captions
                    pattern = re.compile(r'\n(Fig\.\s\d+.*?)\n', re.IGNORECASE)

                    page = doc.load_page(page_num)
                    text = page.get_text("text")
                    #text_blocks = text.split('\n\n')
                    
                    #for block in text_blocks:
                    for match in pattern.findall(text):
                        caption_num = 0                        
                        #if pattern.search(block):                            
                        path = os.path.join(args.p, "images/" "%s_p%s-%s.txt" % (path[:-4], page_num, img_xrefs[caption_num]))
                        with open(path, "w") as file:
                            caption =match.strip()
                            file.write(caption)
                        caption_num += 1

if __name__ == "__main__":
    main()