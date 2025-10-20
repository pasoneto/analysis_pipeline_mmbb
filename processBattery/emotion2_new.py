import pandas as pd
import numpy as np
import sys

data = pd.read_csv("/Users/pdealcan/Documents/data/processed/stage1/emotion_adaptive.csv")
types_stay = ["audio-keyboard-response", "html-multi-slider-response"]
data = data[data["trial_type"].isin(types_stay)]
cols_interest = ["userID", "stimulus", "startDateJATOS", "endDateJATOS", "response", "studyID", "trial_index"]
data = data[data["part"] == "Two"][cols_interest]
remove_values = "Is someone helping you to complete this task?", "", "./songs/movementTapAudio/elPesebre.mp3"
data = data[~data["stimulus"].isin(remove_values)]

data = data.reset_index(drop=True)
data = data.sort_values(by=["userID", "trial_index"])

#Users who did the task more than once
user_out = data[data.duplicated(subset=["userID", "trial_index", "startDateJATOS", "endDateJATOS"], keep=False)]["userID"].unique()
data = data[~data["userID"].isin(user_out)]
data = data.reset_index(drop=True)

#Question rows
expected1 = [
    "['', '']",
    "['How strong are the emotions expressed by the music?']",
    "['How much did you like the music?']"
]
expected2 = [
    "['', '']",
    "['Kuinka voimakkaasti musiikki ilmaisee tunteita?']",
    "['Kuinka paljon pidit musiikista?']"
]
errors = []
rows = []
i = 0
while i < len(data):
    # If this is a stimulus row (mp3 file)
    if isinstance(data.loc[i, "stimulus"], str) and data.loc[i, "stimulus"].endswith(".mp3"):
        stimulus = data.loc[i, "stimulus"]
        # Get the next 3 rows of the 'stimulus' column
        next_rows = data.loc[i+1:i+3, "stimulus"].tolist()

        # Check they match expected
        if next_rows != expected1 and next_rows != expected2:
            print("error")
            print(i)
            errors.append((stimulus, next_rows))

        # Copy next 3 rows and overwrite/add values
        for j in range(1, 4):
            row = data.loc[i+j].copy()   # copy whole row
            row["3d"] = row["stimulus"]  # save question into "3d"
            row["stimulus"] = stimulus   # overwrite with mp3 name
            rows.append(row)

        i += 4
    else:
        i += 1


# Build new DataFrame with all original columns + "3d"
reshaped = pd.DataFrame(rows)
#questions_stay = ["['How strong are the emotions expressed by the music?']", "['Kuinka voimakkaasti musiikki ilmaisee tunteita?']"]
#reshaped = reshaped[~reshaped["3d"].isin(questions_stay)]


reshaped["3d"] = reshaped["3d"].replace("['How much did you like the music?']", "like", regex=False)
reshaped["3d"] = reshaped["3d"].replace("['Kuinka paljon pidit musiikista?']", "like", regex=False)
reshaped["3d"] = reshaped["3d"].replace("['How strong are the emotions expressed by the music?']", "strength", regex=False)
reshaped["3d"] = reshaped["3d"].replace("['Kuinka voimakkaasti musiikki ilmaisee tunteita?']", "strength", regex=False)
reshaped["3d"] = reshaped["3d"].replace("['', '']", "valence_arousal", regex=False)
reshaped["response"] = reshaped["response"].replace(r"[\[\]]", "", regex=True)

# Function to create repeating integers per user
def repeat_integers(group):
    n = len(group)
    # Repeat integers 1,2,... each 2 times
    repeated = [i for i in range(1, (n+1)//2 + 1) for _ in range(3)]
    # Slice in case of odd length
    return repeated[:n]

# Apply per userID
reshaped["tIndex"] = reshaped.groupby(["userID", "startDateJATOS"]).apply(lambda g: repeat_integers(g)).explode().astype(int).values

print(f"stage 1: {reshaped.columns}")
#unique_counts = reshaped.groupby("userID")["tIndex"].nunique()
#frequency = unique_counts.value_counts().sort_index()
#print(frequency)

reshaped = reshaped.pivot_table(
    index=['userID', 'studyID', 'stimulus', 'tIndex', 'startDateJATOS', 'endDateJATOS'],  # these will stay as row identifiers
    columns='3d',                            # this will create new columns
    values='response',                        # values to fill in the new columns
    aggfunc='first',                           # in case there are duplicates
    sort=False  # 👈 this keeps the original order of the index values
).reset_index()

reshaped = reshaped.sort_values(by=["userID", "tIndex"])

print(f"stage 2: {reshaped.columns}")

# Optional: flatten the columns if needed
reshaped.columns.name = None

# Split the column into two
reshaped[['valence', 'arousal']] = reshaped['valence_arousal'].str.split(', ', expand=True)

# Convert to numeric if needed
reshaped['valence'] = reshaped['valence'].astype(int)
reshaped['arousal'] = reshaped['arousal'].astype(int)

reshaped = reshaped.drop(columns=['valence_arousal'])

#remove path from stimulus names
reshaped["stimulus"] = reshaped["stimulus"].replace("././songs/emotionAudio/trimmed_part2_mp3/", "", regex=False)

print(f"stage 3: {reshaped.columns}")

dir_out = "/Users/pdealcan/Documents/data/processed/stage2/"
reshaped.to_csv(f"{dir_out}processed_emotion_adaptive.csv")

print("Emotion 2 - adaptive:")
print(data.groupby(["studyID", "startDateJATOS"])["userID"].nunique())
