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
    "Delhi Daredevils" : "Delhi Capitals",
    "Rising Pune Supergiants": "Rising Pune Supergiant",
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

#ANALYZING 

matches.rename(columns={"id": "match_id"}, inplace=True)
matches["date"] = pd.to_datetime(matches["date"])
matches["season"] = matches["date"].dt.year
matches["player_of_match"] = matches["player_of_match"].replace(player_name).str.strip()
city_name = {
    "Bangalore": "Bengaluru",
    "Delhi": "New Delhi",
    "Visakhapatnam":"Vizag"
}
venue={
    "Feroz Shah Kotla" : "Arun Jaitley Stadium",
    "Sardar Patel Stadium, Motera" : "Narendra Modi Stadium",
    "Punjab Cricket Association Stadium, Mohali" : "Punjab Cricket Association Stadium",
    "Subrata Roy Sahara Stadium" : "Maharashtra Cricket Association Stadium (Pune)"
}
matches['city'] = matches["city"].replace(city_name).str.strip()
matches.loc[matches["venue"]=="Sharjah Cricket Stadium","city"] = "Dubai"
matches.loc[matches["venue"]=="Dubai International Cricket Stadium","city"] = "Dubai"
matches["venue"] = matches["venue"].replace(venue).str.strip()
matches["team1"] = matches["team1"].replace(new_team_names).str.strip()
matches["team2"] = matches["team2"].replace(new_team_names).str.strip()
matches["toss_winner"] = matches["toss_winner"].replace(new_team_names).str.strip()
matches["winner"]=matches["winner"].replace(new_team_names).str.strip()
matches["city"].fillna("Not Available", inplace=True)
matches["winner"].fillna("No Result",inplace=True)
matches["player_of_match"].fillna("Not Available",inplace=True)
matches.loc[matches["result"] == "tie","result_margin"] = 0
matches["result_margin"].fillna(0,inplace=True)
matches["target_runs"] .fillna(0,inplace=True)
matches["target_overs"].fillna(0,inplace=True)


print(matches.isna().sum())