from bs4 import BeautifulSoup
import json
from os.path import dirname, join
import re
import requests
import sys


BASE_URL = 'http://www.j-archive.com/'
FILENAME = join(dirname(__file__), '../data/jeopardy_questions.json')


def soupify_url(url):
    '''Given an url (string), retrieves html and
    returns a BeautifulSoup object'''

    print('soupifying {}'.format(url))
    if not url.startswith('http://'):
        url = BASE_URL + url
    html = requests.get(url)
    if html.ok:
        soup = BeautifulSoup(html.text, 'html.parser')
        return soup
    else:
        raise ValueError("{} could not be retrieved.".format(url))


def _parse_clue_id(clue, categories):
    clue_id = clue['id']
    return categories[int(clue_id.split('_')[2]) - 1]


def create_game(game_soup):
    rounds = game_soup.find_all('table', {'class' : 'round'})
    for j_round in rounds:
        categories = [c.text for c in j_round.find_all('td', {'class' : 'category_name'})]
        clues = j_round.find_all('td', {'class': 'clue'})
        for clue in clues:
            clue_info = clue.find('td', {'class': 'clue_text'})
            clue_text = clue_info.text
            clue_cat = _parse_clue_id(clue_info, categories=categories)

    return 'game data'


def create_game_list(season_soup):
    games = []
    for link in season_soup.find_all('a'):
        if 'showgame' in link['href']:
            game_soup = soupify_url(link['href'])
            games.append((link.contents[0], create_game(game_soup)))
    return games


def create_season_list(main_page, m=None):
    seasons = []
    m = float('inf') if m is None else m
    counter = 0
    for link in main_page.find_all('a')[3:]:
        url = link.get('href')
        if 'showseason' in (url or ''):
            seasons.append((link.contents[0], url))
            counter += 1
            if counter > m:
                break

    return seasons


if __name__ == '__main__':
    try:
        max_seasons = int(sys.argv[-1])
    except ValueError:
        max_seasons = None

    jeopardy = {}
    main_page = soupify_url(BASE_URL + 'listseasons.php')
    seasons = create_season_list(main_page, m=max_seasons)
    games = []

    for season, season_link in seasons:
        print(season)
        season_soup = soupify_url(BASE_URL + season_link)
        games.extend(create_game_list(season_soup))

    for game, data in games:
        jeopardy[game] = data
#
#    with open(FILENAME, 'w') as f:
#        json.dump(xfiles, f)
