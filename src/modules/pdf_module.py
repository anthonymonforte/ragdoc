"""Module to parse PDF documents."""

# pylint: disable=W0613
# pylint: disable=C0116
# pylint: disable=C0301
# pylint: disable=C0115
# pylint: disable=W0511

import os
import re

from typing import List
from dataclasses import dataclass
from langchain_community.document_loaders.pdf import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


import fitz
from tqdm import tqdm

@dataclass
class ChunkConfig:
    chunk_size: int
    chunk_overlap: int

@dataclass
class Config:
    folder_path: str
    caption_above_img: bool
    perform_audit: bool
    caption_regex: str
    image_part_offset_threshold: float

@dataclass
class Caption:
    caption_text: str
    caption_y0: int
    caption_page: int

@dataclass
class ImagePart:
    xref: any
    bbox: any
    dpi: any

@dataclass
class PdfImage:
    image_parts: List[ImagePart]
    image_bbox: any
    image_page: int
    caption: Caption
    filepath: str = ""
    id: str = ""

    def generate_id(self, source_doc_name):
        return f"{source_doc_name}:{self.image_page}:{self.image_parts[0].xref}"

class PdfDocProcessor:

    def __init__(self, config) -> None:
        self.config = config

    def extract_text_chunks(self, folder_path) -> list[fitz.Document]:
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
        return chunks

    def extract_images_and_captions_from_folder(self):
        for path in os.listdir(self.config.folder_path):
            if path.endswith(".pdf"):
                print(path)
                doc_path = os.path.join(self.config.folder_path, path)
                self.extract_images_and_captions_from_doc(doc_path)

    def extract_images_and_captions_from_doc(self, doc_path: str):
        doc = fitz.Document(doc_path)

        doc_images = []
        unresolved_captions = []
        unresolved_captions.clear()

        page_numbers = tqdm(range(len(doc)), desc="pages")

        for page_num in page_numbers:
            page = doc.load_page(page_num)

            page_images = self.extract_images(page)
            self.write_images(doc, page, page_images)

            page_captions = self.extract_captions(page)

            if len(page_images) > 0 or len(page_captions) > 0:
                self.stitch_images_and_captions(page_images, page_captions, doc_images, unresolved_captions)

        if self.config.perform_audit:
            self.audit_log(doc, doc_images, os.path.dirname(doc_path))

        return doc_images

    def stitch_images_and_captions(self, page_images, page_captions, doc_images, unresolved_captions):
        page_images_and_captions = [{'y_pos': img.image_bbox[3], 'page': img.image_page, 'type': 'image', 'image': img} for img in page_images] + [{'y_pos': caption.caption_y0, 'page': caption.caption_page, 'caption': caption, 'type': 'caption'} for caption in page_captions] + unresolved_captions

        if not self.config.caption_above_img:
            sorted_by_y_pos = sorted(page_images_and_captions, key=lambda x: (-x['page'], x['y_pos']), reverse=self.config.caption_above_img)
        else:
            sorted_by_y_pos = sorted(page_images_and_captions, key=lambda x: (x['page'], x['y_pos']), reverse=self.config.caption_above_img)

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

        if self.config.caption_above_img is True:
            wip_list.reverse()

        doc_images.extend(wip_list)
        unresolved_captions.extend(new_unresolved_captions)

    def extract_images(self, page):

        page_images = page.get_image_info(hashes=True, xrefs=True)

        pdf_images: PdfImage = []

        page_num = page.number

        for img in page_images:
            dpi=max( [img['xres'], img['yres'] ])
            pdf_images.append(PdfImage(image_bbox = img['bbox'],
                                        image_page = page_num,
                                        image_parts = [ImagePart(xref=img['xref'], bbox=img['bbox'],dpi=dpi)],
                                        caption = None))

        return self.combine_images(pdf_images)

    # encasulate into more common class
    def write_images(self, doc: fitz.Document, page: fitz.Page, images: List[PdfImage]):
        for img in images:

            final_image: fitz.Pixmap = None
            if len(img.image_parts) == 1:
                final_image = fitz.Pixmap(doc, img.image_parts[0].xref)
            elif len(img.image_parts) > 1:

                x0 = min(ip.bbox[0] for ip in img.image_parts)
                y0 = min(ip.bbox[1] for ip in img.image_parts)
                x1 = max(ip.bbox[2] for ip in img.image_parts)
                y1 = max(ip.bbox[3] for ip in img.image_parts)
                dpi = max(ip.dpi for ip in img.image_parts)

                # specify colorspace?
                final_image = page.get_pixmap(dpi=dpi, clip=fitz.Rect(x0,y0,x1,y1))
            else:
                return

            filepath = os.path.join(self.config.folder_path, "images/", f"p{page.number}_x{img.image_parts[0].xref}.png")
            final_image.save(filepath)
            img.filepath = filepath


    def combine_images(self, images: List[PdfImage]):
        if len(images) < 2:
            return images

        sorted_by_y0 = sorted(images, key=lambda x: (x.image_bbox[1]))

        final_list = []
        for img in sorted_by_y0:
            if len(final_list) < 1 or ((final_list[-1].image_parts[-1].bbox[3] + self.config.image_part_offset_threshold) < img.image_bbox[1]):
                final_list.append(img)
            else:
                final_list[-1].image_parts.append(img.image_parts[-1])

        return final_list

    def extract_captions(self, page):

        pattern = re.compile(self.config.caption_regex, re.IGNORECASE)

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

    def audit_log(self, doc, doc_images, folder_path):
        """Function logging mismatch between images and captions."""
        caption_path = os.path.join(folder_path, "images/", "caption_audit.txt")
        log_path = os.path.join(folder_path, "images/", "log.txt")

        img_num = 1
        for doc_image in doc_images:
            if doc_image.caption is None:
                with open(caption_path, "a", encoding="utf-8") as file:
                    file.write(f"Page {doc_image.image_page}:\tImage {img_num}\n")

                xref = doc_image.image_parts[-1].xref
                pix = fitz.Pixmap(doc, xref)
                pix.save(os.path.join(folder_path, "images/", f"p{xref}-{doc_image.image_page}.png"))

            with open(log_path, "a", encoding="utf-8") as log:
                caption_text = ''
                if doc_image.caption is not None:
                    caption_text = doc_image.caption.caption_text
                log.write(f"Page {doc_image.image_page}:\tImage {img_num}\t{caption_text}\n")

            img_num += 1
