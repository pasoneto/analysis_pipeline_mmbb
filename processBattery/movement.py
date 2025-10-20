import pandas as pd
import numpy as np 
import json
import ast

data = pd.read_csv("/Users/pdealcan/Documents/data/processed/stage1/movement.csv")
data = data[data["accelerometer_data"] != ""]
data = data.dropna(subset=['accelerometer_data'])
data["stimulus"] = data["stimulus"].str.split("/").str[-1]
colsInterest = ["trial_index", "trialIndex", "uniqueID", "userID", "lang", "startDateJATOS", "endDateJATOS", "timeBegin", "timeEnd", "nodeIndex", "studyID", "accelerometer_data", "stimulus"]
data = data.sort_values(["studyID", "userID", "nodeIndex", "trialIndex", "trial_index"]).reset_index(drop=True)

#Checking if any stimulus is lost along the way
initial_n_stimuli = len(data["stimulus"].unique())

#Remove some participants
#out = ["test", "test_3", "c4fec400-39ad-4081-84a1-2035dc437f8d", "9f3eba1a-677f-4378-b7ae-c0bf3089fe9e", "test3", "participantpractice2", "participantTEST"]
#data = data[~data["userID"].isin(out)]
#data = data[~data["userID"].str.contains("test", case=False, na=False)]

# Expand accelerometer dictionaries into columns
data["accelerometer_data"] = data["accelerometer_data"].str.replace("None", "null")
data["accelerometer_data"] = data["accelerometer_data"].str.replace("'", '"')
data = data.reset_index()
data["accelerometer_data"] = [json.loads(k) for k in data["accelerometer_data"]]

#assert initial_n_stimuli == len(data["stimulus"].unique()), "Lost stimulus at checkpoint 1"

# 2. Extract the dict (since it's always inside a list of length 1)
data["accelerometer_data"] = data["accelerometer_data"].str[0]
df_expanded = data.join(pd.json_normalize(data["accelerometer_data"]))

# explode each list column
data = df_expanded.explode(list(df_expanded["accelerometer_data"].iloc[0].keys()))
data = data.drop(columns=["accelerometer_data"]) 

# Compute minimum trial_index for each user (trial_index changes between two occurences of silence.wav)
min_trial = data.groupby(["studyID", "userID"])["trial_index"].transform("min")

# Filter out rows where stimulus == silence.wav AND trial_index == min
data = data[~((data["stimulus"] == "silence.wav") & (data["trial_index"] == min_trial))]
data = data.sort_values(["studyID", "userID", "startDateJATOS", "trial_index", "t"]).reset_index(drop=True)

#assert initial_n_stimuli == len(data["stimulus"].unique()), "Lost stimulus at checkpoint 2"

# (Not working) Keep only first performance of battery. trialIndex differentiates between each task, but not between silence.wav occurances
#data = data.loc[data.groupby(["studyID","userID","trialIndex"])["startDateJATOS"].idxmin()]

#Writting results
colsInterest = ["studyID", "userID", "startDateJATOS", "endDateJATOS", "trial_index", "stimulus", "x", "y", "z", "t", "timeAudio", "gamma", "alpha", "beta"]
data = data[colsInterest]

dir_out = "/Users/pdealcan/Documents/data/processed/stage2/"
data.to_csv(f"{dir_out}movement.csv")

print("Movement:")
print(data.groupby("studyID")["userID"].nunique())

