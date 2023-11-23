import pandas as pd
import numpy as np
import glob
from tqdm import tqdm as tqdm
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt
import math
import warnings
import requests
import json
import os
warnings.simplefilter("ignore")


# generate pcsp file
def generate_pcsp(params, date, ply1_name, ply2_name, hand1, hand2):
    VAR = 'var.txt'
    HAND = '%s_%s.txt' % (hand1, hand2)
    file_name = '%s_%s_' % (hand1, hand2)
    file_name += '%s_%s_%s.pcsp' % (date, ply1_name.replace(' ', '-'), ply2_name.replace(' ', '-'))

    # Create the folder if it doesn't exist
    os.makedirs("pcsp_files", exist_ok=True)

    # Update the file_name to include the folder path
    file_path = os.path.join("pcsp_files", file_name)

    # write to file
    lines = []
    with open(VAR) as f:
        lines_1 = f.readlines()
    lines_2 = []
    for i, p in enumerate(params):
        lines_2.append('#define p%d %d;\n' % (i, p))
    with open(HAND) as f:
        lines_3 = f.readlines()
    lines = lines_1 + lines_2 + lines_3
    with open(file_path, 'w') as f:
        for line in lines:
            f.write(line)


# obtain parameters
def get_params(df, hand):
    # Serve
    De_Serve = df.query('shot_type==1 and from_which_court==1')
    De_Serve_2nd = df.query('shot_type==2 and from_which_court==1')
    Ad_Serve = df.query('shot_type==1 and from_which_court==3')
    Ad_Serve_2nd = df.query('shot_type==2 and from_which_court==3')
    # Return
    De_ForeHandR = df.query('shot_type==3 and prev_shot_from_which_court==1 and shot<=20')
    Ad_ForeHandR = df.query('shot_type==3 and prev_shot_from_which_court==3 and shot<=20')
    De_BackHandR = df.query('shot_type==3 and prev_shot_from_which_court==1 and shot<=40 and shot>20')
    Ad_BackHandR = df.query('shot_type==3 and prev_shot_from_which_court==3 and shot<=40 and shot>20')
    # Stroke
    De_Stroke = df.query('shot_type==4 and from_which_court==1')
    Mid_Stroke = df.query('shot_type==4 and from_which_court==2')
    Ad_Stroke = df.query('shot_type==4 and from_which_court==3')

    results = []
    # Serve
    for Serve in [De_Serve, De_Serve_2nd, Ad_Serve, Ad_Serve_2nd]:
        ServeT = Serve.query('direction==6')
        ServeB = Serve.query('direction==5')
        ServeW = Serve.query('direction==4')
        serve_in = [len(x.query('shot_outcome==7')) for x in [ServeT, ServeB, ServeW]]
        serve_win = [len(Serve.query('shot_outcome in [1, 5, 6]'))]
        serve_err = [len(Serve.query('shot_outcome in [2, 3, 4]'))]
        results.append(serve_in + serve_win + serve_err)

    # Return
    if hand == 'RH':  # RH
        directions = [[[[1], [1]], [[1], [3]], [[1], [2]]],                    # FH_[CC, DL, DM]
                      [[[2, 3], [3]], [[3], [1]], [[2], [1]], [[2, 3], [2]]],  # FH_[IO, II, CC, DM]
                      [[[2], [3]], [[1], [3]], [[1, 2], [1]], [[1, 2], [2]]],  # BH_[CC, II, IO, DM]
                      [[[3], [3]], [[3], [1]], [[3], [2]]]]                    # BH_[CC, DL, DM]
    else:  # LH
        directions = [[[[1, 2], [1]], [[1], [3]], [[2], [3]], [[1, 2], [2]]],  # FH_[IO, II, CC, DM]
                      [[[3], [3]], [[3], [1]], [[3], [2]]],                    # FH_[CC, DL, DM]
                      [[[1], [1]], [[1], [3]], [[1], [2]]],                    # BH_[CC, DL, DM]
                      [[[2], [1]], [[3], [1]], [[2, 3], [3]], [[2, 3], [2]]]]  # BH_[CC, II, IO, DM]
    for i, Return in enumerate([De_ForeHandR, Ad_ForeHandR, De_BackHandR, Ad_BackHandR]):
        shots = [Return.query('from_which_court in @dir[0] and to_which_court in @dir[1]') for dir in directions[i]]
        return_in = [len(x.query('shot_outcome==7')) for x in shots]
        return_win = [len(Return.query('shot_outcome in [1, 5, 6]'))]
        return_err = [len(Return.query('shot_outcome in [2, 3, 4]'))]
        results.append(return_in + return_win + return_err)

    # Rally
    if hand == 'RH':  # RH
        directions = [[[1, 3, 2], [3, 1, 2], [1, 3, 2], [3, 1, 2], [3, 1, 2], [3, 1, 2], [3, 1, 2], [3, 1, 2], [3, 1, 2]], # de - FHCC, FHDL, FHDM, BHII, BHIO, BHDM
                      [[3, 1, 2], [1, 3, 2], [3, 1, 2], [1, 3, 2], [3, 1, 2], [3, 1, 2], [3, 1, 2], [3, 1, 2], [3, 1, 2]], # mid - FHIO, FHCC, FHDM, BHIO, BHCC, BHDM
                      [[3, 1, 2], [3, 1, 2], [3, 1, 2], [3, 1, 2], [1, 3, 2], [1, 3, 2], [1, 3, 2], [1, 3, 2], [1, 3, 2]]] # ad - FHIO, FHII, FHDM, BHCC, BHDL, BHDM

    else:  # LH
        directions = [[[1, 3, 2], [1, 3, 2], [1, 3, 2], [3, 1, 2], [3, 1, 2], [3, 1, 2], [3, 1, 2], [3, 1, 2], [3, 1, 2]],  # de - FHIO, FHII, FHDM, BHCC, BHDL, BHDM
                      [[1, 3, 2], [3, 1, 2], [3, 1, 2], [3, 1, 2], [1, 3, 2], [1, 3, 2], [1, 3, 2], [1, 3, 2], [1, 3, 2]],  # mid - FHIO, FHCC, FHDM, BHIO, BHCC, BHDM
                      [[3, 1, 2], [1, 3, 2], [3, 1, 2], [1, 3, 2], [1, 3, 2], [1, 3, 2], [1, 3, 2], [1, 3, 2], [1, 3, 2]]]  # ad - FHCC, FHDL, FHDM, BHII, BHIO, BHDM
        
    for i, Stroke in enumerate([De_Stroke, Mid_Stroke, Ad_Stroke]):
        FH_Stroke = Stroke.query('shot==1')
        BH_Stroke = Stroke.query('shot==22')
        Lob_Stroke = Stroke.query('shot==11 or shot==32')
        Volley_Stroke = Stroke.query('shot==5 or shot==26')
        Smash_Stroke = Stroke.query('shot==7 or shot==28')
        Slice_Stroke = Stroke.query('shot==3 or shot==24')
        DropShot_Stroke = Stroke.query('shot==9 or shot==30')
        HalfVolley_Stroke = Stroke.query('shot==13 or shot==34')
        SwingingVolley_Stroke = Stroke.query('shot==15 or shot==36')
        FH_shots = [FH_Stroke.query('to_which_court==@to_dir') for to_dir in directions[i][0]]
        BH_shots = [BH_Stroke.query('to_which_court==@to_dir') for to_dir in directions[i][1]]
        Lob_shots = [Lob_Stroke.query('to_which_court==@to_dir') for to_dir in directions[i][2]]
        Volley_shots = [Volley_Stroke.query('to_which_court==@to_dir') for to_dir in directions[i][3]]
        Smash_shots = [Smash_Stroke.query('to_which_court==@to_dir') for to_dir in directions[i][4]]
        Slice_shots = [Slice_Stroke.query('to_which_court==@to_dir') for to_dir in directions[i][5]]
        DropShot_shots = [DropShot_Stroke.query('to_which_court==@to_dir') for to_dir in directions[i][6]]
        HalfVolley_shots = [HalfVolley_Stroke.query('to_which_court==@to_dir') for to_dir in directions[i][7]]
        SwingingVolley_shots = [SwingingVolley_Stroke.query('to_which_court==@to_dir') for to_dir in directions[i][8]]
        shots = FH_shots + BH_shots + Lob_shots + Volley_shots + Smash_shots + Slice_shots + DropShot_shots + HalfVolley_shots + SwingingVolley_shots
        FH_stroke_in = [len(x.query('shot_outcome==7')) for x in FH_shots]
        BH_stroke_in = [len(x.query('shot_outcome==7')) for x in BH_shots]
        Lob_stroke_in = [len(x.query('shot_outcome==7')) for x in Lob_shots]
        Volley_stroke_in = [len(x.query('shot_outcome==7')) for x in Volley_shots]
        Smash_stroke_in = [len(x.query('shot_outcome==7')) for x in Smash_shots]
        Slice_stroke_in = [len(x.query('shot_outcome==7')) for x in Slice_shots]
        DropShot_stroke_in = [len(x.query('shot_outcome==7')) for x in DropShot_shots]
        HalfVolley_stroke_in = [len(x.query('shot_outcome==7')) for x in HalfVolley_shots]
        SwingingVolley_stroke_in = [len(x.query('shot_outcome==7')) for x in SwingingVolley_shots]
        stroke_win = [len(Stroke.query('shot_outcome in [1, 5, 6]'))]
        stroke_err = [len(Stroke.query('shot_outcome in [2, 3, 4]'))]
        results.append(FH_stroke_in + BH_stroke_in + Lob_stroke_in + Volley_stroke_in + Smash_stroke_in + Slice_stroke_in + DropShot_stroke_in + HalfVolley_stroke_in + SwingingVolley_stroke_in + stroke_win + stroke_err)

    return results


