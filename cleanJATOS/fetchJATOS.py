import requests
import zipfile
import os

study_specs = {
   "emotion_old": "5fbace40-dac0-4b3a-8e5f-62387239103e",
   "emotion_adaptive": "c8e398c7-40a8-44e7-8be8-a7529bfac1a9",
   "mbema": "5a3e2dce-c190-48a4-9cb7-1eaab3f200ac",
   "movement": "c23e4b87-a25c-4714-9115-4bed367d4c1b",
   #"rhythm": "62520105-2786-45aa-9991-242459a624df",
   "shared": "227e292d-202d-4858-8f50-366d62054ce3"
}

# Base URL of your JATOS instance
base_url = "https://mmbb.ltdk.helsinki.fi/jatos/api/v1/results"
token = "jap_nu5C6jNF8zAMWYzNOfD2dHVQhJNZ1Ov02ad1a"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {token}"  # remove if not needed
}

def functionFetch(studyUuid, fname):
    payload = {
        "studyUuid": [studyUuid],
    }
    response = requests.post(base_url, headers=headers, params=payload)
    if response.status_code == 200:
        zip_filename = f"/Users/pdealcan/Documents/data/raw/{fname}.zip"
        with open(zip_filename, "wb") as f:
            f.write(response.content)
        print(f"Saved {zip_filename}")
        extract_dir = zip_filename.replace(".zip", "")
        os.makedirs(extract_dir, exist_ok=True)
        with zipfile.ZipFile(zip_filename, "r") as z:
            z.extractall(extract_dir)
            print(f"Extracted to {extract_dir}")
            #os.remove(zip_filename)
    else:
        print(f"Error {response.status_code}: {response.text}")

#Loop through all studies
for study_name, studyUuid in study_specs.items():
    print(f"Study: {study_name}, studyUuid: {studyUuid}")
    functionFetch(studyUuid, study_name)




