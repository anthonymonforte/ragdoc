"""Tests for PDF module."""

# pylint: disable=W0613
# pylint: disable=C0116
# pylint: disable=C0301
# pylint: disable=C0115
# pylint: disable=W0511

import sys
import os
from typing import List

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import modules.pdf_module as pdf
from modules.pdf_module import PdfImage, ImagePart

def create_pdf_image_obj(image_bbox: List[float], page: int, xref: int):    
    return PdfImage(image_bbox=image_bbox, image_page=page, caption=None, image_parts=[ImagePart(xref=xref, bbox=image_bbox)])


def get_default_config():
    return pdf.Config(folder_path=os.path.dirname(__file__), caption_above_img=False, perform_audit=False, caption_regex=r'(?:\n|^)(Fig\.\s\d+.*?)(?:\n|$)', image_part_offset_threshold=.5)

def get_default_pdf_module():
    return pdf.PdfDocProcessor(get_default_config())

def test_combine_images_should_not_combine_separate_images():
    image_list = [create_pdf_image_obj([0,0,0,5], 1, 1),
                  create_pdf_image_obj([0,10,0,15], 1, 2)]
    result = get_default_pdf_module().combine_images(image_list)
    assert len(result) == 2
    assert len(result[0].image_parts) == 1
    assert len(result[1].image_parts) == 1


def test_combine_images_should_combine_image_parts():
    image_list = [create_pdf_image_obj([0,0,0,5], 1, 1),
                  create_pdf_image_obj([0,5,0,15], 1, 2)]
    result = get_default_pdf_module().combine_images(image_list)
    assert len(result) == 1
    assert len(result[0].image_parts) == 2

def test_combine_images_should_combine_image_parts_within_threshold():
    config = get_default_config()

    image_list = [create_pdf_image_obj([0,0,0,5], 1, 1),
                  create_pdf_image_obj([0,5 + config.image_part_offset_threshold,0,15], 1, 2)]
    result = get_default_pdf_module().combine_images(image_list)
    assert len(result) == 1
    assert len(result[0].image_parts) == 2

def test_combine_images_should_not_combine_image_parts_outside_threshold():
    config = get_default_config()

    image_list = [create_pdf_image_obj([0,0,0,5], 1, 1),
                  create_pdf_image_obj([0,5 + config.image_part_offset_threshold + .01,0,15], 1, 2)]
    result = get_default_pdf_module().combine_images(image_list)
    assert len(result) == 2
    assert len(result[0].image_parts) == 1
    assert len(result[1].image_parts) == 1
