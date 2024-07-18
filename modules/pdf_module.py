"""Module to parse PDF documents."""

# pylint: disable=W0613
# pylint: disable=C0116
# pylint: disable=C0301
# pylint: disable=C0115

import os
import argparse
import re

from dataclasses import dataclass
from langchain_community.document_loaders.pdf import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import fitz
from tqdm import tqdm

@dataclass
class ChunkConfig:
    chunk_size: int
    chunk_overlap: int

CAPTION_REGEX = r'(?:\n|^)(Fig\.\s\d+.*?)(?:\n|$)'
CAPTION_ABOVE_IMG = False

def main():

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-p", required=True, help="PDF folder")
    args = arg_parser.parse_args()

    print(args.p)

    #extract_text_chunks(args.p, ChunkConfig(chunk_size=800, chunk_overlap=80))
    extract_images_and_captions(args.p)

def extract_text_chunks(folder_path, config):
    doc_loader = PyPDFDirectoryLoader(folder_path)
    docs = doc_loader.load()
    chunkifier = RecursiveCharacterTextSplitter(
        config.chunk_size,
        config.chunk_overlap,
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
            #doc_captions = []

            for page_num in tqdm(range(len(doc)), desc="pages"):
                page = doc.load_page(page_num)

                page_images = extract_images(page, folder_path, path, doc)
                page_captions = extract_captions(page, page_images, folder_path, path)

                if len(page_images) > 0 and len(page_captions) > 0:
                    stitch_images_and_captions(page_num, page_images, page_captions, doc_images)

                audit_log(len(page_captions), len(page_images), folder_path, page_num)

                #doc_images.append(page_images)
                #doc_captions.append(page_captions)


@dataclass
class Caption:
    caption_text: str
    caption_y0: int
    caption_page: int

@dataclass
class PdfImage:
    image_xref: any
    image_y1: int
    image_page: int
    caption: Caption

def stitch_images_and_captions(page_num, page_images, page_captions, doc_images):
    page_images_and_captions = [{'y_pos': img.image_y1, 'type': 'image', 'image': img} for img in page_images] + [{'y_pos': caption.caption_y0, 'caption': caption, 'type': 'caption'} for caption in page_captions]

    sorted_by_y_pos = sorted(page_images_and_captions, key=lambda x: x['y_pos'], reverse=CAPTION_ABOVE_IMG)

    unresolved_captions = []

    for item in sorted_by_y_pos:
        if item['type'] == 'image':
            doc_images.append(item['image'])
        elif len(doc_images) > 0 and doc_images[-1].caption is None:
            doc_images[-1].caption = item['caption']
        else:
            unresolved_captions.append(item['caption']) # Properly resolve dangling captions

def extract_images(page, folder_path, path, doc):

    page_images =  page.get_images(full=True)
    pdf_images: PdfImage = []

    page_num = page.number

    for img in page_images:
        #xref =img[0]
        #pix = fitz.Pixmap(doc, xref)
        #pix.save(os.path.join(folder_path, "images/" "%s_p%s-%s.png" % (path[:-4], page_num, xref)))

        img_bbox = page.get_image_bbox(img)
        pdf_images.append(PdfImage(image_xref = img[0],
                                    image_y1 = img_bbox[3],
                                    image_page = page_num,
                                    caption = None))

    return pdf_images

def extract_captions(page, images, folder_path, path):

    pattern = re.compile(CAPTION_REGEX, re.IGNORECASE)

    #Resolve mismatched captions such as when they reside on different pages

    page_captions: Caption = []

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

            page_captions.append(Caption(caption_text = text,
                                         caption_y0 = y0,
                                         caption_page = page_num))

    return page_captions

def audit_log(caption_num, img_num, folder_path, page_num):
    """Function logging mismatch between images and captions."""

    if caption_num != img_num:
        caption_path = os.path.join(folder_path, "images/", "caption_audit.txt")
        with open(caption_path, "a", encoding="utf-8") as file:
            file.write(f"Page{page_num}:\t{img_num} Images,\t{caption_num} Captions\n")

if __name__ == "__main__":
    main()
