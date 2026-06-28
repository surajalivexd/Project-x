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
# cleaning matches 
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

#Analyzing 

conn = sq.connect("ipl.db")
deliveries.to_sql("deliveries", conn, if_exists="replace", index=False)
matches.to_sql("matches", conn, if_exists="replace", index=False)
# TOP 10 RUN SCORERS OF ALL TIME (with Strike Rate)
query1 = """
SELECT
    batter,
    SUM(clean_batsman_runs) AS runs_scored,
    (SUM(clean_batsman_runs) * 100.0 / SUM(is_batter_ball)) AS strike_rate
FROM deliveries
GROUP BY batter
ORDER BY runs_scored DESC
LIMIT 10;
"""
top_10_scorers =  pd.read_sql_query(query1, conn)
print("--- Top 10 Run Scorers (with Strike Rate) ---")
print(top_10_scorers)


# BEST BOWLER BY ECONOMY (MIN 50 OVERS)
query2 = """
SELECT
    bowler,
    SUM(bowler_runs) AS runs_conceded,
    SUM(is_legal_ball) AS balls_bowled,
    (SUM(bowler_runs) * 6.0 / SUM(is_legal_ball)) AS economy
FROM deliveries
GROUP BY bowler
HAVING balls_bowled >= 300 
ORDER BY economy ASC
LIMIT 10;
"""
top_10_economical_bowlers = pd.read_sql_query(query2, conn)
print("\n--- Top 10 Most Economical Bowlers (min. 50 overs) ---")
print(top_10_economical_bowlers)

# TOP 10 WICKET TAKERS OF ALL TIME
query3 =  """
SELECT
    bowler,
    SUM(is_bowler_wicket) AS wickets,
    (SUM(bowler_runs) * 6.0 / SUM(is_legal_ball)) AS economy
FROM deliveries
GROUP BY bowler
ORDER BY wickets DESC
limit 10;
"""
top_10_wicket_takers = pd.read_sql_query(query3, conn)
print("\n--- Top 10 Wicket Takers (with Economy) ---")
print(top_10_wicket_takers)

# HIGH SCORING VENUES
query4 ="""
select venue , avg(target_runs) as  avg_innings_score
from matches 
group by venue
order by avg_innings_score desc
limit 10;"""
high_scoring_venues = pd.read_sql_query(query4, conn)
print("\n--- High Scoring Venues ---")
print(high_scoring_venues)

# TOP DEATH OVER BATSMAN
query5 ="""
SELECT
    batter,
    SUM(clean_batsman_runs) AS runs,
    (SUM(clean_batsman_runs) * 100.0 / SUM(is_batter_ball)) AS strike_rate,
    SUM(is_batter_ball) as balls_faced
FROM deliveries
WHERE over >= 15 AND over <= 20 
GROUP BY batter
HAVING balls_faced >= 100 
ORDER BY strike_rate DESC
LIMIT 10;
"""
top_death_over_batsman = pd.read_sql_query(query5, conn)
print("\n--- Top 10 Death Over Batsmen (min. 100 balls) ---")
print(top_death_over_batsman)

# MOST VALUABLE PLAYER
query6="""
SELECT
    player_of_match,
    COUNT(*) AS awards_count
FROM matches
WHERE player_of_match != 'Not Available'
GROUP BY player_of_match
ORDER BY awards_count DESC
LIMIT 10;
"""
most_valuable_player = pd.read_sql_query(query6, conn)
print("\n--- Top 10 'Player of the Match' Award Winners ---")
print(most_valuable_player)

# BEST TEAM OF ALL TIME (BY WINS%)
query7="""
WITH
    games_played AS (
        SELECT team, COUNT(*) AS total_games
        FROM (
            SELECT team1 AS team FROM matches WHERE result != 'no result'
            UNION ALL
            SELECT team2 AS team FROM matches WHERE result != 'no result'
        )
        GROUP BY team
    ),
    games_won AS (
        SELECT winner, COUNT(*) AS total_wins
        FROM matches
        WHERE winner != 'No Result'
        GROUP BY winner
    )
SELECT
    gp.team,
    (gw.total_wins * 100.0 / gp.total_games) AS win_percentage
FROM games_played AS gp
JOIN games_won AS gw ON gp.team = gw.winner
ORDER BY win_percentage DESC
LIMIT 10;
"""
best_team_of_all_time = pd.read_sql_query(query7, conn) 
print("\n--- Best Team of All Time (by Wins%) ---")
print(best_team_of_all_time)
conn.close()