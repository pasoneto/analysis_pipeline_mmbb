import pandas as pd
import numpy as np
import os

# Load files
files = os.listdir("./beat_times/")

def calculateTempo(file_name):
    file1 = pd.read_csv(f"./beat_times/{file_name}")  # Column 'TIME' in seconds
    file2 = pd.read_csv(f"./tempoChanges/{file_name}")  # Column 'TIME' in seconds

    times1 = file1['TIME']
    boundaries = file2['TIME'].tolist()

    # Add -inf at start and +inf at end to include all values
    bins = [-np.inf] + boundaries + [np.inf]

    # Segment the times
    labels = range(1, len(bins))  # Segment labels 1,2,3,...
    file1['segment'] = pd.cut(times1, bins=bins, labels=labels)

    # Compute median difference and convert to BPM
    bpm_per_segment = file1.groupby('segment')['TIME'].apply(
        lambda x: 60 / x.diff().median() if not x.diff().dropna().empty else np.nan
    )

    bpm_per_segment.to_csv(f"./bpms/{file_name}") 

[calculateTempo(x) for x in files]
