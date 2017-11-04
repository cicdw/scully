from bs4 import BeautifulSoup
import json
import requests
import sys


BASE_URL = 'http://www.insidethex.co.uk/'
FILENAME = 'xfiles_dialogue.json'


def soupify_url(url):
    '''Given an url (string), retrieves html and
    returns a BeautifulSoup object'''

    html = requests.get(url)
    if html.ok:
        soup = BeautifulSoup(html.text, 'html.parser')
        return soup
    else:
        raise ValueError("{} could not be retrieved.".format(url))


def create_dialogue_list(episode):
    '''Given a beautifulSoup object representing an episode page,
    returns a list of tuples (character, words) of the dialogue from that
    episode'''

    convos = episode.find_all('b') or episode.find_all('span', {'class': 'char'})
    dialogue = []
    for item in convos:
        who = item.text.rstrip(':')
        what = str(item.next_sibling)
        dialogue.append((who, what))
    return dialogue


def create_episode_list(main_page):
    '''Given the main page BeautifulSoup object, creates a list of episodes
    (episode_name, episode_url)'''

    episodes = []
    for link in main_page.find_all('a'):
        url = link.get('href')
        if 'transcrp/scrp' in (url or ''):
            episodes.append((link.contents[0], url))

    return episodes


if __name__ == '__main__':
    try:
        max_eps = int(sys.argv[-1])
    except ValueError:
        max_eps = None

    xfiles = {}
    main_page = soupify_url(BASE_URL)
    episodes = create_episode_list(main_page)
    for ep in episodes[:max_eps]:
        print(ep[0])
        ep_soup = soupify_url(BASE_URL + ep[1])
        xfiles[ep[0]] = create_dialogue_list(ep_soup)

    with open(FILENAME, 'w') as f:
        json.dump(xfiles, f)
