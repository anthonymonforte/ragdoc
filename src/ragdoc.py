"""RagDoc Main Entry Point"""

# pylint: disable=W0613
# pylint: disable=C0116
# pylint: disable=C0301
# pylint: disable=C0115
# pylint: disable=W0511

import argparse
import modules.pdf_module as pdf
import modules.embedding_module as embed
import modules.database_module as db

def main():

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-p", required=True, help="PDF folder")
    arg_parser.add_argument("-m", required=True, help="Embedding Model")
    arg_parser.add_argument("-v", required=True, help="Embedding Model Version")
    arg_parser.add_argument("-url", required=True, help="Embedding Model URL")
    arg_parser.add_argument("-r", required=False, help="Caption Regular Expression", default="(?:\\n|^)(Fig\\.\\s\\d+.*?)(?:\\n|$)")
    arg_parser.add_argument("-o", required=False, help="Image Part Offset Threshold", default=.5)
    arg_parser.add_argument("-a", required=False, help="Perform caption to image audit", default=False)
    arg_parser.add_argument("-cap_pos", required=False, help="Caption position relative to image", choices=["Above", "Below"], default="Below")
    args = arg_parser.parse_args()

    print(args.p)
    print(args.m)
    print(args.v)
    print(args.url)
    print(args.r)
    print(args.o)
    print(args.a)
    print(args.cap_pos)

    config = pdf.Config(folder_path=args.p, caption_above_img=args.cap_pos == "Above", perform_audit=args.a, caption_regex=args.r, image_part_offset_threshold=args.o)

    pdf_doc_proc = pdf.PdfDocProcessor(config)
    chunks = pdf_doc_proc.extract_text_chunks(args.p)
    pdf_doc_proc.extract_images_and_captions_from_folder()

    doc_db = db.EmbeddingDb("Chroma")

    embedding = embed.Embeddings(model=args.m, version=args.v, url=args.url)
    doc_db.add_to_db(chunks, embedding.get_embedding_function())

if __name__ == "__main__":
    main()
