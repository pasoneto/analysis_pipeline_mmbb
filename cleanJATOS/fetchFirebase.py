# First, ensure you have the Firebase Admin SDK initialized.
from firebase_admin import credentials, initialize_app
from firebase_admin import firestore
import pandas as pd
import json

path_out = "../../../../data/raw/survey_order"
cred = credentials.Certificate("./sequence-e4afd-firebase-adminsdk-mpw3f-0967fc424a.json")
initialize_app(cred) # No databaseURL needed for Firestore client

# Get a reference to the Firestore database
db = firestore.client()
target_collections = ['survey_order', 'survey_order2', 'survey_order3']
selected_firestore_data = {}
for collection_id in target_collections:
    print(f"Fetching data from collection: {collection_id}")
    collection_ref = db.collection(collection_id)
    documents = collection_ref.stream()
    collection_data = {}
    for doc in documents:
        collection_data[doc.id] = doc.to_dict()
    df = pd.DataFrame.from_dict(collection_data, orient='index')
    # Save the collected data to a JSON file
    fname = f"{path_out}/{collection_id}.json"
    with open(fname, 'w', encoding='utf-8') as f:
        json.dump(collection_data, f, indent=4, ensure_ascii=False)
