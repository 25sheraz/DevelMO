import os
import sys
import argparse
from typing import List
from dotenv import load_dotenv

# Reconfigure stdout encoding for Windows compatibility
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

load_dotenv()

from document_processor import DocumentProcessor
from qdrant_manager import QdrantManager
from sentence_transformers import SentenceTransformer

# Suppress HF noisy warnings
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

def ingest_file(file_path: str, processor: DocumentProcessor, embed_model: SentenceTransformer, manager: QdrantManager):
    """Processes a single file, generates embeddings, and uploads to Qdrant."""
    print(f"\n📄 Ingesting: {file_path}")
    chunks = processor.chunk_document(file_path)
    if not chunks:
        print(f"⚠️ No text content extracted from {file_path}.")
        return 0

    print(f"   Generated {len(chunks)} chunks (size={processor.chunk_size}, overlap={processor.chunk_overlap}).")
    
    texts = [c["content"] for c in chunks]
    model_label = getattr(embed_model, 'model_name_or_path', 'SentenceTransformer')
    print(f"   Computing embeddings using '{model_label}'...")
    embeddings = embed_model.encode(texts, show_progress_bar=False, batch_size=32).tolist()

    print(f"   Upserting {len(embeddings)} vectors into Qdrant collection '{manager.collection_name}'...")
    manager.upsert_chunks(chunks, embeddings)
    return len(chunks)

def ingest_directory(dir_path: str, processor: DocumentProcessor, embed_model: SentenceTransformer, manager: QdrantManager):
    """Ingests all supported documents (.pdf, .md, .txt) in a directory."""
    if not os.path.exists(dir_path):
        print(f"❌ Directory not found: {dir_path}")
        return

    supported_exts = {".pdf", ".md", ".txt", ".markdown"}
    total_files = 0
    total_chunks = 0

    for root, _, files in os.walk(dir_path):
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext in supported_exts:
                file_path = os.path.join(root, f)
                chunks_count = ingest_file(file_path, processor, embed_model, manager)
                total_files += 1
                total_chunks += chunks_count

    print(f"\n✅ Directory Ingestion Complete!")
    print(f"   Files Processed : {total_files}")
    print(f"   Total Chunks    : {total_chunks}")

def main():
    parser = argparse.ArgumentParser(description="DevelMo RAG Document Ingestion Tool")
    parser.add_argument("--file", "-f", help="Path to a single PDF, Markdown, or Text file to ingest.")
    parser.add_argument("--dir", "-d", help="Path to a directory containing documents to ingest.")
    parser.add_argument("--recreate", action="store_true", help="Recreate Qdrant collection before ingesting.")
    
    args = parser.parse_args()

    # Default to DevelMo_Knowledge_Base.md if no arguments supplied
    if not args.file and not args.dir:
        default_file = "DevelMo_Knowledge_Base.md"
        if os.path.exists(default_file):
            print(f"ℹ️ No file/directory specified. Defaulting to '{default_file}'.")
            args.file = default_file
        else:
            parser.print_help()
            return

    # Initialize components
    embedding_model_name = os.getenv("EMBEDDING_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    print(f"🤖 Loading Embedding Model from local cache: '{embedding_model_name}'...")
    embed_model = SentenceTransformer(embedding_model_name, local_files_only=True)

    processor = DocumentProcessor()
    manager = QdrantManager(force_recreate=args.recreate)

    if args.file:
        ingest_file(args.file, processor, embed_model, manager)
    elif args.dir:
        ingest_directory(args.dir, processor, embed_model, manager)

    # Print final collection status
    info = manager.get_info()
    print("\n" + "=" * 50)
    print(f"📊 QDRANT COLLECTION STATUS: '{info['name']}'")
    print(f"   Total Vector Points: {info['vectors_count']}")
    print(f"   Collection Status  : {info['status']}")
    print("=" * 50)

if __name__ == "__main__":
    main()
    