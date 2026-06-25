import pandas as pd
import numpy as np
import sqlite3 as sq
import matplotlib as plt
import matplotlib.pyplot as plt
import seaborn as sns
import kagglehub as kh

path = kh.dataset_download("patrickb1912/ipl-complete-dataset-20082020")
deliveries=pd.read_csv(r"C:\Users\suraj\.cache\kagglehub\datasets\patrickb1912\ipl-complete-dataset-20082020\versions\3\deliveries.csv")
matches = pd.read_csv(r"C:\Users\suraj\.cache\kagglehub\datasets\patrickb1912\ipl-complete-dataset-20082020\versions\3\matches.csv")
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



deliveries["ball"].astype("Int32")
deliveries["is_legal_ball"] = ~deliveries["extras_type"].isin(["wides","no_balls"])
deliveries["is_batter_ball"] = deliveries["extras_type"] != "wides"


print(deliveries.columns.to_list())
player_name = {
    "AB De Villiers": "AB de Villiers",
    "G Gambhir": "Gautam Gambhir",
    "V Sehwag": "Virender Sehwag",
    "RG Sharma": "Rohit Sharma",
    "MS Dhoni": "MS Dhoni",  
    "KH Pandya": "Krunal Pandya",
    "HH Pandya": "Hardik Pandya"
}
deliveries["batter"] = deliveries["batter"].replace(player_name).str.strip()
deliveries["non_striker"] = deliveries["non_striker"].replace(player_name).str.strip()
for col in ["batter","bowler","non_striker"]:
    deliveries[col]=deliveries[col].astype(str).str.strip()

