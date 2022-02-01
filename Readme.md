# Wordle/Sutom solver

This project implement a solver for the wordle game. This solver work for games in FRENCH but could be adapted on other languages.<br>They are currently two version of the solver working on these websites : [Wordle](https://wordle.louan.me/), [Sutom](https://sutom.nocle.fr/).

<img src="Demo.gif" width="100%" >

## How it works
First the solver launch the website.<br>
Then, at each step:<br>
-Find the pattern to search for and all the hints.<br>
-Select the words agreeing with each hint from a list of possible words (Extracted from the French Scrabble dictionary, ODS 8, 2019 [link](https://github.com/Thecoolsim/French-Scrablle-ODS8) ). The hints are processed step after step as logic contains inexplicit rules : see note. <br>
-Computes the probability of all possible words from their set of letters and there probability in the French language.<br>
The probability of each letter is determined by their relative frequency from the dictionary in `findproba.py` and exported in `French_letter_proba.csv`. <br>
The probability of each word in the French language was found from the [Google Ngram Corpus](https://books.google.com/ngrams) available for download [here](https://storage.googleapis.com/books/ngrams/books/datasetsv3.html). The files are parsed in `findproba_words.py` and exported in `French_word_proba.csv`.<br>
The probability determined by the set of letter allow to get better hint at next step. The probability determined by the word probability allow to guess final words as wordle game do not select rare words. <br>
The final probability is determined by both probabilities weighted by the number of possible words (lot of possible words, high weight on letter probability; few possible words, high weight on word probability).
-Submits the guess and go to next step.


*Note on wordle logic*.<br>
Because the correct/possible and impossible letter logic contain inexplicit rules, it is needed to process each hint one after the other and not as a batch with : all correct letters, all possible letters and all impossible letter. For example if we select all words not containing impossible letters, we could remove possible words as impossible letters are determined from the correct and possible letter of the current guess. More precisely, if the word contains exactly one A and the guessed word contain 2 A the first one will be considered correct(or possible) and the second one impossible. The latter doesn't mean the final word do not contain any A but it contain exactly one A.

## Licence

This software is distributed under the MIT license. Enjoy!
