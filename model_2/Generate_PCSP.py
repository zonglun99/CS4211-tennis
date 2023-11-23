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
    De_Stroke_FH = df.query('shot_type==4 and from_which_court==1 and prev_shot<=20')
    Mid_Stroke_FH = df.query('shot_type==4 and from_which_court==2 and prev_shot<=20')
    Ad_Stroke_FH = df.query('shot_type==4 and from_which_court==3 and prev_shot<=20')
    De_Stroke_BH = df.query('shot_type==4 and from_which_court==1 and prev_shot<=40 and prev_shot>20')
    Mid_Stroke_BH = df.query('shot_type==4 and from_which_court==2 and prev_shot<=40 and prev_shot>20')
    Ad_Stroke_BH = df.query('shot_type==4 and from_which_court==3 and prev_shot<=40 and prev_shot>20')

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
        directions = [[[1, 3, 2], [3, 1, 2], [1, 3, 2], [3, 1, 2], [3, 1, 2], [3, 1, 2], [3, 1, 2], [3, 1, 2], [3, 1, 2], [3, 1, 2], [3, 1, 2], [3, 1, 2], [3, 1, 2], [3, 1, 2], [3, 1, 2], [3, 1, 2]], # de - FHCC, FHDL, FHDM, BHII, BHIO, BHDM
                      [[3, 1, 2], [1, 3, 2], [3, 1, 2], [1, 3, 2], [1, 3, 2], [1, 3, 2], [3, 1, 2], [1, 3, 2], [3, 1, 2], [1, 3, 2], [3, 1, 2], [1, 3, 2], [3, 1, 2], [1, 3, 2], [3, 1, 2], [1, 3, 2]], # mid - FHIO, FHCC, FHDM, BHIO, BHCC, BHDM
                      [[3, 1, 2], [3, 1, 2], [3, 1, 2], [3, 1, 2], [3, 1, 2], [3, 1, 2], [3, 1, 2], [3, 1, 2], [3, 1, 2], [3, 1, 2], [3, 1, 2], [3, 1, 2], [3, 1, 2], [3, 1, 2], [3, 1, 2], [3, 1, 2]]] # ad - FHIO, FHII, FHDM, BHCC, BHDL, BHDM

    else:  # LH
        directions = [[[1, 3, 2], [1, 3, 2], [1, 3, 2], [1, 3, 2], [1, 3, 2], [1, 3, 2], [1, 3, 2], [1, 3, 2], [1, 3, 2], [1, 3, 2], [1, 3, 2], [1, 3, 2], [1, 3, 2], [1, 3, 2], [1, 3, 2], [1, 3, 2]],  # de - FHIO, FHII, FHDM, BHCC, BHDL, BHDM
                      [[1, 3, 2], [1, 3, 2], [3, 1, 2], [3, 1, 2], [1, 3, 2], [1, 3, 2], [3, 1, 2], [3, 1, 2], [1, 3, 2], [1, 3, 2], [3, 1, 2], [3, 1, 2], [1, 3, 2], [1, 3, 2], [3, 1, 2], [3, 1, 2]],  # mid - FHIO, FHCC, FHDM, BHIO, BHCC, BHDM
                      [[3, 1, 2], [3, 1, 2], [1, 3, 2], [1, 3, 2], [3, 1, 2], [3, 1, 2], [1, 3, 2], [1, 3, 2], [3, 1, 2], [3, 1, 2], [1, 3, 2], [1, 3, 2], [3, 1, 2], [3, 1, 2], [1, 3, 2], [1, 3, 2]]]  # ad - FHCC, FHDL, FHDM, BHII, BHIO, BHDM
    for i, Stroke in enumerate([De_Stroke_FH, Mid_Stroke_FH, Ad_Stroke_FH]):
        Prev_FH_Stroke = Stroke.query('prev_shot<=20')
        FH_Stroke_Prev_FH = Prev_FH_Stroke.query('shot==1')
        BH_Stroke_Prev_FH = Prev_FH_Stroke.query('shot==22')
        FHLob_Stroke_Prev_FH = Prev_FH_Stroke.query('shot==11')
        BHLob_Stroke_Prev_FH = Prev_FH_Stroke.query('shot==32')
        FHVolley_Stroke_Prev_FH = Prev_FH_Stroke.query('shot==5')
        BHVolley_Stroke_Prev_FH = Prev_FH_Stroke.query('shot==26')
        FHSmash_Stroke_Prev_FH = Prev_FH_Stroke.query('shot==7')
        BHSmash_Stroke_Prev_FH = Prev_FH_Stroke.query('shot==28')
        FHSlice_Stroke_Prev_FH = Prev_FH_Stroke.query('shot==3')
        BHSlice_Stroke_Prev_FH = Prev_FH_Stroke.query('shot==24')
        FHDropShot_Stroke_Prev_FH = Prev_FH_Stroke.query('shot==9')
        BHDropShot_Stroke_Prev_FH = Prev_FH_Stroke.query('shot==30')
        FHHalfVolley_Stroke_Prev_FH = Prev_FH_Stroke.query('shot==13')
        BHHalfVolley_Stroke_Prev_FH = Prev_FH_Stroke.query('shot==34')
        FHSwingingVolley_Stroke_Prev_FH = Prev_FH_Stroke.query('shot==15')
        BHSwingingVolley_Stroke_Prev_FH = Prev_FH_Stroke.query('shot==36')
        FH_shots_Prev_FH = [FH_Stroke_Prev_FH.query('to_which_court==@to_dir') for to_dir in directions[i][0]]
        BH_shots_Prev_FH = [BH_Stroke_Prev_FH.query('to_which_court==@to_dir') for to_dir in directions[i][1]]
        FHLob_shots_Prev_FH = [FHLob_Stroke_Prev_FH.query('to_which_court==@to_dir') for to_dir in directions[i][2]]
        BHLob_shots_Prev_FH = [BHLob_Stroke_Prev_FH.query('to_which_court==@to_dir') for to_dir in directions[i][3]]
        FHVolley_shots_Prev_FH = [FHVolley_Stroke_Prev_FH.query('to_which_court==@to_dir') for to_dir in directions[i][4]]
        BHVolley_shots_Prev_FH = [BHVolley_Stroke_Prev_FH.query('to_which_court==@to_dir') for to_dir in directions[i][5]]
        FHSmash_shots_Prev_FH = [FHSmash_Stroke_Prev_FH.query('to_which_court==@to_dir') for to_dir in directions[i][6]]
        BHSmash_shots_Prev_FH = [BHSmash_Stroke_Prev_FH.query('to_which_court==@to_dir') for to_dir in directions[i][7]]
        FHSlice_shots_Prev_FH = [FHSlice_Stroke_Prev_FH.query('to_which_court==@to_dir') for to_dir in directions[i][8]]
        BHSlice_shots_Prev_FH = [BHSlice_Stroke_Prev_FH.query('to_which_court==@to_dir') for to_dir in directions[i][9]]
        FHDropShot_shots_Prev_FH = [FHDropShot_Stroke_Prev_FH.query('to_which_court==@to_dir') for to_dir in directions[i][10]]
        BHDropShot_shots_Prev_FH = [BHDropShot_Stroke_Prev_FH.query('to_which_court==@to_dir') for to_dir in directions[i][11]]
        FHHalfVolley_shots_Prev_FH = [FHHalfVolley_Stroke_Prev_FH.query('to_which_court==@to_dir') for to_dir in directions[i][12]]
        BHHalfVolley_shots_Prev_FH = [BHHalfVolley_Stroke_Prev_FH.query('to_which_court==@to_dir') for to_dir in directions[i][13]]
        FHSwingingVolley_shots_Prev_FH = [FHSwingingVolley_Stroke_Prev_FH.query('to_which_court==@to_dir') for to_dir in directions[i][14]]
        BHSwingingVolley_shots_Prev_FH = [BHSwingingVolley_Stroke_Prev_FH.query('to_which_court==@to_dir') for to_dir in directions[i][15]]
        shots_Prev_FH = FH_shots_Prev_FH + BH_shots_Prev_FH + FHLob_shots_Prev_FH + BHLob_shots_Prev_FH + FHVolley_shots_Prev_FH + BHVolley_shots_Prev_FH + FHSmash_shots_Prev_FH + BHSmash_shots_Prev_FH + FHSlice_shots_Prev_FH + BHSlice_shots_Prev_FH + FHDropShot_shots_Prev_FH + BHDropShot_shots_Prev_FH + FHHalfVolley_shots_Prev_FH + BHHalfVolley_shots_Prev_FH + FHSwingingVolley_shots_Prev_FH + BHSwingingVolley_shots_Prev_FH
        FH_stroke_in_Prev_FH = [len(x.query('shot_outcome==7')) for x in FH_shots_Prev_FH]
        BH_stroke_in_Prev_FH = [len(x.query('shot_outcome==7')) for x in BH_shots_Prev_FH]
        FHLob_stroke_in_Prev_FH = [len(x.query('shot_outcome==7')) for x in FHLob_shots_Prev_FH]
        BHLob_stroke_in_Prev_FH = [len(x.query('shot_outcome==7')) for x in BHLob_shots_Prev_FH]
        FHVolley_stroke_in_Prev_FH = [len(x.query('shot_outcome==7')) for x in FHVolley_shots_Prev_FH]
        BHVolley_stroke_in_Prev_FH = [len(x.query('shot_outcome==7')) for x in BHVolley_shots_Prev_FH]
        FHSmash_stroke_in_Prev_FH = [len(x.query('shot_outcome==7')) for x in FHSmash_shots_Prev_FH]
        BHSmash_stroke_in_Prev_FH = [len(x.query('shot_outcome==7')) for x in BHSmash_shots_Prev_FH]
        FHSlice_stroke_in_Prev_FH = [len(x.query('shot_outcome==7')) for x in FHSlice_shots_Prev_FH]
        BHSlice_stroke_in_Prev_FH = [len(x.query('shot_outcome==7')) for x in BHSlice_shots_Prev_FH]
        FHDropShot_stroke_in_Prev_FH = [len(x.query('shot_outcome==7')) for x in FHDropShot_shots_Prev_FH]
        BHDropShot_stroke_in_Prev_FH = [len(x.query('shot_outcome==7')) for x in BHDropShot_shots_Prev_FH]
        FHHalfVolley_stroke_in_Prev_FH = [len(x.query('shot_outcome==7')) for x in FHHalfVolley_shots_Prev_FH]
        BHHalfVolley_stroke_in_Prev_FH = [len(x.query('shot_outcome==7')) for x in BHHalfVolley_shots_Prev_FH]
        FHSwingingVolley_stroke_in_Prev_FH = [len(x.query('shot_outcome==7')) for x in FHSwingingVolley_shots_Prev_FH]
        BHSwingingVolley_stroke_in_Prev_FH = [len(x.query('shot_outcome==7')) for x in BHSwingingVolley_shots_Prev_FH]
        stroke_win_Prev_FH = [len(Stroke.query('shot_outcome in [1, 5, 6]'))]
        stroke_err_Prev_FH = [len(Stroke.query('shot_outcome in [2, 3, 4]'))]
        results.append(FH_stroke_in_Prev_FH + BH_stroke_in_Prev_FH + FHLob_stroke_in_Prev_FH + BHLob_stroke_in_Prev_FH + FHVolley_stroke_in_Prev_FH + BHVolley_stroke_in_Prev_FH + FHSmash_stroke_in_Prev_FH + BHSmash_stroke_in_Prev_FH + FHSlice_stroke_in_Prev_FH + BHSlice_stroke_in_Prev_FH + FHDropShot_stroke_in_Prev_FH + BHDropShot_stroke_in_Prev_FH + FHHalfVolley_stroke_in_Prev_FH + BHHalfVolley_stroke_in_Prev_FH + FHSwingingVolley_stroke_in_Prev_FH + BHSwingingVolley_stroke_in_Prev_FH + stroke_win_Prev_FH + stroke_err_Prev_FH)

    if hand == 'RH':  # RH
        directions = [[[1, 3, 2], [3, 1, 2], [1, 3, 2], [3, 1, 2], [3, 1, 2], [3, 1, 2], [3, 1, 2], [3, 1, 2], [3, 1, 2], [3, 1, 2], [3, 1, 2], [3, 1, 2], [3, 1, 2], [3, 1, 2], [3, 1, 2], [3, 1, 2]], # de - FHCC, FHDL, FHDM, BHII, BHIO, BHDM
                      [[3, 1, 2], [1, 3, 2], [3, 1, 2], [1, 3, 2], [1, 3, 2], [1, 3, 2], [3, 1, 2], [1, 3, 2], [3, 1, 2], [1, 3, 2], [3, 1, 2], [1, 3, 2], [3, 1, 2], [1, 3, 2], [3, 1, 2], [1, 3, 2]], # mid - FHIO, FHCC, FHDM, BHIO, BHCC, BHDM
                      [[3, 1, 2], [3, 1, 2], [3, 1, 2], [3, 1, 2], [3, 1, 2], [3, 1, 2], [3, 1, 2], [3, 1, 2], [3, 1, 2], [3, 1, 2], [3, 1, 2], [3, 1, 2], [3, 1, 2], [3, 1, 2], [3, 1, 2], [3, 1, 2]]] # ad - FHIO, FHII, FHDM, BHCC, BHDL, BHDM

    else:  # LH
        directions = [[[1, 3, 2], [1, 3, 2], [1, 3, 2], [1, 3, 2], [1, 3, 2], [1, 3, 2], [1, 3, 2], [1, 3, 2], [1, 3, 2], [1, 3, 2], [1, 3, 2], [1, 3, 2], [1, 3, 2], [1, 3, 2], [1, 3, 2], [1, 3, 2]],  # de - FHIO, FHII, FHDM, BHCC, BHDL, BHDM
                      [[1, 3, 2], [1, 3, 2], [3, 1, 2], [3, 1, 2], [1, 3, 2], [1, 3, 2], [3, 1, 2], [3, 1, 2], [1, 3, 2], [1, 3, 2], [3, 1, 2], [3, 1, 2], [1, 3, 2], [1, 3, 2], [3, 1, 2], [3, 1, 2]],  # mid - FHIO, FHCC, FHDM, BHIO, BHCC, BHDM
                      [[3, 1, 2], [3, 1, 2], [1, 3, 2], [1, 3, 2], [3, 1, 2], [3, 1, 2], [1, 3, 2], [1, 3, 2], [3, 1, 2], [3, 1, 2], [1, 3, 2], [1, 3, 2], [3, 1, 2], [3, 1, 2], [1, 3, 2], [1, 3, 2]]]  # ad - FHCC, FHDL, FHDM, BHII, BHIO, BHDM
    for i, Stroke in enumerate([De_Stroke_BH, Mid_Stroke_BH, Ad_Stroke_BH]):
        Prev_BH_Stroke = Stroke.query('prev_shot<=40 and prev_shot>20')
        FH_Stroke_Prev_BH = Prev_BH_Stroke.query('shot==1')
        BH_Stroke_Prev_BH = Prev_BH_Stroke.query('shot==22')
        FHLob_Stroke_Prev_BH = Prev_BH_Stroke.query('shot==11')
        BHLob_Stroke_Prev_BH = Prev_BH_Stroke.query('shot==32')
        FHVolley_Stroke_Prev_BH = Prev_BH_Stroke.query('shot==5')
        BHVolley_Stroke_Prev_BH = Prev_BH_Stroke.query('shot==26')
        FHSmash_Stroke_Prev_BH = Prev_BH_Stroke.query('shot==7')
        BHSmash_Stroke_Prev_BH = Prev_BH_Stroke.query('shot==28')
        FHSlice_Stroke_Prev_BH = Prev_BH_Stroke.query('shot==3')
        BHSlice_Stroke_Prev_BH = Prev_BH_Stroke.query('shot==24')
        FHDropShot_Stroke_Prev_BH = Prev_BH_Stroke.query('shot==9')
        BHDropShot_Stroke_Prev_BH = Prev_BH_Stroke.query('shot==30')
        FHHalfVolley_Stroke_Prev_BH = Prev_BH_Stroke.query('shot==13')
        BHHalfVolley_Stroke_Prev_BH = Prev_BH_Stroke.query('shot==34')
        FHSwingingVolley_Stroke_Prev_BH = Prev_BH_Stroke.query('shot==15')
        BHSwingingVolley_Stroke_Prev_BH = Prev_BH_Stroke.query('shot==36')
        FH_shots_Prev_BH = [FH_Stroke_Prev_BH.query('to_which_court==@to_dir') for to_dir in directions[i][0]]
        BH_shots_Prev_BH = [BH_Stroke_Prev_BH.query('to_which_court==@to_dir') for to_dir in directions[i][1]]
        FHLob_shots_Prev_BH = [FHLob_Stroke_Prev_BH.query('to_which_court==@to_dir') for to_dir in directions[i][2]]
        BHLob_shots_Prev_BH = [BHLob_Stroke_Prev_BH.query('to_which_court==@to_dir') for to_dir in directions[i][3]]
        FHVolley_shots_Prev_BH = [FHVolley_Stroke_Prev_BH.query('to_which_court==@to_dir') for to_dir in directions[i][4]]
        BHVolley_shots_Prev_BH = [BHVolley_Stroke_Prev_BH.query('to_which_court==@to_dir') for to_dir in directions[i][5]]
        FHSmash_shots_Prev_BH = [FHSmash_Stroke_Prev_BH.query('to_which_court==@to_dir') for to_dir in directions[i][6]]
        BHSmash_shots_Prev_BH = [BHSmash_Stroke_Prev_BH.query('to_which_court==@to_dir') for to_dir in directions[i][7]]
        FHSlice_shots_Prev_BH = [FHSlice_Stroke_Prev_BH.query('to_which_court==@to_dir') for to_dir in directions[i][8]]
        BHSlice_shots_Prev_BH = [BHSlice_Stroke_Prev_BH.query('to_which_court==@to_dir') for to_dir in directions[i][9]]
        FHDropShot_shots_Prev_BH = [FHDropShot_Stroke_Prev_BH.query('to_which_court==@to_dir') for to_dir in directions[i][10]]
        BHDropShot_shots_Prev_BH = [BHDropShot_Stroke_Prev_BH.query('to_which_court==@to_dir') for to_dir in directions[i][11]]
        FHHalfVolley_shots_Prev_BH = [FHHalfVolley_Stroke_Prev_BH.query('to_which_court==@to_dir') for to_dir in directions[i][12]]
        BHHalfVolley_shots_Prev_BH = [BHHalfVolley_Stroke_Prev_BH.query('to_which_court==@to_dir') for to_dir in directions[i][13]]
        FHSwingingVolley_shots_Prev_BH = [FHSwingingVolley_Stroke_Prev_BH.query('to_which_court==@to_dir') for to_dir in directions[i][14]]
        BHSwingingVolley_shots_Prev_BH = [BHSwingingVolley_Stroke_Prev_BH.query('to_which_court==@to_dir') for to_dir in directions[i][15]]
        shots_Prev_BH = FH_shots_Prev_BH + BH_shots_Prev_BH + FHLob_shots_Prev_BH + BHLob_shots_Prev_BH + FHVolley_shots_Prev_BH + BHVolley_shots_Prev_BH + FHSmash_shots_Prev_BH + BHSmash_shots_Prev_BH + FHSlice_shots_Prev_BH + BHSlice_shots_Prev_BH + FHDropShot_shots_Prev_BH + BHDropShot_shots_Prev_BH + FHHalfVolley_shots_Prev_BH + BHHalfVolley_shots_Prev_BH + FHSwingingVolley_shots_Prev_BH + BHSwingingVolley_shots_Prev_BH
        FH_stroke_in_Prev_BH = [len(x.query('shot_outcome==7')) for x in FH_shots_Prev_BH]
        BH_stroke_in_Prev_BH = [len(x.query('shot_outcome==7')) for x in BH_shots_Prev_BH]
        FHLob_stroke_in_Prev_BH = [len(x.query('shot_outcome==7')) for x in FHLob_shots_Prev_BH]
        BHLob_stroke_in_Prev_BH = [len(x.query('shot_outcome==7')) for x in BHLob_shots_Prev_BH]
        FHVolley_stroke_in_Prev_BH = [len(x.query('shot_outcome==7')) for x in FHVolley_shots_Prev_BH]
        BHVolley_stroke_in_Prev_BH = [len(x.query('shot_outcome==7')) for x in BHVolley_shots_Prev_BH]
        FHSmash_stroke_in_Prev_BH = [len(x.query('shot_outcome==7')) for x in FHSmash_shots_Prev_BH]
        BHSmash_stroke_in_Prev_BH = [len(x.query('shot_outcome==7')) for x in BHSmash_shots_Prev_BH]
        FHSlice_stroke_in_Prev_BH = [len(x.query('shot_outcome==7')) for x in FHSlice_shots_Prev_BH]
        BHSlice_stroke_in_Prev_BH = [len(x.query('shot_outcome==7')) for x in BHSlice_shots_Prev_BH]
        FHDropShot_stroke_in_Prev_BH = [len(x.query('shot_outcome==7')) for x in FHDropShot_shots_Prev_BH]
        BHDropShot_stroke_in_Prev_BH = [len(x.query('shot_outcome==7')) for x in BHDropShot_shots_Prev_BH]
        FHHalfVolley_stroke_in_Prev_BH = [len(x.query('shot_outcome==7')) for x in FHHalfVolley_shots_Prev_BH]
        BHHalfVolley_stroke_in_Prev_BH = [len(x.query('shot_outcome==7')) for x in BHHalfVolley_shots_Prev_BH]
        FHSwingingVolley_stroke_in_Prev_BH = [len(x.query('shot_outcome==7')) for x in FHSwingingVolley_shots_Prev_BH]
        BHSwingingVolley_stroke_in_Prev_BH = [len(x.query('shot_outcome==7')) for x in BHSwingingVolley_shots_Prev_BH]
        stroke_win_Prev_BH = [len(Stroke.query('shot_outcome in [1, 5, 6]'))]
        stroke_err_Prev_BH = [len(Stroke.query('shot_outcome in [2, 3, 4]'))]
        results.append(FH_stroke_in_Prev_BH + BH_stroke_in_Prev_BH + FHLob_stroke_in_Prev_BH + BHLob_stroke_in_Prev_BH + FHVolley_stroke_in_Prev_BH + BHVolley_stroke_in_Prev_BH + FHSmash_stroke_in_Prev_BH + BHSmash_stroke_in_Prev_BH + FHSlice_stroke_in_Prev_BH + BHSlice_stroke_in_Prev_BH + FHDropShot_stroke_in_Prev_BH + BHDropShot_stroke_in_Prev_BH + FHHalfVolley_stroke_in_Prev_BH + BHHalfVolley_stroke_in_Prev_BH + FHSwingingVolley_stroke_in_Prev_BH + BHSwingingVolley_stroke_in_Prev_BH + stroke_win_Prev_BH + stroke_err_Prev_BH)

    return results


def generate_transition_probs(data, date, ply1_name, ply2_name, ply1_hand, ply2_hand):
    # increase date period to 20 years so more matches can be extracted
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
    if (num_ply1_prev_n > 0):
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
