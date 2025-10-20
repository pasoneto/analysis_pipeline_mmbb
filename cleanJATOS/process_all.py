import os
import subprocess
from tqdm import tqdm

folder_path = "../processBattery/"

# Loop through all .py files in the folder
fs = os.listdir(folder_path)
for file_name in tqdm(fs):
    if file_name.endswith(".py"):
        file_path = os.path.join(folder_path, file_name)
        print(f"Running {file_path}...")
        subprocess.run(["python3", file_path], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"Study processed correctly ✅")

print(f"Running log calculations...")
#subprocess.run(["python3", "./log_all.py"], check=True)
#print(f"All studies logged ✅")
