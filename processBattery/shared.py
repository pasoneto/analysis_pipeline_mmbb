import pandas as pd
import numpy as np
import ast  # safely evaluate strings like dicts
import re
import json

# Read the files
data = pd.read_csv("/Users/pdealcan/Documents/data/processed/stage1/shared.csv")

# Read the JSON file
with open("/Users/pdealcan/Documents/code/mmbb/processing/processBattery/info_shared/translations.json", "r", encoding="utf-8") as f:
    translations = json.load(f)

# Create a dictionary mapping English -> Finnish
eng_fi_map = {v['eng']: v['fi'] for v in translations.values() if 'eng' in v and 'fi' in v}

# Function to replace Finnish with English
def fi_to_eng(text, mapping):
    if text in mapping.values():  # If text is in Finnish
        return next((eng for eng, fi in mapping.items() if fi == text), text)
    return text

#Remove some participants
out = ["test", "test_3", "c4fec400-39ad-4081-84a1-2035dc437f8d", "9f3eba1a-677f-4378-b7ae-c0bf3089fe9e", "test3", "participantpractice2", "participantTEST"]
data = data[~data["userID"].isin(out)]
data = data[~data["userID"].str.contains("test", case=False, na=False)]

colsInterest = ["userID", "studyID", "response", "startDateJATOS", "endDateJATOS"]
data = data[colsInterest]

print("Shared:")
print(data.groupby("studyID")["userID"].nunique())

data = data.dropna(subset=['response'])
data["response"] = data["response"].apply(ast.literal_eval)
data = data[data["response"] != 0]
data[["question", "answer"]] = data["response"].apply(lambda d: pd.Series(list(d.items())[0]))
#data = data.drop(columns=["response"])

# Apply to both columns
data['question'] = data['question'].apply(lambda x: fi_to_eng(x, eng_fi_map))
data['answer'] = data['answer'].apply(lambda x: fi_to_eng(x, eng_fi_map))

#Appending categories
categories = pd.read_csv("/Users/pdealcan/Documents/code/mmbb/processing/processBattery/info_shared/questionnaire_categories.csv")
data = pd.merge(data, categories, left_on = "question", right_on = "eng", how= "left")

#Get scales to numeric values
with open("../processBattery/info_shared/response_scale.json", "r", encoding="utf-8") as f:
    rs = json.load(f)
scale_converter = {}
for inner_dict in rs.values():
    scale_converter.update(inner_dict)

data['answer'] = data['answer'].map(scale_converter).fillna(data['answer'])

colsInterest = ["userID","studyID","startDateJATOS","endDateJATOS","question","answer", "questionnaire"]
data = data[colsInterest]

data = data.dropna(subset=['answer'])

bq = ["yearOfBirth", "Where are you from?", "Gender", "Education", "What is your primary spoken language?", "What is your secondary spoken language? (If applicable)"]
base_questions = data[data["question"].isin(bq)][["question", "answer", "userID", "questionnaire", "studyID"]]

base_questions_wide = (
    base_questions
    .pivot_table(
        index=["userID", "studyID"],   # keep these as identifiers
        columns="question",             # each question becomes a column
        values="answer",                # fill with answer values
        aggfunc="first"                 # if duplicates, take the first
    )
    .reset_index()                      # make sure userID & studyID are normal columns again
)

data = data[~data["question"].isin(bq)][["question", "questionnaire", "answer", "userID", "studyID", "startDateJATOS"]]

data = data.merge(
    base_questions_wide,
    on=["userID", "studyID"],
    how="left"   # keep all rows from data, attach matching background info
)

#Categorize stomp
with open("/Users/pdealcan/Documents/code/mmbb/processing/processBattery/info_shared/stomp_cats.json", "r", encoding="utf-8") as f:
    stomp_cats = json.load(f)

data["stomp_cats"] = data["question"].map(stomp_cats)

dir_out = "/Users/pdealcan/Documents/data/processed/stage2/"
data.to_csv(f"{dir_out}shared.csv")
