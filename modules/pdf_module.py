"""Module to parse PDF documents."""

# pylint: disable=W0613
# pylint: disable=C0116
# pylint: disable=C0301

import os
import argparse
import re

from langchain_community.document_loaders.pdf import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import fitz
from tqdm import tqdm

def main():

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-p", required=True, help="PDF folder")
    args = arg_parser.parse_args()

    print(args.p)

    #extract_text_chunks(args.p)
    extract_images_and_captions(args.p)

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

def extract_images_and_captions(folder_path):
    for path in os.listdir(folder_path):
        if path.endswith(".pdf"):
            print(path)
            doc = fitz.Document(os.path.join(folder_path, path))

            doc_images = []
            doc_captions = []

            for page_num in tqdm(range(len(doc)), desc="pages"):
                page = doc.load_page(page_num)

                page_images = extract_images(page, folder_path, path, doc)
                page_captions = extract_captions(page, page_images, folder_path, path)

                audit_log(len(page_captions), len(page_images), folder_path, page_num)

                doc_images.append(page_images)
                doc_captions.append(page_captions)

def extract_images(page, folder_path, path, doc):

    page_images =  page.get_images(full=True)
    images_with_bbox = []

    page_num = page.number

    for img in page_images:
        #xref =img[0]
        #pix = fitz.Pixmap(doc, xref)
        #pix.save(os.path.join(folder_path, "images/" "%s_p%s-%s.png" % (path[:-4], page_num, xref)))

        img_bbox = page.get_image_bbox(img)
        images_with_bbox.append(img + (img_bbox,page_num,))

    return images_with_bbox

def extract_captions(page, images, folder_path, path):

    pattern = re.compile(r'(?:\n|^)(Fig\.\s\d+.*?)(?:\n|$)', re.IGNORECASE)

    #Resolve mismatched captions such as when they reside on different pages

    page_captions= []

    page_num = page.number
    #caption_num = 0
    text_blocks = page.get_text("blocks")

    for _, block in enumerate(text_blocks):
        _, y0, _, _, text, _, _, = block

        for _ in pattern.findall(text):
            # img_xref = 0
            # #temporary guard check
            # if len(images) > caption_num:
            #     img_xref = images[caption_num][0]

            # caption_path = os.path.join(folder_path, "images/" "%s_p%s-%s.txt" % (path[:-4], page_num, img_xref))
            # with open(caption_path, "w") as file:
            #     caption = match.strip()
            #     file.write(caption)
            # caption_num += 1

            page_captions.append((text,y0,page_num))

    return page_captions

def audit_log(caption_num, img_num, folder_path, page_num):
    """Function logging mismatch between images and captions."""

    if caption_num != img_num:
        caption_path = os.path.join(folder_path, "images/", "caption_audit.txt")
        with open(caption_path, "a", encoding="utf-8") as file:
            file.write(f"Page{page_num}:\t{img_num} Images,\t{caption_num} Captions\n")

if __name__ == "__main__":
    main()