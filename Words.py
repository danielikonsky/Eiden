import time, os, re, datetime, csv
import pandas as pd
from datetime import datetime

import string

words_df_list = []

# non-interesting words to be skipped. In real code instead of hardcoding will probably check against some library
skipword = ['the','and','to','of','that','a','in','we','i','for','is','our','this','it','you','on',
            'will','be','are','as','but','have','can','who','with','more','us','not','from','all','was','or','my','they','by',
            'has','their','about','what','when','its','one','he','were','at','there','because','she','his','so','been',
            'up','just','these','your','an','if','those','dont','thats','had','own','where','no','do','me','here','let','many','than','every','out','some',
            'how','make','them','also','should','keep','must','after','her','would','could','most','now','say','too']

def main():

# 1. Get  a list of input text  files
# 2. Load each file into dataframe
# 3. Process count of each word into DataFrame
# 4. Load each sentence as a row into Dataframe
# 5. Search if word in sentence and build word:sentence(s) dictionary then load into Dataframe
# 6. Merge word and sentence Dataframes to combine word, number of occurences, mentioned in what sentences, and in what file
# 7. Build and format output result.

    cwd = os.getcwd()

    listfiles = [f for f in (os.listdir(cwd)) if 'doc' in f]

    for filename in listfiles:

        print (filename + ' process started')

        input_df = pd.read_csv(filename,delimiter='/n',header=None,engine='python')

        words_df = wordsTodf(input_df)

        sentence_df = sentencesTodf(input_df)

        words_df = build_result(words_df,sentence_df,filename)

        words_df_list.append(words_df)

        print (filename + ' process finished')

    words_df = pd.concat(words_df_list,sort=True)

    create_out(words_df)

    print ('Process End {0}'.format(datetime.now()))

def wordsTodf(text_df):

    # Create an empty dictionary
    d = dict()

    # Loop through each line of the file

    for i in range(0,len(text_df)):
        line = text_df.iloc[i][0]
        # Remove the leading spaces and newline character
        line = line.strip()

        # Convert the characters in line to
        # lowercase to avoid case mismatch
        line = line.lower()

        # Remove the punctuation marks from the line
        line = line.translate(line.maketrans("", "", string.punctuation))

        # Split the line into words
        words = line.split(" ")

        # Iterate over each word in line
        for word in words:

            # Filter articles, prepositions etc
            if word in skipword:
                pass
            elif word in d:

            # Check if the word is already in dictionary

                # Increment count of word by 1
                d[word] = d[word] + 1
            else:
                # Add the word to dictionary with count 1
                if word > ' ':
                    d[word] = 1

        df = pd.DataFrame(list(d.items()), columns=['Word','Number of occurences'])

    return df

def sentencesTodf(text_df):

    # Create an empty list
    d = []

    # Loop through each line of the file

    for i in range(0,len(text_df)):
        line = text_df.iloc[i][0]
        # Remove the leading spaces and newline character
        line = line.strip()

        # For the purpose of this exersise replace ? and ! with .
        # For more refined code should use regular expression

        line = line.replace('!','.').replace('?','.')

        # Split the line into sentences
        sentences = line.split(".")

        # Iterate over each sentence in line
        for sentence in sentences:
            if sentence > ' ':

                d.append(sentence.strip())

    df = pd.DataFrame(d,columns=['Sentence'])

    return df

def build_result(words_df,sentences_df,filename):
    wordInSentences = {}
    inSentences = []
    for i in range(0, len(words_df)):
        for j in range(0,len(sentences_df)):

#Convert sentence to lowercase, strip of punctuation, and load to list
            s = sentences_df.iloc[j]['Sentence']
            exclude = set(string.punctuation)
            s = (''.join(ch for ch in s if ch not in exclude)).lower()
            s = s.split(' ')
            if words_df.iloc[i]['Word'] in s:

                inSentences.append((sentences_df.iloc[j]['Sentence'] + '. \n'))

        if len(inSentences) > 0:

            wordInSentences[words_df.iloc[i]['Word']] = '\n'.join(inSentences)

            inSentences = []

#Convert dict to df and merge

    df = pd.DataFrame(list(wordInSentences.items()), columns=['Word','In sentences'])
    df.insert(1, "In File", filename, True)

#Merge with words_df

    words_df = words_df.merge(df,left_on = 'Word',right_on = 'Word',how='left')

    return words_df

def create_out(words_df):

# Prepare output formatted file
    df1 = words_df.drop(columns=['In File','In sentences'])
    df1 = df1.groupby(['Word']).sum()

    df = words_df.drop(columns='Number of occurences')
    df = df.merge(df1,left_on = 'Word',right_on = 'Word',how='left')
    df = df.sort_values(by=['Number of occurences','In File'], ascending=[False,True])

    prevWord = ''
    for i in range(0,len(df)):

        if df.iloc[i]['Word'] == prevWord:
            newWord = False
        else:
            newWord = True
            prevWord = df.iloc[i]['Word']

# Only show a word in the first row if in more than one document
        if newWord:
            outWord = df.iloc[i]['Word']+' ('+str(df.iloc[i]['Number of occurences'])+')'
        else:
            outWord = ' '

        df.iloc[i, df.columns.get_loc('Word')] = outWord

    df.drop(columns='Number of occurences')
    df = df[['Word', 'In File', 'In sentences']]
    df.rename(columns = {'Word':'Word (Total Occurrences)', 'In File':'Documents','In sentences':'Sentences containing the word'},inplace = True)
    print (df)

    csv_file = 'outfile.csv'
    df.to_csv(csv_file, encoding='utf-8', index=False)

if __name__ == '__main__':
    main()
