import os
import sys
import pandas as pd


if __name__ == "__main__":
    folder_path = sys.argv[1]

    table2_output_path = os.path.join(folder_path, "table2.csv")

    analyses_meta = {
                     "HB": ("HB_result.csv", "HBVectorClockNoRace", "HBTreeClockNoRace"),
                     "HBRaceAnalysis": ("HBRaceAnalysis_result.csv", "HBVectorClockRaceAnalysis", "HBTreeClockRaceAnalysis"),
                     "SHB": ("SHB_result.csv", "SHBVectorClockNoRace", "SHBTreeClockNoRace"),
                     "SHBRaceAnalysis": ("SHBRaceAnalysis_result.csv", "SHBVectorClockRaceAnalysis", "SHBTreeClockRaceAnalysis"),
                     "MAZ": ("MAZ_result.csv", "MAZVectorClockNoRace", "MAZTreeClockNoRace"),
                     "MAZRaceAnalysis": ("MAZRaceAnalysis_result.csv", "MAZVectorClockRaceAnalysis", "MAZTreeClockRaceAnalysis") 
                    }
    
    table2 = {}

    for a in analyses_meta:
        filename, vc_alg, tc_alg = analyses_meta[a]
        file_path = os.path.join(folder_path, filename)

        df = pd.read_csv(file_path)

        vc_avgs = df[df["algorithm"] == vc_alg].groupby(["benchmark"]).mean()["average_total_time"]
        tc_avgs = df[df["algorithm"] == tc_alg].groupby(["benchmark"]).mean()["average_total_time"]

        table2[a] = (vc_avgs / tc_avgs).mean()

    table2_df = pd.DataFrame(columns=analyses_meta.keys())
    table2_df = table2_df.append(table2, ignore_index=True)
    table2_df.to_csv(table2_output_path, index=None)