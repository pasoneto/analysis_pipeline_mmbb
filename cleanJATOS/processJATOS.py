import os
import json
import pandas as pd
import numpy as np

def read_folders(inPath, battery):
    p1 = f"{inPath}/{battery}"
    folders = os.listdir(p1)
    folders = [f for f in os.listdir(p1) if f != ".DS_Store"]
    folders.remove("metadata.json")
    study_result = [x. replace("study_result_", "") for x in folders]
    folders = [f"{p1}/{x}" for x in folders]
    sub_folders = [[f for f in os.listdir(x) if f != ".DS_Store"] for x in folders]
    comp_result = [os.listdir(f"{y}/{x[0]}")[0].replace("comp_result_", "") for x, y in zip(sub_folders, folders)]
    assert len(folders) == len(sub_folders), "Unequal number of folders"
    assert len(study_result) == len(comp_result), "Unequal number of results"
    final_paths = [f"{x}/{y[0]}/data.txt" for x, y in zip(folders, sub_folders)]
    return [study_result, comp_result, final_paths]

def read_file(study_result, comp_result, file):
    with open(file) as f:
        a = json.load(f)
        a = pd.DataFrame.from_dict(a["trials"])
        a["study_result"] = study_result
        a["comp_result"] = comp_result
    return a

def read_metadata(inPath, battery):
    p1 = f"{inPath}/{battery}/metadata.json"
    with open(p1) as f:
        a = json.load(f)
        a = pd.concat([pd.DataFrame.from_dict(x["studyResults"]) for x in a["data"]])
        urlPar = pd.json_normalize(a["urlQueryParameters"])
        #urlPar = urlPar.rename(columns={"studyID": "studyID_backup"})
        a = a.join(urlPar)
        a = a.rename(columns={"startDate": "startDateJATOS", "endDate": "endDateJATOS"})
    return a

def read_all_results(inPath, battery):
    study_result, comp_result, all_files = read_folders(inPath, battery)
    file = [read_file(x, y, z) for x, y, z in zip(study_result, comp_result, all_files)]
    file = pd.concat(file)
    return file

def add_metadata_to_results(all_results, metadata):
    all_results["study_result"] = all_results["study_result"].astype("int32")
    metadata["id"] = metadata["id"].astype("int32")
    #print(f"Checkpoint 0: {len(np.unique(metadata[metadata['studyID'] == 'm12']['user']))}")
    #print(f"Checkpoint 1: {len(np.unique(all_results[all_results['studyID'] == 'm12']['userID']))}")
    metadata[metadata['studyID'] == 'm12'].to_csv("./metadata.csv")
    all_results[all_results['studyID'] == 'm12'].to_csv("./all_results.csv")
    all_results = all_results.merge(metadata, left_on="study_result", right_on="id")
    all_results.drop(columns=["id"], inplace = True)
    #print(f"Checkpoint 2: {len(np.unique(all_results[all_results['studyID_x'] == 'm12']['userID']))}")
    return all_results

def merge_xy_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df.replace("", np.nan)
    x_cols = [col for col in df.columns if col.endswith("_x")]
    for x_col in x_cols:
        root = x_col[:-2]  # remove _x
        y_col = root + "_y"
        if y_col not in df.columns: 
            continue  # skip if no pair
        x = df[x_col]
        y = df[y_col]
        conflict_mask = x.notna() & y.notna() & (x != y)
        if conflict_mask.any() and root != "part": #It is ok if column is part, because it changes depending on the order of tasks done
            raise ValueError(
                f"Conflict found in columns {x_col} and {y_col} at rows {df.index[conflict_mask].tolist()}"
            )
        df[x_col] = x.fillna(y)
        df = df.drop(columns=[y_col])
        df = df.rename(columns={x_col: root})
    #print(f"Checkpoint 3: {len(np.unique(df[df['studyID'] == 'm12']['userID']))}")
    return df

#Lukilapsi
def is_valid_id(s) -> bool:
    s = str(s)
    return s.isdigit() or s == 'testPilot01'

def tag_lostID(df: pd.DataFrame) -> pd.DataFrame:
    if "uniqueID" in df.columns:
        df.loc[df["uniqueID"].apply(is_valid_id), "userID"] = df["uniqueID"]
    return df

def process_all(inPath, battery, outPath):
    all_results = read_all_results(inPath, battery)
    print("Finished reading all files")
    metadata = read_metadata(inPath, battery)
    print("Added metadata info")
    data = add_metadata_to_results(all_results, metadata)
    data = merge_xy_columns(data)
    data = tag_lostID(data)
    print("Double checked studyID and userID data")
    data.to_csv(f"{outPath}{battery}.csv")
    print(f"Successfully written {battery} to {outPath}")
   
inPath = "../../../../data/raw"
outPath = "../../../../data/processed/stage1/"
all_studies = [f for f in os.listdir(inPath) if os.path.isdir(os.path.join(inPath, f))]
for battery in all_studies:
    print(f"########## {battery} #############")
    process_all(inPath, battery, outPath)
