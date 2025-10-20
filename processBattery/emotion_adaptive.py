import pandas as pd
import numpy as np
import sys

data = pd.read_csv("/Users/pdealcan/Documents/data/processed/stage1/emotion_adaptive.csv")

data = data[~data["Theta"].isna()][["studyID", "userID", "startDateJATOS", "Theta", "Theta_idx", "trial_index"]]
data = data.sort_values(by=["studyID", "userID"])

data = data.loc[
    data.groupby(["userID", "studyID", "startDateJATOS"])["trial_index"].transform("max") == data["trial_index"]
]
data = data.reset_index(drop=True)
data = data.sort_values(by=["studyID", "userID", "startDateJATOS"])

data = data.drop_duplicates(subset=["userID", "studyID"], keep="first")

data = data.rename(columns={'Theta': 'score'})

data["questionnaire"] = "emotion"
data["sub_item"] = "adaptive"

colsInterest = ["userID", "studyID", "sub_item", "questionnaire", "score"]
data = data[colsInterest]

data.to_csv("/Users/pdealcan/Documents/data/processed/final_features/emotion_adaptive.csv")

