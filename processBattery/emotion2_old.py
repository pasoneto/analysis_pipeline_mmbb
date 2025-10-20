import pandas as pd
import numpy as np
import sys

data = pd.read_csv("/Users/pdealcan/Documents/data/processed/stage1/emotion_old.csv")
types_stay = ["audio-keyboard-response", "html-multi-slider-response"]
data = data[data["trial_type"].isin(types_stay)]

cols_interest = ["userID", "stimulus", "startDateJATOS", "endDateJATOS", "response", "studyID", "trial_index"]
#remove_values = ["['Kuinka paljon pidit, tai et pitänyt musiikista?', 'Kuinka tutulta musiikki kuulosti?']", "['How much did you like/dislike the music?', 'How familiar did the music sound to you?']"]
#data = data[~data["stimulus"].isin(remove_values)]
data = data.sort_values(by=["userID", "startDateJATOS", "trial_index"])
data = data.reset_index(drop=True)

#Users who did the task more than once
user_out = data[data.duplicated(subset=["userID", "trial_index"], keep=False)]["userID"].unique()
data = data[~data["userID"].isin(user_out)]
data = data.reset_index(drop=True)

#Check structure of dataframe
targets = ["['Tunnetila', 'Energisyys', 'Kuinka voimakkaasti musiikki ilmaisee tunteita?']", "['Mood', 'Energy', 'How strong are the emotions expressed by the music?']"]
condition = data["stimulus"].astype(str).str.contains(r"\.mp3")
next_row = data.groupby("userID")["stimulus"].shift(-1)
violations = data.index[
    condition & ~next_row.isin(targets)
]
print("Violations at indices:", violations.tolist())

#Question rows
expected = [
    "['Tunnetila', 'Energisyys', 'Kuinka voimakkaasti musiikki ilmaisee tunteita?']",
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
        if next_rows != expected:
            errors.append((stimulus, next_rows))

        # Copy next 3 rows and overwrite/add values
        for j in range(1, 3):
            row = data.loc[i+j].copy()   # copy whole row
            row["3d"] = row["stimulus"]  # save question into "3d"
            row["stimulus"] = stimulus   # overwrite with mp3 name
            rows.append(row)

        i += 3
    else:
        i += 3


# Build new DataFrame with all original columns + "3d"
reshaped = pd.DataFrame(rows)
#questions_stay = ["['How strong are the emotions expressed by the music?']", "['Kuinka voimakkaasti musiikki ilmaisee tunteita?']"]
#reshaped = reshaped[~reshaped["3d"].isin(questions_stay)]
reshaped["3d"] = reshaped["3d"].replace("['How much did you like the music?']", "like", regex=False)
reshaped["3d"] = reshaped["3d"].replace("['Kuinka paljon pidit musiikista?']", "like", regex=False)
reshaped["3d"] = reshaped["3d"].replace("['How strong are the emotions expressed by the music?']", "strength", regex=False)
reshaped["3d"] = reshaped["3d"].replace("['Kuinka voimakkaasti musiikki ilmaisee tunteita?']", "strength", regex=False)
reshaped["3d"] = reshaped["3d"].replace("['', '']", "valence_arousal", regex=False)
reshaped["3d"] = reshaped["3d"].replace("['Tunnetila', 'Energisyys', 'Kuinka voimakkaasti musiikki ilmaisee tunteita?']", "valence_arousal_strength", regex=False)
reshaped["3d"] = reshaped["3d"].replace("['Mood', 'Energy', 'How strong are the emotions expressed by the music?']", "valence_arousal_strength", regex=False)
reshaped["3d"] = reshaped["3d"].replace("['Kuinka paljon pidit, tai et pitänyt musiikista?', 'Kuinka tutulta musiikki kuulosti?']" , "like_familiar", regex=False)
reshaped["3d"] = reshaped["3d"].replace("['How much did you like/dislike the music?', 'How familiar did the music sound to you?']", "like_familiar", regex=False)

reshaped["response"] = reshaped["response"].replace(r"[\[\]]", "", regex=True)

# Function to create repeating integers per user
def repeat_integers(group):
    n = len(group)
    # Repeat integers 1,2,... each 2 times
    repeated = [i for i in range(1, (n+1)//2 + 1) for _ in range(2)]
    # Slice in case of odd length
    return repeated[:n]

# Apply per userID
reshaped["tIndex"] = reshaped.groupby(["userID", "startDateJATOS"]).apply(lambda g: repeat_integers(g)).explode().astype(int).values

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

# Optional: flatten the columns if needed
reshaped.columns.name = None

# Split the column into two
reshaped[['valence', 'arousal', 'strength']] = reshaped['valence_arousal_strength'].str.split(', ', expand=True)
reshaped[['like', 'familiar']] = reshaped['like_familiar'].str.split(', ', expand=True)

# Convert to numeric if needed
reshaped['valence'] = reshaped['valence'].astype(int)
reshaped['arousal'] = reshaped['arousal'].astype(int)
reshaped['strength'] = reshaped['strength'].astype(int)

reshaped = reshaped.drop(columns=['valence_arousal_strength'])
reshaped = reshaped.drop(columns=['like_familiar'])

#Remove duplicated users
cols = ["valence", "arousal", "strength", "like", "familiar"]
reshaped = reshaped.groupby("userID").filter(
    lambda x: (x[cols].nunique() != 1).any()
)
#reshaped.to_csv()

reshaped["stimulus"] = reshaped["stimulus"].replace("././songs/emotionAudio/trimmed_part2_mp3/", "", regex=False)

dir_out = "/Users/pdealcan/Documents/data/processed/stage2/"
reshaped.to_csv(f"{dir_out}processed_emotion_old.csv")

# Group by userID and startDateJATOS, count unique stimuli
print("Emotion 2 - old:")
print(reshaped.groupby("studyID")["userID"].nunique())
