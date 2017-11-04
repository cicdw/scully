import json
from os.path import dirname, join
import sqlite3


SOURCE_JSON = join(dirname(__file__), '../data/xfiles_dialogue.json')
DB_FILE = join(dirname(__file__), '../data/xfiles_db.sqlite')


def load_data(filename=SOURCE_JSON):
    '''Loads JSON data and does a little cleaning.  Returns
    list of data that can be iterated over for inserting into db.'''

    with open(filename, 'r') as f:
        data = json.load(f)

    out = []
    for ep, dialogue in data.items():
        ep_name = ep.rstrip(' *').replace("'", "''")
        for num, mono in enumerate(dialogue):
            out.append((ep_name, num,
                        mono[0].replace("'", "''"),
                        mono[1].replace("'", "''")))
    return out


def insert_row(row):
    insert_cmd = '''INSERT INTO XFILES (EPISODE, CONVO_NUM, CHARACTER, TEXT) VALUES
    ('{0}', {1}, '{2}', '{3}')'''.format(*row)
    return insert_cmd


if __name__ == '__main__':
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    create_cmd = '''CREATE TABLE XFILES (EPISODE TEXT, CONVO_NUM INTEGER, CHARACTER TEXT, TEXT TEXT)'''
    c.execute(create_cmd)

    data = load_data()
    for row in data:
        c.execute(insert_row(row))

    conn.commit()
    conn.close()
