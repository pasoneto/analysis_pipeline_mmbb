import pandas as pd
import numpy as np
import json

data = pd.read_csv("/Users/pdealcan/Documents/data/processed/stage1/mbema.csv")

#Remove some participants
out = ["test", "test_3", "c4fec400-39ad-4081-84a1-2035dc437f8d", "9f3eba1a-677f-4378-b7ae-c0bf3089fe9e", "test3", "participantpractice2", "participantTEST"]
data = data[~data["userID"].isin(out)]
data = data[~data["userID"].str.contains("test", case=False, na=False)]
data = data[~data["userID"].isna()]

#Verify lost users
initial = len(data["userID"].unique())

#Get only trials of interest
#Very important to sort
data = data.sort_values(["studyID", "userID", "startDateJATOS", "trial_index"]).reset_index(drop=True) 

#data[data["userID"] == "516"][["trial_index", "startDateJATOS", "stimulus", "response", "userID", "studyID"]].to_csv("test.csv")

data["response"] = data["response"].shift(-1)
data = data[data["stimulus"].str.contains("wav", na=False)]

#Verify lost users
assert initial == len(data["userID"].unique())

data = data[["trial_index", "startDateJATOS", "stimulus", "response", "userID", "studyID"]]

print("MBEMA:")
print(data.groupby("studyID")["userID"].nunique())

# correct sheet for different parts (melody/rhythm/memory)
# 0==same/old_melody, 1==different/novel_melody
pt1_corr=[1,0,1,1,1,0,1,0,0,0,1,0,1,0,1,0,1,0,0,1]
pt2_corr=[1,0,0,1,1,0,1,1,0,1,0,1,0,0,1,0,0,1,0,1]
pt3_corr=[1,0,1,1,0,0,1,0,1,1,0,0,1,1,0,1,0,1,0,0]

#Lukilapsi
p1_reduced = [1,3,4,6,5,8,9,14,20,16]
p2_reduced = [1,3,9,10,13,14,15,16,18,20]
p3_reduced = [1,3,4,6,9,12,10,15,17,20]

#Removing example files
data = data[~data["stimulus"].str.contains("example", case=False, na=False)]

# Sort so earliest dates come first
data = data.sort_values(['userID', 'studyID', 'stimulus', 'startDateJATOS'])
data = data.drop_duplicates(subset=['userID', 'studyID', 'stimulus'], keep='first')

# Check
check_counts = data.groupby(['userID', 'studyID']).size()
assert len(check_counts[~check_counts.isin([30, 60])]) == 0

#Verify lost users again
assert initial == len(data["userID"].unique())

#Verify NA in response
assert len(data[data["response"].isna()][["userID", "stimulus", "response"]]) == 0

#Attach correct response
melody = ["bMelody - 2.wav", "bMelody - 3.wav", "bMelody - 4.wav", "bMelody - 5.wav", "bMelody - 6.wav", "bMelody - 7.wav", "bMelody - 8.wav", "bMelody - 9.wav", "bMelody - 10.wav", "bMelody - 11.wav", "bMelody - 12.wav", "bMelody - 13.wav", "bMelody - 14.wav", "bMelody - 15.wav", "bMelody - 16.wav", "bMelody - 17.wav", "bMelody - 18.wav", "bMelody - 19.wav", "bMelody - 20.wav"]
rhythm = ["bRhythm - 2.wav", "bRhythm - 3.wav", "bRhythm - 4.wav", "bRhythm - 5.wav", "bRhythm - 6.wav", "bRhythm - 7.wav", "bRhythm - 8.wav", "bRhythm - 9.wav", "bRhythm - 10.wav", "bRhythm - 11.wav", "bRhythm - 12.wav", "bRhythm - 13.wav", "bRhythm - 14.wav", "bRhythm - 15.wav", "bRhythm - 16.wav", "bRhythm - 17.wav", "bRhythm - 18.wav", "bRhythm - 19.wav", "bRhythm - 20.wav"]
memory = ["bMemory - 2.wav", "bMemory - 3.wav", "bMemory - 4.wav", "bMemory - 5.wav", "bMemory - 6.wav", "bMemory - 7.wav", "bMemory - 8.wav", "bMemory - 9.wav", "bMemory - 10.wav", "bMemory - 11.wav", "bMemory - 12.wav", "bMemory - 13.wav", "bMemory - 14.wav", "bMemory - 15.wav", "bMemory - 16.wav", "bMemory - 17.wav", "bMemory - 18.wav", "bMemory - 19.wav", "bMemory - 20.wav"]

melody_c=[1,0,1,1,1,0,1,0,0,0,1,0,1,0,1,0,1,0,0,1]
rhythm_c=[1,0,0,1,1,0,1,1,0,1,0,1,0,0,1,0,0,1,0,1]
memory_c=[1,0,1,1,0,0,1,0,1,1,0,0,1,1,0,1,0,1,0,0]

melody_dict = dict(zip(melody, melody_c))
rhythm_dict = dict(zip(rhythm, rhythm_c))
memory_dict = dict(zip(memory, memory_c))

correct_responses = {**melody_dict, **rhythm_dict, **memory_dict}
with open("./correct_responses.json", "w") as f:
    json.dump(correct_responses, f, indent=4) 

# Check if response matches value for any key contained in the stimulus
def check_match(row):
    stimulus_str = str(row["stimulus"]).strip()
    for key, value in correct_responses.items():
        if key in stimulus_str:  # check if key string is contained
            return int(row["response"]) == value
    return False

data["correct"] = data.apply(check_match, axis=1)

#Verify lost users again
assert initial == len(data["userID"].unique())

#Add subsection of mbema
def check_letter(stimulus):
    for letter in ["Rhythm", "Melody", "Memory"]:
        if letter in stimulus:
            return letter
    return None

data["section"] = data["stimulus"].apply(check_letter)

data = data.sort_values(['studyID', 'userID', 'section', 'trial_index', 'startDateJATOS'])
dir_out = "/Users/pdealcan/Documents/data/processed/stage2/"

data.to_csv(f"{dir_out}mbema.csv")
