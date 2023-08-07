# -*- coding: utf-8 -*-
"""
Meant to write simple, quick .txt files containing post-game pitching stats.

Designed to be generated with Trackman data, but column/variable names can be edited
in order to accomadate other software.

Created on Sat Jul 29 17:46:44 2023

@author: Carolyn Angelillo / https://www.linkedin.com/in/carolynangelillo/
"""
import pandas as pd

trackman = pd.read_csv(r"Insert Your CSV Here!")

"""First, the CSV is filtered to include only your team data"""
pitcher_filter = trackman["PitcherTeam"] == "TEAM_CODE"
trackman = trackman[pitcher_filter]

pitchers = list(set(trackman["Pitcher"].tolist()))
date = trackman["Date"].tolist()[0]

"""
Next, new columns/variables are added to the Trackman CSV as follows:
    
    TotalBallStrikes: Marks every pitch as either a ball or strike.
    
    OutsGained: Total outs gained from every pitch, whether by a strikeout
                 or a fielding out.
    
    ProductiveStrikes: Any strike that does not result in an hit.
"""
    
total_b_s = []

for row in trackman["PitchCall"]:
    if row == ("BallCalled"):
        total_b_s.append("Ball")
    elif row == ("HitByPitch"):
        total_b_s.append("Ball")
    elif row == ("BallinDirt"):
        total_b_s.append("Ball")
    else:
        total_b_s.append("Strike")
trackman["TotalBallStrikes"] = total_b_s

outs_gained = []
strikeouts = trackman["KorBB"].tolist()
pitcher_outs = []
field_outs = trackman["OutsOnPlay"].tolist()
for play in strikeouts:
    if play == "Strikeout":
        pitcher_outs.append(1)
    else:
        pitcher_outs.append(0)
for z in range(0, len(strikeouts)):
    outs_gained.append(pitcher_outs[z] + field_outs[z])
trackman["OutsGained"] = outs_gained

productive_strikes = []
pitch_calls = trackman["PitchCall"].tolist()
outs_on_play = trackman["OutsOnPlay"].tolist()
hit_type = trackman["TaggedHitType"].tolist()
for x in range(0, len(total_b_s)):
    if total_b_s[x] == "Strike":
        if pitch_calls[x] == "StrikeCalled":
            productive_strikes.append(True)
        elif pitch_calls[x] == "StrikeSwinging":
            productive_strikes.append(True)
        elif pitch_calls[x] == "FoulBall":
            productive_strikes.append(True)
        elif pitch_calls[x] == "InPlay":
            if outs_on_play[x] != 0:
                productive_strikes.append(True)
            else:
                productive_strikes.append(False)
        else:
            productive_strikes.append(False)
    else:
        productive_strikes.append(False)
trackman["ProductiveStrikes"] = productive_strikes

"""
The CSV is then filtered by each individual pitcher.

The stats for each pitcher will be written into an unique
.txt file labeled with the pitcher's name and game date.
"""
for pitcher in pitchers:
    cpf = trackman["Pitcher"] == pitcher
    cur_pitcher = trackman[cpf]
    filename = date + " " + pitcher
    pitcher_report = open(filename + ".txt", "w")
    pitcher_report.write(f"{date} Pitching Report for: {pitcher} ")
    pitcher_report.writelines(["\n", "\n"])
    pitcher_report.write("PITCH TYPE STATISTICS")
    all_pitches = cur_pitcher["TaggedPitchType"].tolist()
    total_pitches = len(all_pitches)
    pitch_types = list(set(all_pitches))
    
    """
    CSV is filtered by pitch type to calculate seperate stats for 
    each pitch a pitcher throws.
    """
    for type in pitch_types:
        pitch_filter = cur_pitcher["TaggedPitchType"] == type
        cur_pitch = cur_pitcher[pitch_filter]
        pitcher_report.writelines(["\n", "\n"])
        pitcher_report.write(type.upper() + ": \n")
        total = len(cur_pitch["TaggedPitchType"].tolist())
        usage = total / total_pitches
        avg_velo = sum(cur_pitch["RelSpeed"].tolist()) / total
        avg_spinrate = sum(cur_pitch["SpinRate"].tolist()) / total
        avg_extension = sum(cur_pitch["Extension"].tolist()) / total
        avg_rh = sum(cur_pitch["RelHeight"].tolist()) / total
        max_velo = max(cur_pitch["RelSpeed"].tolist())
        pitch_stats = [(f"Total: {total} \n"),
                       (f"Usage: {usage:.2f} \n"),
                 (f"Average Velo: {avg_velo:.2f} \n"),
                 (f"Max Velo: {max_velo:.2f} \n"),
                 (f"Average Spin Rate: {avg_spinrate:.2f} \n"),
                 (f"Average Extension: {avg_extension:.2f} \n"),
                 (f"Average Release Height: {avg_rh:.2f} \n"),
                 ]
        pitcher_report.writelines(pitch_stats)
        strike_count = cur_pitch["TotalBallStrikes"].tolist().count("Strike")
        pro_strike_count = cur_pitch["ProductiveStrikes"].tolist().count(True)
        strike_per = strike_count / total
        pro_strike_per = pro_strike_count / total
        pitcher_report.writelines([f"Strike Percentage: {strike_per:.2f} \n",
                                   f"Productive Strike Percentage: {pro_strike_per:.2f} \n"])
    
    "The CSV is filtered by inning to determine IP."
    innings_in_play = list(set(cur_pitcher["Inning"].tolist()))
    innings_pitched = 0
    for inning in innings_in_play:
        inning_filter = cur_pitcher["Inning"] == inning
        cur_inning = cur_pitcher[inning_filter]
        outs_on_inning = sum(cur_inning["OutsGained"].tolist())
        if outs_on_inning == 3:
            innings_pitched += 1
        elif outs_on_inning == 2:
            innings_pitched += 0.2
        elif outs_on_inning == 1:
            innings_pitched += 0.1
        else:
            innings_pitched += 0
    
    "Finally, full game stats are calculated for each pitcher."
    pitcher_report.writelines(["\n", "FULL GAME STATS", "\n"])
    total_strikes = cur_pitcher["TotalBallStrikes"].tolist().count("Strike")
    total_balls = cur_pitcher["TotalBallStrikes"].tolist().count("Ball")
    total_walks = cur_pitcher["KorBB"].tolist().count("Walk")
    total_strikeouts = cur_pitcher["KorBB"].tolist().count("Strikeout")
    k_per_nine = (total_strikeouts / innings_pitched) * 9
    bb_per_nine = (total_walks / innings_pitched) * 9
    all_hits = cur_pitcher["TaggedHitType"].tolist()
    outs = cur_pitcher["OutsOnPlay"].tolist()
    hits = 0
    for y in range(0, len(all_hits)):
        if all_hits[y] != "Undefined":
            if outs[y] == 0:
                hits += 1
    whip = (total_walks + hits) / innings_pitched
    
    game_stats = [f"Innings Pitched: {innings_pitched} \n",
                  f"Total Strikes: {total_strikes} \n",
                  f"Total Balls: {total_balls} \n",
                  f"Total Hits: {hits} \n",
                  f"Total Strikeouts: {total_strikeouts} \n",
                  f"Total Walks: {total_walks} \n",
                  f"K's Per Nine: {k_per_nine:.2f} \n",
                  f"BB's Per Nine: {bb_per_nine:.2f} \n",
                  f"WHIP: {whip:.2f} \n",
                  "\n"]     
    pitcher_report.writelines(game_stats)
    pitcher_report.write("End")