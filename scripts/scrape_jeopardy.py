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


def _parse_clue_answer(clue):
    hint = clue['onmouseover']
    p = re.compile("<em.*\">(.*?)</em>")
    ans = p.findall(hint)[0]
    return ans


def _parse_clue_id(clue, categories):
    is_not_single_round = len(categories) > 7
    clue_id = clue['id']
    which_round = clue_id.split('_')[1]
    if which_round == 'J':
        which_cat = clue_id.split('_')[2]
        cat = categories[int(which_cat) - 1]
    elif which_round == 'DJ':
        which_cat = clue_id.split('_')[2]
        cat = categories[6 * is_not_single_round + int(which_cat) - 1]
    else:
        cat = categories[-1]
    return cat


def create_game(game_soup):
    game_data = []
    rounds = game_soup.find_all('table', {'class' : 'round'})
    rounds.extend(game_soup.find_all('table', {'class' : 'final_round'}))
    categories = [c.text for c in game_soup.find_all('td', {'class' : 'category_name'})]
    clues = [div for div in game_soup.find_all('div') if 'onmouseover' in div.attrs]
    for clue in clues:
        clue_info = clue.find_next('td', {'class': 'clue_text'})
        if clue_info is None:
            continue
        clue_text = clue_info.text
        clue_cat = _parse_clue_id(clue_info, categories=categories)
        clue_ans = _parse_clue_answer(clue)
        game_data.append((clue_cat, clue_text, clue_ans))

    return game_data


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

    for season, season_link in seasons[:max_seasons]:
        print(season)
        season_soup = soupify_url(BASE_URL + season_link)
        games.extend(create_game_list(season_soup))

    for game, data in games:
        jeopardy[game] = data

    with open(FILENAME, 'w') as f:
        json.dump(jeopardy, f)
