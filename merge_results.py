import os
import sys
import pandas as pd



if __name__ == "__main__":
    base_folder_path = sys.argv[1]

    files = ["HB_result.csv", "HBRaceAnalysis_result.csv",
             "MAZ_result.csv", "MAZRaceAnalysis_result.csv",
             "SHB_result.csv", "SHBRaceAnalysis_result.csv"]
    
    dfs = {f: [] for f in files}
    all_folders = [os.path.join(base_folder_path, f) for f in os.listdir(base_folder_path)]

    for folder_path in all_folders:
        for f in files:
            df = pd.read_csv(os.path.join(folder_path, f))
            dfs[f].append(df)
    
    merged_results = {}
    for d in dfs:
        merged_results = pd.concat(dfs[d])
        merged_result_path = os.path.join(base_folder_path, d)
        merged_results.to_csv(merged_result_path, index=None)