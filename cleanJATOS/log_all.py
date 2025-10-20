import os
import json
import pandas as pd
from collections import defaultdict

path = "../../../../data/processed/final_features/"
path_out = "../../../../data/processed/logs/"
studies = os.listdir(path)

# Loop through all CSV files in the input directory
for filename in os.listdir(path):
    if filename.endswith(".csv"):
        file_path = os.path.join(f"{path}{filename}")
        df = pd.read_csv(file_path)
        participants = df.groupby("studyID")["userID"].unique()

        # Convert to dict with lists
        participants_dict = {study: users.tolist() for study, users in participants.items()}
        nOut = filename.replace(".csv", "")
        with open(f"{path_out}{nOut}.json", "w") as f:
            json.dump(participants_dict, f, indent=2)


# Data structures
study_per_battery = defaultdict(lambda: defaultdict(list))  # study_per_battery[battery][study] = [users]
all_users_per_battery = defaultdict(set)  # all_users_per_battery[battery] = set(users)
all_study_counts = defaultdict(set)  # all_study_counts[study] = set(users)
user_batteries = defaultdict(set)  # user_batteries[user] = set(batteries)
user_studies = defaultdict(set)  # user_batteries[user] = set(batteries)

# Read all JSON files
for file_name in os.listdir(path_out):
    if file_name.endswith(".json"):
        battery_name = file_name.replace(".json", "")
        with open(os.path.join(path_out, file_name)) as f:
            data = json.load(f)
            for study, users in data.items():
                study_per_battery[battery_name][study] = users
                all_users_per_battery[battery_name].update(users)
                all_study_counts[study].update(users)
                for user in users:
                    user = str(user).strip()  # convert everything to string
                    user_batteries[user].add(battery_name)

# 1 Participants per studyID per battery
rows = []
for battery, studies in study_per_battery.items():
    for study, users in studies.items():
        rows.append({"Battery": battery, "StudyID": study, "Participants": len(users)})
df_study_per_battery = pd.DataFrame(rows)
df_study_per_battery.to_csv(f"{path_out}study_per_battery.csv", index=False)

# 2 Participants per battery (total per battery)
rows = [{"Battery": battery, "TotalParticipants": len(users)} for battery, users in all_users_per_battery.items()]
df_total_per_battery = pd.DataFrame(rows)
df_total_per_battery.to_csv(f"{path_out}total_per_battery.csv", index=False)

# 3 Participants per studyID (total across batteries)
#rows = [{"StudyID": study, "TotalParticipants": len(users)} for study, users in all_study_counts.items()]
rows = [{"StudyID": study, "TotalParticipants": len(users), "participants": users} for study, users in all_study_counts.items()]
df_total_per_study = pd.DataFrame(rows)
df_total_per_study.to_csv(f"{path_out}total_per_study.csv", index=False)

# 4 Batteries each user participated in
rows = [{"UserID": user, "Batteries": ", ".join(sorted(batteries))} for user, batteries in user_batteries.items()]
df_user_batteries = pd.DataFrame(rows)
df_user_batteries.to_csv(f"{path_out}user_batteries.csv", index=False)

# 5 Participants per studyID per battery
for battery, studies in study_per_battery.items():
    for study, users in studies.items():
        for user in users:
            user_studies[user].add(study)

rows = [{ "UserID": user.lower().strip(), "Batteries": ", ".join(sorted(user_batteries[user])), "Studies": ", ".join(sorted(user_studies[user])) } for user in user_batteries ]
df_user_batteries = pd.DataFrame(rows)
df_user_batteries.to_csv(f"{path_out}user_batteries_studies.csv", index=False)

df_m12 = df_user_batteries[df_user_batteries["Studies"].str.contains("m12", na=False)]
df_m12.to_csv(f"{path_out}m12.csv", index=False)
print("All CSV files have been saved!")
