import pandas as pd
import numpy as np

data = pd.read_csv("/Users/pdealcan/Documents/data/processed/stage1/rhythm.csv")

data["batSong"] = data["batSong"].str.replace("./songs/movementTapAudio/", "", regex=False)
data["batSong"] = data["batSong"].str.replace("modifiedAudio/", "", regex=False)
data["batSong"] = data["batSong"].str.replace(".wav", "", regex=False)
data = data[data["batSong"] != ""]
data = data.dropna(subset=['batSong', 'offset'])
data["batSong"] = data["batSong"].str.split("/").str[-1]
colsInterest = ['batSong', 'tIndex', 'response', 'studyID', 'offset', 'nChanges', 'initialOffset', 'startDateJATOS', 'endDateJATOS', 'userID']
data = data[colsInterest]
data = data.sort_values(["studyID", "userID", "tIndex"]).reset_index(drop=True)

print("BAT:")
print(data.groupby("studyID")["userID"].nunique())

dir_out = "/Users/pdealcan/Documents/data/processed/stage2/"
data.to_csv(f"{dir_out}bat.csv")
