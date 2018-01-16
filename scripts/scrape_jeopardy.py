from bs4 import BeautifulSoup
import json
from os.path import dirname, join
import requests


BASE_URL = 'http://www.j-archive.com/'
FILENAME = join(dirname(__file__), '../data/jeopardy_questions.json')


def soupify_url(url):
    '''Given an url (string), retrieves html and
    returns a BeautifulSoup object'''

    html = requests.get(url)
    if html.ok:
        soup = BeautifulSoup(html.text, 'html.parser')
        return soup
    else:
        raise ValueError("{} could not be retrieved.".format(url))


def create_game(game_soup):
    return None


def create_game_list(season_soup):
    games = []
    for link in seasons.find_all('a'):
        if 'showgame' in link['href']:
            game_soup = soupify_url(link['href'])
            games.append((link.contents[0], create_game(game_soup)))
    return games


def create_season_list(main_page):
    seasons = []
    for link in main_page.find_all('a')[3:]:
        url = link.get('href')
        if 'showseason' in (url or ''):
            seasons.append((link.contents[0], url))

    return seasons


if __name__ == '__main__':
    jeopardy = {}
    main_page = soupify_url(BASE_URL + 'listseasons.php')
    seasons = create_season_list(main_page)
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
