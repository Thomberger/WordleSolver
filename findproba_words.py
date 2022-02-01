# -*- coding: utf-8 -*-
"""
Last modified on Tue Feb  1  2022

@author: Thomas Berger

File purpose:
    get a portion(row) of 1 file from google ngram
    find the counts of each words in this portion
    output as csv
    
for memory/processing power and parrallelization, the task is divided in smaller portion
create multiple console and run different portion for multitasking. 
TODO : better parrallelization
"""

import gzip
import numpy as np
import re
import pandas as pd
from tqdm import tqdm
import winsound
import unidecode
import logging

# file and portion index
f = '0'
row = 0

# logger config
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(format='%(asctime)s %(levelname)s | %(message)s')

# Extract file and split each words
logging.info('Opening file %s :' % f)
a_file = gzip.open("1-0000"+f+"-of-00006.gz", "rb")
contents = a_file.read()
logging.info('Extracted\n')
contents = contents.split(b'\n')
logging.info('Splitted\n')

# Extract dictionary and split each words
logging.info('Extracting dictionary :')
textfile = open("French ODS dictionary.txt", 'r')
dictionary = textfile.read()
textfile.close()
dictionary = dictionary.split("\n")
logging.info('Extracted\n')

# Select relevant portion (change portion size if needed)
sz = round(len(contents)*25/100)
contents = contents[sz*row:sz*(row+1)]
logging.info("Working from %d to %d" % (sz*row,sz*(row+1)))

# %% Processing

results = []

# get word and word count
def find_word_count(content):
    global dictionary
    word = unidecode.unidecode(re.split(b'\t|_',content)[0].decode("utf-8")).upper()
    if word in dictionary:
        return [word, sum([int(n.split(b',')[2].decode("utf-8")) for n in content[re.search(b'\t',content).end():].split(b'\t')])]

# Parse file with iteration counter
for content in tqdm(contents, mininterval=2, desc= "Word parsing",unit="word"):
    result = find_word_count(content)
    if result is not None:
        results.append(result)

# Make sound to alert user
winsound.Beep(200,300)
winsound.Beep(400,600)
winsound.Beep(200,300)

# Output
probs = pd.DataFrame(np.array(results))
probs.to_csv("./Ngram export/French_word_proba_%s_%d.csv" % (f,row),header=False,index = False)