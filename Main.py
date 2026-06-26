import pandas as pd
import numpy as np
import sqlite3 as sq
import matplotlib.pyplot as plt
import seaborn as sns
import kagglehub as kh
import os

# Download dataset and get the path
dataset_path = kh.dataset_download("patrickb1912/ipl-complete-dataset-20082020")

deliveries = pd.read_csv(os.path.join(dataset_path, "deliveries.csv"))
matches = pd.read_csv(os.path.join(dataset_path, "matches.csv"))
deliveries.columns=deliveries.columns.str.strip()
matches.columns=matches.columns.str.strip()

deliveries["match_id"]=deliveries["match_id"].astype("Int64")
deliveries["inning"]=deliveries["inning"].astype("Int32")

new_team_names={
    "Royal Challengers Bangalore" : "Royal Challengers Bengaluru",
    "Kings XI Punjab" : "Punjab Kings",
    "Delhi Daredevils" : "Delhi Capitals"
}
deliveries["batting_team"]=deliveries["batting_team"].replace(new_team_names)
deliveries["bowling_team"] = deliveries["bowling_team"].replace(new_team_names)

deliveries["over"]=deliveries["over"].astype("Int32")
deliveries["over"]=deliveries["over"]+1


deliveries["ball"] = deliveries["ball"].astype("Int32")
deliveries["is_legal_ball"] = ~deliveries["extras_type"].isin(["wides","no_balls"])
deliveries["is_batter_ball"] = deliveries["extras_type"] != "wides"


player_name = {
    "AB De Villiers": "AB de Villiers",
    "G Gambhir": "Gautam Gambhir",
    "V Sehwag": "Virender Sehwag",
    "RG Sharma": "Rohit Sharma",
    "MS Dhoni": "MS Dhoni",
    "SR Watson": "Shane Watson",
    "KH Pandya": "Krunal Pandya",
    "HH Pandya": "Hardik Pandya",
    "KA Pollard": "Kieron Pollard",
    "YK Pathan": "Yusuf Pathan",
    "IK Pathan": "Irfan Pathan",
    "DJ Bravo": "Dwayne Bravo",
    "PP Chawla": "Piyush Chawla",
    "A Mishra": "Amit Mishra",
    "R Ashwin": "Ravichandran Ashwin",
    "B Kumar": "Bhuvneshwar Kumar",
    "YS Chahal": "Yuzvendra Chahal",
    "JJ Bumrah": "Jasprit Bumrah",
    "UT Yadav": "Umesh Yadav"
}


for col in ["batter", "bowler", "non_striker", "player_dismissed"]:
    deliveries[col] = deliveries[col].replace(player_name).str.strip()


deliveries["total_runs"] = deliveries["batsman_runs"] + deliveries["extra_runs"]


deliveries["bowler_runs"] = np.where(
    deliveries["extras_type"].isin(["byes", "leg byes"]),
    0,
    deliveries["total_runs"]
)
bowlers_wicket_types=["bowled","caught","stumped","lbw","caught and bowled"]
deliveries["is_bowler_wicket"] = deliveries["dismissal_kind"].isin(bowlers_wicket_types)

deliveries["clean_batsman_runs"] = np.where(
    deliveries["extras_type"]=="wides",
    0,
    deliveries["batsman_runs"]
)


deliveries["bowlers_extra_runs"] = np.where(
    deliveries["extras_type"].isin(["wides","no_balls"]),
    deliveries["extra_runs"],
    0
)


deliveries["fielders_extras_runs"] = np.where(
    deliveries["extras_type"].isin(["leg byes", "byes"]), 
    deliveries["extra_runs"],
    0
)
deliveries["extras_types"] = deliveries["extras_type"].fillna("none").str.strip().str.lower()

deliveries["clean_fielder"] = np.where(
    deliveries["dismissal_kind"] == "caught and bowled",
    deliveries["bowler"],
    deliveries["fielder"]
)
 

output_excel_path = "deliveries_cleaned.xlsx"
deliveries.to_excel(output_excel_path, index=False)
 
print(f"DataFrame successfully exported to {output_excel_path}")
