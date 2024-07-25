"""Integration Tests for PDF module."""

# pylint: disable=W0613
# pylint: disable=C0116
# pylint: disable=C0301
# pylint: disable=C0115
# pylint: disable=W0511

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import modules.pdf_module as pdf

def test_extract_images_and_captions_from_pdf1():
    doc_images = pdf.extract_images_and_captions_from_doc(os.path.join(os.path.dirname(__file__), "test_assets/pdfs/pdf1_test.pdf"), False)

    assert len(doc_images) == 1
    pdf_image = doc_images[0]

    assert len(pdf_image.image_parts) == 1
    assert pdf_image.caption is not None
    assert pdf_image.caption.caption_text == "Fig. 1 This is a caption. \n"

def test_extract_images_and_captions_from_pdf2():
    doc_images = pdf.extract_images_and_captions_from_doc(os.path.join(os.path.dirname(__file__), "test_assets/pdfs/pdf2_test.pdf"), False)

    assert len(doc_images) == 2

    pdf_image = doc_images[0]
    assert len(pdf_image.image_parts) == 1
    assert pdf_image.caption is None

    pdf_image = doc_images[1]
    assert len(pdf_image.image_parts) == 1
    assert pdf_image.caption is not None
    assert pdf_image.caption.caption_text == "Fig. 1 This is a caption, on the next page. \n"
