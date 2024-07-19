"""Module to parse PDF documents."""

# pylint: disable=W0613
# pylint: disable=C0116
# pylint: disable=C0301
# pylint: disable=C0115
# pylint: disable=W0511

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
            unresolved_captions = []
            unresolved_captions.clear()

            page_numbers = tqdm(range(len(doc)), desc="pages")
            for page_num in page_numbers:
                page = doc.load_page(page_num)

                page_images = extract_images(page, folder_path, path, doc)
                page_captions = extract_captions(page, page_images, folder_path, path)

                if len(page_images) > 0 or len(page_captions) > 0:
                    stitch_images_and_captions(page_images, page_captions, doc_images, unresolved_captions)

            audit_log(doc, doc_images, folder_path)

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

def stitch_images_and_captions(page_images, page_captions, doc_images, unresolved_captions):
    page_images_and_captions = [{'y_pos': img.image_y1, 'page': img.image_page, 'type': 'image', 'image': img} for img in page_images] + [{'y_pos': caption.caption_y0, 'page': caption.caption_page, 'caption': caption, 'type': 'caption'} for caption in page_captions] + unresolved_captions

    sorted_by_y_pos = sorted(page_images_and_captions, key=lambda x: (-x['page'], x['y_pos']), reverse=CAPTION_ABOVE_IMG)

    wip_list = []
    new_unresolved_captions = []

    for item in sorted_by_y_pos:
        if item['type'] == 'image':
            wip_list.append(item['image'])
        elif len(wip_list) > 0:
            if wip_list[-1].caption is None:
                wip_list[-1].caption = item['caption']
                unresolved_captions.clear()
            else:
                new_unresolved_captions.append(item)
        elif len(doc_images) > 0 and doc_images[-1].caption is None:
            doc_images[-1].caption = item['caption']
        else:
            new_unresolved_captions.append(item)

    if CAPTION_ABOVE_IMG is True:
        wip_list.reverse()

    doc_images.extend(wip_list)
    unresolved_captions.extend(new_unresolved_captions)

def extract_images(page, folder_path, path, doc):

    page_images =  page.get_images(full=True)
    pdf_images: PdfImage = []

    page_num = page.number

    #image_bboxes = []
    for img in page_images:
        #xref =img[0]
        #pix = fitz.Pixmap(doc, xref)
        #pix.save(os.path.join(folder_path, "images/" "%s_p%s-%s.png" % (path[:-4], page_num, xref)))

        img_bbox = page.get_image_bbox(img)
        #image_bboxes.append(img_bbox)   #TODO: use this information to combine images that have been broken apart
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

def audit_log(doc, doc_images, folder_path):
    """Function logging mismatch between images and captions."""
    caption_path = os.path.join(folder_path, "images/", "caption_audit.txt")
    log_path = os.path.join(folder_path, "images/", "log.txt")

    img_num = 1
    for doc_image in doc_images:
        if doc_image.caption is None:
            with open(caption_path, "a", encoding="utf-8") as file:
                file.write(f"Page {doc_image.image_page}:\tImage {img_num}\n")

            xref = doc_image.image_xref
            pix = fitz.Pixmap(doc, xref)
            pix.save(os.path.join(folder_path, "images/", f"p{xref}-{doc_image.image_page}.png"))

        with open(log_path, "a", encoding="utf-8") as log:
            caption_text = ''
            if doc_image.caption is not None:
                caption_text = doc_image.caption.caption_text
            log.write(f"Page {doc_image.image_page}:\tImage {img_num}\t{caption_text}\n")

        img_num += 1

if __name__ == "__main__":
    main()
