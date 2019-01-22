import collections
import requests
from lxml import etree
import string
import rhymes_db
import matplotlib.pyplot as plt
import time
import datatypes
from typing import List

# The Sonnet's expected rhyme form is: ABAB CDCD EFEF GG
# This list contains tuples encoding that: the 0th row should rhyme with the 2nd row, the 1st with the 3rd row, and so
# on.
SONNET_EXPECTED_RHYMES = [(0, 2), (1, 3), (4, 6), (5, 7), (8, 10), (9, 11), (12, 13)]
GUTENBERG_SONNETS_URL = 'http://www.gutenberg.org/files/1041/1041-h/1041-h.htm'
DATAMUSE_API_URL = 'https://api.datamuse.com/words?rel_rhy='
SonnetStats = collections.namedtuple('SonnetStats', ['num_rhymes', 'average_rhyme_score'])


def pull_sonnets() -> List[List[str]]:
    """Retrieve Shakespeare's sonnets from Gutenberg and return them as lists of strings."""
    sonnets_html = requests.get(GUTENBERG_SONNETS_URL).content
    html = etree.HTML(sonnets_html)
    poems_elements = [element for element in html.xpath("//p[@class='poem']")]
    return [[text.strip() for text in element.itertext() if text.strip()] for element in poems_elements]


def get_sonnet_stats(poem: List[str]) -> SonnetStats:
    """Returns sonnet stats for the given sonnet. This method assumes that the given sonnet has 14 lines."""
    poem_without_punctuation = [line.translate(str.maketrans('', '', string.punctuation)) for line in poem]
    last_words = [line.split()[-1] for line in poem_without_punctuation]
    rhyme_score_counter = []

    for line_num1, line_num2 in SONNET_EXPECTED_RHYMES:
        word1 = last_words[line_num1]
        word2 = last_words[line_num2]
        rhyme_match = [rhyme for rhyme in find_rhyming_words(word1) if rhyme.word2 == word2]
        if len(rhyme_match):
            rhyme_score_counter.append(float(rhyme_match[0].score))

    num_rhymes_found = len(rhyme_score_counter)
    rhyme_score_average = sum(rhyme_score_counter) / float(num_rhymes_found)

    return SonnetStats(num_rhymes=num_rhymes_found, average_rhyme_score=rhyme_score_average)


def find_rhyming_words(word: str) -> List[datatypes.Rhyme]:
    """Returns a list of Rhymes for which word == Rhyme.word1."""
    with rhymes_db.create_db_connection() as conn:
        if not rhymes_db.datamuse_rhymes_populated(conn, word):
            with conn:
                rhymes_db.populate_datamuse_rhymes(conn, word, lookup_datamuse_rhymes(word))
        return rhymes_db.find_datamuse_rhymes(conn, word)


def lookup_datamuse_rhymes(word: str) -> List[datatypes.Rhyme]:
    """Queries datamuse to create a list of Rhymes."""
    rhyme_list = requests.get(DATAMUSE_API_URL + word).json()
    return [datatypes.Rhyme(word1=word, word2=rhyme['word'], score=rhyme['score'], num_syllables=rhyme['numSyllables'])
            for rhyme in rhyme_list if 'score' in rhyme]


def histogram_sonnet_scores(sonnet_stats: List[SonnetStats]) -> None:
    """Creates visualizations for a list of SonnetStats."""
    rhymes_found_list = [sonnet_stat.num_rhymes for sonnet_stat in sonnet_stats]
    rhyme_score_list = [sonnet_stat.average_rhyme_score for sonnet_stat in sonnet_stats]

    fig, axs = plt.subplots(2, 1, tight_layout=True)

    axs[0].hist(rhymes_found_list, bins=6, color='darkslategrey', alpha=1.0)
    axs[0].set_title('Sonnet rhyming lines found')

    axs[1].hist(rhyme_score_list, bins=6, color='darkmagenta', alpha=1.0)
    axs[1].set_title('Sonnet mean rhyme scores')

    timestamp = time.time()

    plt.show()
    fig.savefig(('sonnets_{0}.svg'.format(timestamp)))


def main():
    sonnets = pull_sonnets()
    sonnet_stats = [get_sonnet_stats(sonnet) for sonnet in sonnets if len(sonnet) == 14]
    histogram_sonnet_scores(sonnet_stats)


if __name__ == '__main__':
    main()
