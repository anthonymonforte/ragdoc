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

                page = doc.load_page(page_num)

                # temporary exit condition
                # if page_num > 100:
                #     exit()
                
                #for img in doc.get_page_images(page_num):
                for img in page.get_images(full=True):
                    xref =img[0]                    
                    pix = fitz.Pixmap(doc, xref)
                    pix.save(os.path.join(folder_path, "images/" "%s_p%s-%s.png" % (path[:-4], page_num, xref)))
                    img_num += 1
                    img_xrefs.append(xref)

                    #img_bbox = page.get_image_bbox(img)

                pattern = re.compile(r'(?:\n|^)(Fig\.\s\d+.*?)(?:\n|$)', re.IGNORECASE)
                
                #TODO: Resolve mismatched captions such as when they reside on different pages

                caption_num = 0
                text_blocks = page.get_text("blocks")
                for idx, block in enumerate(text_blocks):
                    x0, y0, x1, y1, text, _, _, = block
                
                    for match in pattern.findall(text):
                        img_xref = 0
                        #temporary guard check
                        if len(img_xrefs) > caption_num:
                            img_xref = img_xrefs[caption_num]

                        caption_path = os.path.join(folder_path, "images/" "%s_p%s-%s.txt" % (path[:-4], page_num, img_xref))
                        with open(caption_path, "w") as file:
                            caption = match.strip()
                            file.write(caption)
                        caption_num += 1

                if caption_num != img_num:
                    caption_path = os.path.join(folder_path, "images/" "caption_audit.txt")
                    with open(caption_path, "a") as file:                        
                        file.write("Page%d:\t%d Images,\t%d Captions\n" % (page_num, img_num, caption_num))





if __name__ == "__main__":
    main()