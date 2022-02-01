# -*- coding: utf-8 -*-
"""
Last modified on Tue Feb  1  2022

@author: Thomas Berger

File purpose:
    grab all word counts from google ngram export
    get their relative frquency
    output as csv
"""


from os import listdir
from os.path import isfile, join
import pandas as pd

# take all files in ngram parse export path
mypath = "./Ngram export/"
myfs = [f for f in listdir(mypath) if isfile(join(mypath, f))]

# add all words to a dataframe
words = pd.read_csv(mypath + myfs[0], header = None,names=['word','proba'])
for f in myfs[1:]:
    words = words.append(pd.read_csv(mypath + f, header = None,names=['word','proba']))

# Find their relative frequencies
words = words.groupby('word').sum().reset_index()
words.iloc[:,1] = words.iloc[:,1]/words.iloc[:,1].sum()
words=words.drop(words.iloc[:,0][words.iloc[:,0].isna()].index,axis=0)

# Export
words.to_csv("./French_word_proba.csv",header=False,index = False)