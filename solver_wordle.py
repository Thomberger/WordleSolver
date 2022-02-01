# -*- coding: utf-8 -*-
"""
Last modified on Tue Feb  1  2022

@author: Thomas Berger

File purpose:
    solve wordle
    
"""

import numpy as np
import pandas as pd
import re
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
import logging
import time



def FindLetters(soup,step):
    """
    Read HTML of website to get the pattern of the word to search and all hints
    
    Parameters
    ----------
    soup : BeautifulSoup
        HTML code of wordle page.
    step : int
        Current step of the wordle game.

    Returns
    -------
    str : str
        Current pattern we have to guess (letter in uppercase, joker as dot(.)).
    found : int
        indicate if all letters are found (game finnish).
    hints : list of list
        each list contains one hint corresponding to each step.
        
        hint: list of 3 elements:
            almletters_pos: list containing positions of almost letter (letter contained in
                            the final word vut not currently at the correct position)
            almletter : string containing almost letters ready for regex search
            nonletter : string containing letter not existing  in final word.
                                     

    """
    # Find game grid and current pattern
    str = ""
    if step==0:
        str="."*5
    else:
        sp = soup.find_all("div", {"class": "attempt"})[step-1]
        for i in sp.find_all("div", {"id": "letter-container"}):
            if i['class'][2]=="correct":
                str = str + i.text[1:-1]
            else:
                str = str + "."
    
    found=0
    
    # Get extra hints
    almletters_pos = []
    hints = []
    # for each step
    for j in range(0,step):
        letter_found = 0
        almletter = "(?:.*["
        nonletter = ""
        almletters_pos = []
        almcount =0
        
        
        # for each letter check letter category and add it to the hint
        sp = soup.find_all("div", {"class": "attempt"})[j]
        for k,i in enumerate(sp.find_all("div", {"id": "letter-container"})):
            fclass = i["class"][2]
            if fclass == 'partial':
                almcount +=1
                almletter += "" + i.text[1:-1] + "|"
                almletter_pos = ""
                almletter_pos = "."*k + i.text[1:-1] + "."*(len(str)-k-1)
                almletters_pos.append(almletter_pos)
                
            elif fclass == 'incorrect':
                nonletter += i.text[1:-1] + "|"
                
            elif fclass == 'correct':
                letter_found +=1
        
        if almcount > 0:
            almletter= almletter[:-1]+"].*){1}"
        else:
            almletter = ""
        
        hints.append([almletters_pos,almletter,nonletter[:-1]])
        
    # if game finished
    if letter_found ==5:
        found = 1
        
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source,features="lxml")
        str = "balec"
        hints = "monfrr"
    else:
        logging.info('Searching for the word: %s' % str)
    return str,found,hints,soup

def bestmatch(patterns,dictionary,proba,hints,step,t1 = 200,t2 = 70):#almletters,almletters_pos,nonletters):
    """
    From the pattern and all available hints find all the possible words.
    From the number of possible words, the letter probabilities and word probabilies find
    the best word to submit.

    Parameters
    ----------
    patterns : list of strings
        List of all patterns (patterns of future steps are not important).
    dictionary : list
        list of all possible words.
    proba : DataFrame
        Dataframe of the probability of each letter (generated with findproba.py).
    hints : list of list
        each list contains one hint corresponding to each step. See function FindLetters
        for more informations.
    step : int
        Current step of the wordle game.
    t1 : int, optional
        Threshold for counting word probability and letter probability rather than only letter probability. The default is 1000.
    t2 : int, optional
        Threshold for counting only  word  probability rather than word probability and letter probability. The default is 100.

    Returns
    -------
    match_df : Series
        *Ordered* series containing the first 100 most probable words order.

    """
    
    # find all match that contain the correct pattern and correct length
    matchs = np.empty((0,7))
    for match in dictionary:
        if re.findall(patterns[-1],match) and len(match)==len(patterns[-1]):
            matchs_wo = np.array([[match]])
            for pattern in patterns:
                match_wo = match
                for pat in pattern.split("."):
                    match_wo = match_wo.replace(pat,'',1)
                matchs_wo = np.append(matchs_wo,[[match_wo]], axis=1)
            matchs = np.append(matchs,matchs_wo, axis=0)
    
    
    logging.info('Found %d corresponding words' % len(matchs))
    
    if step>0:
        logging.info('Searching with extra hints')
        # for each hints
        for j,hint in enumerate(hints):
            matchs_old = matchs
            matchs = np.empty((0,7))
            almletters_pos,almletter,nonletter = hint
            for matchs_wo in matchs_old:
                match = matchs_wo[0]
                match_wo = matchs_wo[j+1]
                bad = 0
                # exclude word that have almost letter at position 
                for almletter_pos in almletters_pos:
                    if re.findall(almletter_pos,match):
                        bad +=1
                        
                # exclude word w/ good that do not contain almost letter
                if not re.findall(almletter,match_wo):
                    bad +=1
                # remove letter from almost letter in w/ good
                for pat in re.findall("[A-Z]",almletter):
                    match_wo = match_wo.replace(pat,'',1)
                
                        
                # Exclude word w/ good that contain non letter
                if re.findall(nonletter,match_wo):
                    bad +=1
                        
                # if all good write word
                if not bad:
                    matchs = np.append(matchs,[matchs_wo],axis=0)
        logging.info('Found %d corresponding words' % len(matchs))
    
    
    match_df = pd.Series([0]*len(matchs),index = matchs[:,0])
    
    # From all possible word find the best one
    write = 0
    leng = 0 # number of different letters
    
    # weight for letter or word probability
    if len(match_df)>t1:
        alpha = 0
    elif len(match_df)<t2:
        alpha = 1
    else:
        alpha = -1/(t1-t2)*len(match_df)+1/(t1-t2)*t2+1
    # while no word found
    while write == 0:
        # for each word
        for j,match in enumerate(match_df.index):
            match_unique = ''.join(set(match))
            # if it contains enough non repeting letters
            if len(match_unique)>=len(patterns[-1])+leng:
                write = 1
                # get its word probability from google ngram
                try:
                    r = word_proba["proba"][word_proba["word"]==match].values[0]
                except:
                    r=0
                p = 1
                # get its letter probability
                for i in match_unique:
                    p = p*proba.loc[i,1]
                # output its final word pobability
                match_df.iloc[j]= alpha * r + (1-alpha)* p
        leng = leng-1         
    return match_df.nlargest(500)

