from src.tools.librarian import Librarian

def verify_rag():
    print("Initializing Librarian...")
    lib = Librarian()
    
    # Ensure data is ingested (idempotent-ish, chroma handles duplicates by ID usually, 
    # but our simple script might error if IDs exist. 
    # Actually ChromaDB .add fails if IDs exist. 
    # We should use .upsert or handle it. 
    # For this verification, we assume it might be fresh or we just query.
    
    # Let's try to query first.
    query = "What is the separation distance for Transport Index 3.0?"
    print(f"\nQuerying: '{query}'")
    
    results = lib.query(query)
    
    if results['documents'] and results['documents'][0]:
        print("\nTop Result:")
        print(results['documents'][0][0])
        print("\nSource:")
        print(results['metadatas'][0][0])
        print("\n✅ RAG Verification Passed!")
    else:
        print("\n❌ No results found. Ingesting data first...")
        lib.ingest_pdf("data/regulations/hazmat_regulations.pdf")
        
        # Retry query
        results = lib.query(query)
        if results['documents'] and results['documents'][0]:
            print("\nTop Result:")
            print(results['documents'][0][0])
            print("\n✅ RAG Verification Passed after ingestion!")
        else:
            print("\n❌ RAG Verification Failed.")

if __name__ == "__main__":
    verify_rag()
