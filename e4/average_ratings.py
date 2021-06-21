import numpy as np
import pandas as pd
import sys
import difflib

def check_closeness(word, possibilities):
    possibilities = list(possibilities)
    ret = difflib.get_close_matches(word, possibilities, n=1)
    return ret[0] if len(ret) == 1 else np.nan

if len(sys.argv) > 1:
    movie_list = sys.argv[1]
    movie_ratings = sys.argv[2]
    output_file = sys.argv[3]
else:
    movie_list = 'movie_list.txt'
    movie_ratings = 'movie_ratings.csv'
    output_file = 'output.csv'


movie_list = pd.read_csv(movie_list, sep='\n', names=['movie_name'])
movie_ratings = pd.read_csv(movie_ratings)
movie_ratings = movie_ratings.sort_values(by=['title'])
movie_ratings['title'] = movie_ratings.apply(lambda x: check_closeness(x['title'], movie_list['movie_name']), axis=1)
movie_ratings = movie_ratings.groupby('title').mean().round(decimals=2).dropna().reset_index()
#print(movie_ratings)
movie_ratings.to_csv(output_file, index=False, header=True)