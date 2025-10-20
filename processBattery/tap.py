import pandas as pd
import numpy as np

def expand_rt(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Normalize: replace empty fields (NaN or "") with empty lists
    df["rt"] = df["rt"].apply(
        lambda x: [] if (pd.isna(x) or x == "" or x == []) else x
    )

    # first ensure both rt and rtAudio are lists (not strings)
    df["rt"] = df["rt"].apply(lambda x: eval(x) if isinstance(x, str) else x)
    df["rtAudio"] = df["rtAudio"].apply(lambda x: eval(x) if isinstance(x, str) else x)

    # convert them into list of tuples so they explode together
    df["rt_tuple"] = df.apply(lambda row: list(zip(row["rt"], row["rtAudio"])), axis=1)

    # explode that column
    df = df.explode("rt_tuple").reset_index(drop=True)

    # split back into separate columns
    df[["rt", "rtAudio"]] = pd.DataFrame(df["rt_tuple"].tolist(), index=df.index)

    # drop the helper column
    df = df.drop(columns=["rt_tuple"])
    return df

data = pd.read_csv("/Users/pdealcan/Documents/data/processed/stage1/tapping.csv")
data["stimulus"] = data["stimulus"].str.replace("./songs/movementTapAudio/", "", regex=False)
data["stimulus"] = data["stimulus"].str.replace("modifiedAudio/", "", regex=False)
data["stimulus"] = data["stimulus"].str.replace(".wav", "", regex=False)

#Check missed studyIDs
#unique_combos = data[["studyID", "uniqueID", "userID", "user", "userIDAlicia"]].drop_duplicates()
#unique_combos.to_csv("test.csv")
#print(unique_combos)

data = data[data["rt"].str.contains(r"[\[\]]", regex=True, na=False)]
out = ["test", "c4fec400-39ad-4081-84a1-2035dc437f8d", "9f3eba1a-677f-4378-b7ae-c0bf3089fe9e", "test3", "participantpractice2", "participantTEST"]
data = expand_rt(data)

colsInterest = ['rt', 'stimulus', 'response','trial_index', 'userID', 'lang', 'sequenceTrials', 'studyID', 'rtAudio', 'startDateJATOS', 'endDateJATOS']
data = data[colsInterest]

dir_out = "/Users/pdealcan/Documents/data/processed/stage2/"
data.to_csv(f"{dir_out}tapping.csv")

print("Tap:")
print(data.groupby("studyID")["userID"].nunique())

