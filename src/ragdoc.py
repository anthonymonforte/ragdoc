"""RagDoc Main Entry Point"""

# pylint: disable=W0613
# pylint: disable=C0116
# pylint: disable=C0301
# pylint: disable=C0115
# pylint: disable=W0511

import argparse
import modules.pdf_module as pdf

def main():

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-p", required=True, help="PDF folder")
    arg_parser.add_argument("-r", required=False, help="Caption Regular Expression", default="(?:\\n|^)(Fig\\.\\s\\d+.*?)(?:\\n|$)")
    arg_parser.add_argument("-o", required=False, help="Image Part Offset Threshold", default=.5)
    arg_parser.add_argument("-a", required=False, help="Perform caption to image audit", default=True)
    arg_parser.add_argument("-cap_pos", required=False, help="Caption position relative to image", choices=["Above", "Below"], default="Below")
    args = arg_parser.parse_args()

    print(args.p)
    print(args.r)
    print(args.o)
    print(args.a)
    print(args.cap_pos)

    config = pdf.Config(folder_path=args.p, caption_above_img=args.cap_pos == "Above", perform_audit=args.a, caption_regex=args.r, image_part_offset_threshold=args.o)

    pdf_doc_proc = pdf.PdfDocProcessor(config)
    #extract_text_chunks(args.p, ChunkConfig(chunk_size=800, chunk_overlap=80))
    pdf_doc_proc.extract_images_and_captions_from_folder()

if __name__ == "__main__":
    main()
