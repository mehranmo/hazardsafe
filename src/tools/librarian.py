import os
import chromadb
from chromadb.utils import embedding_functions
from pypdf import PdfReader
import google.generativeai as genai

# Configure Gemini API (Assuming GOOGLE_API_KEY is in env)
# If not, we might need to ask the user or use a placeholder.
# For this implementation, we'll use a simple sentence transformer for local embedding 
# if Gemini is not set, to ensure it runs in the Kaggle/Local env without friction initially.
# But ideally we use Gemini embeddings.

class Librarian:
    def __init__(self, db_path="data/chroma_db"):
        self.client = chromadb.PersistentClient(path=db_path)
        
        # Use a default embedding function (all-MiniLM-L6-v2) which is free and local
        # This avoids API key issues for the basic setup. 
        # We can switch to GoogleGenerativeAIEmbeddingFunction later.
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        
        self.collection = self.client.get_or_create_collection(
            name="hazmat_regulations",
            embedding_function=self.embedding_fn
        )

    def ingest_pdf(self, pdf_path):
        print(f"Ingesting {pdf_path}...")
        reader = PdfReader(pdf_path)
        text_chunks = []
        metadatas = []
        ids = []

        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                # Simple chunking by paragraph or just page for now
                # For regulations, paragraph/section based is better.
                # Let's split by double newlines to get sections roughly.
                paragraphs = text.split('\n\n')
                for j, para in enumerate(paragraphs):
                    if len(para.strip()) > 20: # Ignore small noise
                        chunk_id = f"{os.path.basename(pdf_path)}_p{i}_s{j}"
                        text_chunks.append(para.strip())
                        metadatas.append({"source": pdf_path, "page": i})
                        ids.append(chunk_id)

        if text_chunks:
            self.collection.add(
                documents=text_chunks,
                metadatas=metadatas,
                ids=ids
            )
            print(f"Added {len(text_chunks)} chunks to ChromaDB.")
        else:
            print("No text found in PDF.")

    def query(self, query_text, n_results=3):
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        return results

if __name__ == "__main__":
    # Test run
    lib = Librarian()
    lib.ingest_pdf("data/regulations/hazmat_regulations.pdf")
    results = lib.query("What is the max temperature for Type B(U) packages?")
    print("\nQuery Result:")
    print(results['documents'][0])