def generate_transition_probs(data, date, ply1_name, ply2_name, ply1_hand, ply2_hand):
    prev_date = (pd.to_datetime(date) - relativedelta(years=20)).strftime('%Y-%m-%d')

    data_ply1 = data.query('date>=@prev_date and date<@date and ply1_name==@ply1_name and ply2_name==@ply2_name')
    data_ply2 = data.query('date>=@prev_date and date<@date and ply1_name==@ply2_name and ply2_name==@ply1_name')

    # number of matches played
    num_ply1_prev_n = len(data_ply1.date.unique())
    num_ply2_prev_n = len(data_ply2.date.unique())

    # get players params
    ply1_params = get_params(data_ply1, ply1_hand)
    ply2_params = get_params(data_ply2, ply2_hand)

    # sample
    params = sum(ply1_params, []) + sum(ply2_params, [])

    print('# P1 matches:', num_ply1_prev_n)
    print('# P2 matches:', num_ply2_prev_n)
    
    # Generate pcsp files for pair of players with matches from database
    if num_ply1_prev_n > 0:
        generate_pcsp(params, date, ply1_name, ply2_name, ply1_hand, ply2_hand)


# obtain shot-by-shot data
file = 'tennisabstract-v2-combined.csv'
data = pd.read_csv(file, names=['ply1_name', 'ply2_name', 'ply1_hand', 'ply2_hand', 'ply1_points',
                                'ply2_points', 'ply1_games', 'ply2_games', 'ply1_sets', 'ply2_sets', 'date',
                                'tournament_name', 'shot_type', 'from_which_court', 'shot', 'direction',
                                'to_which_court', 'depth', 'touched_net', 'hit_at_depth', 'approach_shot',
                                'shot_outcome', 'fault_type', 'prev_shot_type', 'prev_shot_from_which_court',
                                'prev_shot', 'prev_shot_direction', 'prev_shot_to_which_court', 'prev_shot_depth',
                                'prev_shot_touched_net', 'prev_shot_hit_at_depth', 'prev_shot_approach_shot',
                                'prev_shot_outcome', 'prev_shot_fault_type', 'prev_prev_shot_type',
                                'prev_prev_shot_from_which_court', 'prev_prev_shot', 'prev_prev_shot_direction',
                                'prev_prev_shot_to_which_court', 'prev_prev_shot_depth',
                                'prev_prev_shot_touched_net', 'prev_prev_shot_hit_at_depth',
                                'prev_prev_shot_approach_shot', 'prev_prev_shot_outcome',
                                'prev_prev_shot_fault_type', 'url', 'description'])

# Extract players from MDP_pred file and combine dominant hand data from tennisabstract
columns = ['ply1_name', 'ply2_name', 'ply1_hand', 'ply2_hand']
player_hands = data[columns].copy().drop_duplicates()
players = pd.read_csv('MDP_pred.csv')
players = pd.merge(players, player_hands, left_on=['P1Name', 'P2Name'], right_on=['ply1_name', 'ply2_name'], how='inner')
players = players.drop(['P1WinProb', 'P2WinProb', 'P1Name', 'P2Name'], axis=1)


for index, row in players.iterrows():
    # Extract relevant information from the row
    date = row['date']
    ply1_name = row['ply1_name']
    ply2_name = row['ply2_name']
    ply1_hand = row['ply1_hand']
    ply2_hand = row['ply2_hand']

    # Generate pcsp files with each player data
    generate_transition_probs(data, date, ply1_name, ply2_name, ply1_hand, ply2_hand)


