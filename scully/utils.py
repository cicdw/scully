from functools import lru_cache
from os.path import dirname, join
import pandas as pd
import sqlite3
from string import punctuation


DB_FILE = join(dirname(__file__), '../data/xfiles_db.sqlite')


def clean_characters(char):
    if 'SCULLY' in char:
        return 'SCULLY'
    elif 'MULDER' in char:
        return 'MULDER'
    elif 'CIGARETTE' in char:
        return 'CIGARETTE SMOKING MAN'
    return char


@lru_cache(maxsize=1024)
def clean_word(wrd):
    clear = ["'", '-', '\x92', ',', '\x97', '.', '\x94'] + list(punctuation)
    clean = wrd.lower().strip().translate({ord(c): None for c in clear})
    return clean


def db_to_dataframe(db_file=DB_FILE, clean=True):
    conn = sqlite3.connect(db_file)
    df = pd.read_sql_query('SELECT * FROM XFILES', conn)
    conn.close()
    if clean is True:
        df['CHARACTER'] = df.CHARACTER.apply(clean_characters)
        df.drop(df.loc[df.CHARACTER == 'CUT TO'].index, inplace=True)
    return df
