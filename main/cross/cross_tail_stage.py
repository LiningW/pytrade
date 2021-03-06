#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

#@author  Bin Hong

import sys,os
import json
import time
import numpy as np
import pandas as pd
from sklearn.externals import joblib # to dump model
import cPickle as pkl
local_path = os.path.dirname(__file__)
root = os.path.join(local_path, '..', '..')
sys.path.append(root)
sys.path.append(local_path)

import main.base as base
import main.ta as ta

def accu(df, label, threshold):
    if threshold > 0:
        df2 = df.sort("pred", ascending = False)[:threshold]
    else:
        df2 = df
    npPred = df2["pred"].values
    npLabel = df2[label].values
    npTrueInPos = npLabel[npLabel>1.0]
    return {"pos": npLabel.size, "trueInPos":npTrueInPos.size}

def get_range(df, start ,end):
    return df.query('date >="%s" & date <= "%s"' % (start, end)) 

def one_work(cls, taName, label, date_range, th):
    df = base.get_merged(base.dir_ta(taName))
    df = get_range(df, date_range[0], date_range[1])
    m = joblib.load(os.path.join(root, 'data', 'models',"model_" + cls + ".pkl"))
    s = joblib.load(os.path.join(root, 'data', 'models',"scaler_" + cls + ".pkl"))
    feat_names = base.get_feat_names(df)
    npFeat = df.loc[:,feat_names].values
    #npPred = cls.predict_proba(npFeat)[:,1]
    #prent npPred
    res = ""
    for i, npPred in enumerate(m.staged_predict_proba(s.transform(npFeat))):
        #if i % 1 != 0:
        #    continue
        re =  "%s\t%s\t%s\t%s\t%s\t%f\t" % (cls, taName, label, date_range[0], date_range[1],th)
        df["pred"] = npPred[:,1]
        dacc =  accu(df, label, th)
        re += "%d\t%d\t%d\t" % (i, dacc["trueInPos"], dacc["pos"])
        if dacc["pos"] > 0:
            re += "%f" % (dacc["trueInPos"]*1.0 / dacc["pos"])
        else :
            re += "0.0"
        re += "\n"
        print re
        res += re
    return re

def main(argv):
    conf_file = argv[1]
    impstr = "import %s as conf" % conf_file
    exec impstr
    out_file = os.path.join(root, 'data', "crosses", conf_file+".report")
    fout = open(out_file, 'w')

    res = one_work(*conf.params)
    print >> fout, "%s" % res
    fout.close()

if __name__ == '__main__':
    main(sys.argv)
