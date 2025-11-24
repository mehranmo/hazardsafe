import os
import json
import time
from google.cloud import firestore
from google.auth.exceptions import DefaultCredentialsError

class FirestoreClient:
    def __init__(self, collection_name="provenance_events"):
        self.collection_name = collection_name
        self.use_local = False
        self.local_db_path = "data/firestore_mock.json"
        self.db = None
        
        # Try to initialize real Firestore
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        if project_id:
            try:
                self.db = firestore.Client(project=project_id)
                print(f"[Firestore] Connected to project: {project_id}")
            except (DefaultCredentialsError, Exception) as e:
                print(f"[Firestore] Connection failed ({e}). Falling back to local JSON.")
                self.use_local = True
        else:
            print("[Firestore] GOOGLE_CLOUD_PROJECT not set. Using local JSON mock.")
            self.use_local = True

        if self.use_local:
            # Ensure local db file exists
            if not os.path.exists(self.local_db_path):
                with open(self.local_db_path, 'w') as f:
                    json.dump({}, f)

    def add_document(self, data):
        """
        Adds a document to the collection.
        """
        timestamp = int(time.time())
        data['timestamp'] = timestamp
        
        if self.use_local:
            return self._add_local(data)
        else:
            try:
                # Add to real Firestore
                update_time, doc_ref = self.db.collection(self.collection_name).add(data)
                return doc_ref.id
            except Exception as e:
                print(f"[Firestore] Write failed: {e}. Fallback to local.")
                return self._add_local(data)

    def _add_local(self, data):
        try:
            with open(self.local_db_path, 'r') as f:
                db = json.load(f)
            
            if self.collection_name not in db:
                db[self.collection_name] = []
            
            # Generate a simple ID
            doc_id = f"evt_{int(time.time()*1000)}"
            data['id'] = doc_id
            db[self.collection_name].append(data)
            
            with open(self.local_db_path, 'w') as f:
                json.dump(db, f, indent=2)
                
            return doc_id
        except Exception as e:
            print(f"[Firestore] Local write failed: {e}")
            return None

    def get_all_documents(self):
        if self.use_local:
            with open(self.local_db_path, 'r') as f:
                db = json.load(f)
            return db.get(self.collection_name, [])
        else:
            docs = self.db.collection(self.collection_name).stream()
            return [d.to_dict() for d in docs]
