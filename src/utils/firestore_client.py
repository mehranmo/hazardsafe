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

    def get_document(self, doc_id):
        """
        Retrieves a specific document by ID.
        """
        if self.use_local:
            with open(self.local_db_path, 'r') as f:
                db = json.load(f)
            docs = db.get(self.collection_name, [])
            for doc in docs:
                if doc.get('id') == doc_id:
                    return doc
            return None
        else:
            try:
                doc = self.db.collection(self.collection_name).document(doc_id).get()
                if doc.exists:
                    return doc.to_dict()
                return None
            except Exception as e:
                print(f"[Firestore] Get document failed: {e}")
                return None

    def update_document(self, doc_id, data):
        """
        Updates an existing document by ID.
        """
        timestamp = int(time.time())
        data['updated_at'] = timestamp
        
        if self.use_local:
            return self._update_local(doc_id, data)
        else:
            try:
                self.db.collection(self.collection_name).document(doc_id).update(data)
                return True
            except Exception as e:
                print(f"[Firestore] Update failed: {e}. Fallback to local.")
                return self._update_local(doc_id, data)

    def _update_local(self, doc_id, data):
        try:
            with open(self.local_db_path, 'r') as f:
                db = json.load(f)
            
            if self.collection_name not in db:
                return False
            
            docs = db[self.collection_name]
            for i, doc in enumerate(docs):
                if doc.get('id') == doc_id:
                    # Merge update data with existing document
                    docs[i].update(data)
                    
                    with open(self.local_db_path, 'w') as f:
                        json.dump(db, f, indent=2)
                    return True
            
            return False
        except Exception as e:
            print(f"[Firestore] Local update failed: {e}")
            return False

    def query_documents(self, filters):
        """
        Query documents with filters.
        filters: dict like {"status": "PENDING_HITL", "created_at": {">=": 123456}}
        """
        if self.use_local:
            with open(self.local_db_path, 'r') as f:
                db = json.load(f)
            docs = db.get(self.collection_name, [])
            
            # Simple filtering for local mode
            results = []
            for doc in docs:
                match = True
                for key, value in filters.items():
                    if isinstance(value, dict):
                        # Handle comparison operators
                        for op, target in value.items():
                            doc_val = doc.get(key)
                            if op == ">=" and not (doc_val >= target):
                                match = False
                            elif op == "<=" and not (doc_val <= target):
                                match = False
                            elif op == ">" and not (doc_val > target):
                                match = False
                            elif op == "<" and not (doc_val < target):
                                match = False
                    else:
                        # Exact match
                        if doc.get(key) != value:
                            match = False
                if match:
                    results.append(doc)
            return results
        else:
            try:
                query = self.db.collection(self.collection_name)
                for key, value in filters.items():
                    if isinstance(value, dict):
                        for op, target in value.items():
                            query = query.where(key, op, target)
                    else:
                        query = query.where(key, "==", value)
                docs = query.stream()
                return [d.to_dict() for d in docs]
            except Exception as e:
                print(f"[Firestore] Query failed: {e}")
                return []
