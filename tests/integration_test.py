"""Integration Tests for PDF module."""

# pylint: disable=W0613
# pylint: disable=C0116
# pylint: disable=C0301
# pylint: disable=C0115
# pylint: disable=W0511

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import src.modules.pdf_module as pdf

def get_default_config():
    return pdf.Config(folder_path=os.path.dirname(__file__), caption_above_img=False, perform_audit=False, caption_regex=r'(?:\n|^)(Fig\.\s\d+.*?)(?:\n|$)', image_part_offset_threshold=.5)

def get_default_pdf_module():
    return pdf.PdfDocProcessor(get_default_config())

def test_extract_images_and_captions_from_pdf_1_image_bottom_caption_test():
    doc_images = get_default_pdf_module().extract_images_and_captions_from_doc(os.path.join(os.path.dirname(__file__), "test_assets/pdfs/pdf_1_image_bottom_caption_test.pdf"))

    assert len(doc_images) == 1
    pdf_image = doc_images[0]

    assert len(pdf_image.image_parts) == 1
    assert pdf_image.caption is not None
    assert pdf_image.caption.caption_text == "Fig. 1 This is a caption. \n"

def test_extract_images_and_captions_from_pdf_2_images_one_bottom_caption_and_page_break_test():
    doc_images = get_default_pdf_module().extract_images_and_captions_from_doc(os.path.join(os.path.dirname(__file__), "test_assets/pdfs/pdf_2_images_one_bottom_caption_and_page_break_test.pdf"))

    assert len(doc_images) == 2

    pdf_image = doc_images[0]
    assert len(pdf_image.image_parts) == 1
    assert pdf_image.caption is None

    pdf_image = doc_images[1]
    assert len(pdf_image.image_parts) == 1
    assert pdf_image.caption is not None
    assert pdf_image.caption.caption_text == "Fig. 1 This is a caption, on the next page. \n"

def test_extract_images_and_captions_from_pdf_2_images_top_captions_and_page_break():
    config = get_default_config()
    config.caption_above_img = True
    doc_images = pdf.PdfDocProcessor(config).extract_images_and_captions_from_doc(os.path.join(os.path.dirname(__file__), "test_assets/pdfs/pdf_2_images_top_captions_and_page_break.pdf"))

    assert len(doc_images) == 2

    pdf_image = doc_images[0]
    assert len(pdf_image.image_parts) == 1
    assert pdf_image.caption is not None
    assert pdf_image.caption.caption_text == "Fig. 1 This is a caption \n"

    pdf_image = doc_images[1]
    assert len(pdf_image.image_parts) == 1
    assert pdf_image.caption is not None
    assert pdf_image.caption.caption_text == "Fig. 2 This is also a caption \n"
