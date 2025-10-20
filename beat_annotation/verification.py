import os
import pandas as pd

# Define folder paths
beat_times_folder = "beat_times"
tempo_changes_folder = "tempoChanges"

# Get lists of files
beat_files = sorted([f for f in os.listdir(beat_times_folder) if f.endswith(".txt")])
tempo_files = sorted([f for f in os.listdir(tempo_changes_folder) if f.endswith(".txt")])

# --- 1. Check if both folders have the same number of files ---
if len(beat_files) != len(tempo_files):
    print(f"❌ Mismatch in file count: {len(beat_files)} in beat_times vs {len(tempo_files)} in tempo_changes")
else:
    print(f"✔ Both folders have {len(beat_files)} files")

# --- 2. Check for matching filenames ---
missing_in_tempo = set(beat_files) - set(tempo_files)
missing_in_beat = set(tempo_files) - set(beat_files)

if missing_in_tempo:
    print(f"❌ Missing in tempo_changes: {missing_in_tempo}")
if missing_in_beat:
    print(f"❌ Missing in beat_times: {missing_in_beat}")
if not missing_in_tempo and not missing_in_beat:
    print("✔ All filenames match")

# --- 3. Check TXT (CSV) content rules + TIME differences ---
for fname in beat_files:
    beat_path = os.path.join(beat_times_folder, fname)
    tempo_path = os.path.join(tempo_changes_folder, fname)

    if not os.path.exists(tempo_path):
        continue  # skip if no corresponding file

    # Function to check TIME differences
    def check_time_diffs(df, file_label):
        if "TIME" in df.columns:
            diffs = df["TIME"].diff().dropna()
            bad_diffs = diffs[diffs < 0.2]
            if not bad_diffs.empty:
                print(f"❌ {fname} in {file_label} has {len(bad_diffs)} intervals < 0.2 sec") #0.2 because that corresponds to 300bpm
                # Print the row indices and values where it occurred
                for idx in bad_diffs.index:
                    print(f"   Row {idx-1} -> {idx}: {df['TIME'].iloc[idx-1]} -> {df['TIME'].iloc[idx]} (diff={bad_diffs.loc[idx]})")

    # Check beat_times file
    try:
        beat_df = pd.read_csv(beat_path)
        duplicates = beat_df[beat_df.duplicated(subset="TIME", keep=False)]
        if not duplicates.empty:
            print(f"✔ Cleaned duplicate TIME values in {beat_path}")
            beat_df = beat_df.drop_duplicates(subset="TIME", keep="first")
            beat_df.to_csv(beat_path, index=False)
            print(f"✔ Cleaned duplicate TIME values in {beat_path}")
        if len(beat_df) <= 2:
            print(f"❌ {fname} in beat_times has {len(beat_df)} data rows (needs > 2)")
        check_time_diffs(beat_df, "beat_times")
    except Exception as e:
        print(f"⚠ Error reading {beat_path}: {e}")

    # Check tempo_changes file
    try:
        tempo_df = pd.read_csv(tempo_path)
        if len(tempo_df) != 2:
            print(f"❌ {fname} in tempo_changes has {len(tempo_df)} data rows (needs exactly 2)")
        check_time_diffs(tempo_df, "tempo_changes")
    except Exception as e:
        print(f"⚠ Error reading {tempo_path}: {e}")

print("✔ No duplicate beats")
print("✅ Verification complete")
