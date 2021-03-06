# -*- coding: utf-8 -*-
"""Netcracker_task02eng.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1gSqkXFB5UCjf171SCp1nbpfMdQXCvE9g

Task from Netcracker to find outliners in data. Made by Alex Bocharov skype bam271074



Let s install pyldavis lib for visualization
"""

!pip install pyldavis

import numpy as np
import pandas as pd
import re
from sklearn.metrics import *
from sklearn.pipeline import *
from sklearn.feature_extraction.text import *
from sklearn.decomposition import TruncatedSVD, PCA
from sklearn.preprocessing import Normalizer, LabelEncoder
from gensim.models import *
from gensim import corpora
from gensim import similarities
import random
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import style
# %matplotlib inline
style.use('ggplot')
import pyLDAvis
import pyLDAvis.gensim as gensimvis


import warnings
warnings.filterwarnings('ignore')

#let s upload file with data
from google.colab import files
uploaded = files.upload()
for fn in uploaded.keys():
  print ('User uploaded file {name} with length {length} bytes'.format(name=fn, \
                                                                       length=len(uploaded[fn])))

!ls

!wget https://github.com/GuansongPang/anomaly-detection-datasets/blob/main/categorical%20data/census-income-full-nominal.tar.xz

!ls

#let s build dataframe from uploaded file

df = pd.read_csv("census-income-full-nominal.arff", sep=',', skip_blank_lines=True, header=36)
df.head()

df.tail()

df.shape

df.columns

df.describe(include=['object']).T

#let s see how many NaNs
df.isnull().sum()

"""Anoimaly #1- 1279 NaNs"""

df['All-other'].fillna(value='NaNvalue',inplace=True)

#let s see how many NaNs
df.isnull().sum()

def concat_features(x1,x2,x3,x4,x5,x6,x7,x8,x9,x10,x11,x12,x13,x14,x15,x16,x17,x18,x19,x20,x21,x22,x23,x24,x25,x26,x27,x28,x29,x30,x31,x32,x33):
  """
  Let s concat features
  """
  buff=(str(x1)+' '+str(x2)+' '+str(x3)+' '+' '+str(x4)+' '+str(x5)+' '+str(x6)+' '+str(x7)+' '+str(x8)+' '+str(x9)+' '+
        str(x10)+' '+str(x11)+' '+str(x12)+' '+str(x13)+' '+str(x14)+' '+str(x15)+' '+str(x16)+' '+str(x17)+' '+
        str(x18)+' '+str(x19)+' '+str(x20)+' '+str(x21)+' '+str(x22)+' '+str(x23)+' '+str(x24)+' '+str(x25)+' '+
        str(x26)+' '+str(x27)+' '+str(x28)+' '+str(x29)+' '+str(x30)+' '+str(x31)+' '+str(x32)+' '+str(x33))
  return buff

concat_features('a','b','c','D','e','f,','r','y','f','h','ee',
                'w','e','d','r','t','w','x','i','u','o','l',
                'a','d','s','x','z','x','v','b','b','m','p')

TOKEN_RE = re.compile(r'[\w\d]+')  #regular expression to divide data

def tokenize_text_simple_regex(txt, min_token_size=2):
    """ This func tokenize text with TOKEN_RE applied ealier """
    txt = txt.lower()
    all_tokens = TOKEN_RE.findall(txt)
    all_tokens = [token for token in all_tokens if len(token) >= min_token_size]
    s=' '.join(all_tokens)
    return s

X_list=[]  #list for concat results
#loop on dataframe
#we do not use column #34. it seems target
for t in df.itertuples():
  buff=concat_features(t[1],t[2],t[3],t[4],t[5],t[6],t[7],t[8],t[9],t[10],t[11],t[12],t[13],t[14],t[15],t[16],t[17],
                       t[18],t[19],t[20],t[21],t[22],t[23],t[24],t[25],t[26],t[27],t[28],t[29],t[30],t[31],t[32],t[33])
  buff=tokenize_text_simple_regex(buff, min_token_size=4)
  X_list.append(buff)

X_list[0]

tokenized_texts = []
for text in X_list:
    #text = [w for w in text.split() if w not in sw]  #del stop words
    text = [w for w in text.split()]
    tokenized_texts.append(text)

print('Making dictionary...')
dictionary = corpora.Dictionary(tokenized_texts)
print('Original: {}'.format(dictionary))
dictionary.filter_extremes(no_below = 2, no_above = 0.95, keep_n=None)
print('Filtered: {}'.format(dictionary))

print('Vectorizing corpus...')
corpus = [dictionary.doc2bow(text) for text in tokenized_texts]



"""##Latent Dirichet Allocation(LDA)


This model is also implemented in the gensim library. One of its advantages is that you can train the finished model (and unlike LSA and pLSA, where even when adding one new document you have to train the model from scratch).

We assume that in the entire collection of k topics.
We distribute these k topics according to documents m (this is the distribution ??), assigning a topic to each document.
For each word w in the document, we assume that its theme is incorrect, while the themes of all other words are correct.

Based on probability, we assign a theme to the word w, based on:
which topics in document m
how many times the word w was assigned to specific topics in the entire collection (this is the distribution ??)
We repeat many, many times
?? is a matrix (stochastic) where each row = document, column = theme.

?? is a matrix (stochastic) where each row = theme, column = word.

## Latent Dirichet Allocatoin

???????????? ???????????? ?????????? ?????????????????????? ?? ???????????????????? `gensim`. ???????? ???? ???? ???????????? ?? ??????, ?????? ?????????? ?????????????????? ?????????????? ???????????? (?? ?????????????? ???? LSA ?? pLSA, ?????? ???????? ?????? ???????????????????? ???????????? ???????????? ?????????????????? ???????????????????? ?????????????? ???????????? ?? ????????).

- ????????????????????????, ?????? ???? ???????? ?????????????????? k ??????.
- ???????????????????????? ?????? k ?????? ???? ???????????????????? m (?????? ?????????????????????????? ??), ???????????????????? ?????????????? ?????????????????? ????????.
- ?????? ?????????????? ?????????? w  ?? ?????????????????? m????????????????????????, ?????? ?????? ???????? ??????????????, ?????? ???????? ???????? ???????? ?????????????????? ???????? ??????????.
- ?????????????????????? ???? ?????????????????????? ?????????????????????? ?????????? w ????????, ???????????????? ????:
    1. ?????????? ???????? ?? ??????????????????  m
    2. ?????????????? ?????? ?????????? w ?????????????????????????? ???????????????????? ?????????? ???? ???????? ?????????????????? (?????? ?????????????????????????? ??)
- ?????????????????? ??????????-?????????? ??????

?? - ?????? ?????????????? (????????????????????????????), ?????? ???????????? ???????????? = ????????????????, ?????????????? = ????????. 

?? - ?????? ?????????????? (????????????????????????????), ?????? ???????????? ???????????? = ????????, ?????????????? = ??????????.
"""

# Commented out IPython magic to ensure Python compatibility.
# %%time
# lda = ldamodel.LdaModel(corpus, id2word=dictionary, num_topics=25, chunksize=50, update_every=1, passes=2)

lda.show_topics(num_topics=3, num_words=15, formatted=False)

vis_data = gensimvis.prepare(lda, corpus, dictionary)
pyLDAvis.display(vis_data)



"""For example if we take a look at theme #28, it is connected with people from Cuba(take a look at words connected with this group). We found anomaly."""