def SendWord(driver,match_df,w):
    """
    Send word to website

    Parameters
    ----------
    driver : 
        selenium browser driver.
    match_df : Series
        Ordered series of most probable words.
    w : int
        index of word to try.

    Returns
    -------
    soup : BeautifulSoup
        Updated HTML code of game.

    """
    # Send word
    actions = ActionChains(driver)
    actions.send_keys(match_df.index[w])
    actions.send_keys(Keys.ENTER)
    actions.perform()
    
    logging.info('Waiting for page update ...\n')
    time.sleep(0.5)
    
    # Update html
    soup = BeautifulSoup(driver.page_source,features="lxml")
    return soup

# %% Initialisation

# Logger
logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(format='%(asctime)s %(levelname)s | %(message)s')

# Get word list and letter probability
logging.info('Extracting words from Scrabble dictionaray ODS 8\n')
textfile = open("French ODS dictionary.txt", 'r')
dictionary = textfile.read().split('\n')
textfile.close()
proba = pd.read_csv("French_letter_proba.csv",header=None,index_col=0)
word_proba = pd.read_csv("French_word_proba.csv",header=None,index_col=None,names=['word','proba'])

# Get website
logging.info('launching Firefox on WORDLE\n')
driver = webdriver.Firefox()
driver.set_window_position(650, 0, windowHandle='current')
driver.get("https://wordle.louan.me/")
soup = BeautifulSoup(driver.page_source,features="lxml")

# %% Do 

# Send best word (hardcoded as no first hint always same most probable word)
soup = SendWord(driver,pd.DataFrame([0],index=["AIRES"]),0)
step = 1
finish = 0

# Get first hint
pattern,found,hints,soup = FindLetters(soup,step)
patterns = [pattern]*6
while finish == 0:
    found = 0
    # Get best words
    match_df = bestmatch(patterns,dictionary,proba,hints,step)
    
    # Try best word
    w = 0
    logging.info('Best word found is %s' % match_df.index[w])
    soup = SendWord(driver,match_df,w)
    
    # Until step submitted
    while found == 0:
        # If error delete word from dictionary (Word not valid for website) and retry
        if len(soup.find_all("div", {"class": "error"}))>0:
            dictionary.remove(match_df.index[w])
            w += 1
            logging.info('Word not valid for website, trying: %s' % match_df.index[w])
            actions = ActionChains(driver)
            for i in range(0,5):
                actions.send_keys(Keys.BACKSPACE)
            actions.perform()
            soup = SendWord(driver,match_df,w)
        # If word valid go to next steps
        else:
            found = 1
            step +=1
            
    # Get pattern and hint
    pattern,finish,hints,soup = FindLetters(soup,step)
    patterns[step:] = [pattern]*(6-step)

# Game finished
logging.info('Word found %s in %d steps:' % (match_df.index[w],step))

# click on share button
driver.find_elements(By.CLASS_NAME , "sh4re-btn-anti-adblock")[0].click()
logging.info('Results copied in clipboard')

# Closing
logging.info('Closing in 5 seconds')
time.sleep(5)
driver.close()



