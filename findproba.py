# -*- coding: utf-8 -*-
"""
Last modified on Tue Feb  1  2022

@author: Thomas Berger

File purpose:
    grab all words in dictionary
    get relative frequency of each letter
    output as csv
"""

import numpy as np
import pandas as pd
import re

# Read dictionary
textfile = open("French ODS dictionary.txt", 'r')
dictionary = textfile.read()
textfile.close()

# Count letters
probs=pd.DataFrame(np.empty((26,2)))
count = 0

letters= 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
for j,letter in enumerate(letters):
    n = len(re.findall(letter,dictionary))
    count +=  n
    probs.iloc[j,0]= letter
    probs.iloc[j,1]= n

# Output
probs.iloc[:,1]=probs.iloc[:,1]/count
probs.to_csv("French_letter_proba.csv",header=False,index = False)

