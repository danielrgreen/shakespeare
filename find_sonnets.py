
import nltk
from nltk.corpus import shakespeare
import xml.etree.ElementTree as ET
from nltk.corpus import gutenberg
import requests
from lxml import etree
# import pronouncing
import string
import numpy as np
import rhymes_db
# import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import time
import datatypes
from typing import List

# def load_shakespeare():
#     RJ = shakespeare.xml('r_and_j.xml')
#     hamlet = nltk.Text(nltk.corpus.gutenberg.words('shakespeare-hamlet.txt'))


def pull_sonnets():
    """Retrieve Shakespeare's sonnets from Gutenberg and return them as lists of strings."""
    sonnets_html = requests.get('http://www.gutenberg.org/files/1041/1041-h/1041-h.htm').content
    html = etree.HTML(sonnets_html)
    poems_elements = [element for element in html.xpath("//p[@class='poem']")]
    clean_sonnets = []
    for element in poems_elements:
        clean_sonnet = [text.strip() for text in element.itertext() if text.strip()]
        clean_sonnets.append(clean_sonnet)
    print('Sonnets retrieved')
    return clean_sonnets


def rhyme_scheme(poem):
    """Return a rhyme scheme for the given poem in the for of a list of numbers.
    Every number refers to the first line in the poem with which the given line rhymes.
    ['A', 'B', 'A', 'B'] -> [1, 2, 1, 2]
    ['A', 'B', 'C', 'A', 'B'] -> [1, 2, 3, 1, 2]
    """
    poem_without_punctuation = [line.translate(str.maketrans('', '', string.punctuation)) for line in poem]
    last_words = [line.split()[-1] for line in poem_without_punctuation]
    rhyme_coords_ABAB = np.array([0, 1, 4, 5, 8, 9])
    rhyme_score_counter = []

    for line in rhyme_coords_ABAB:
        last_word = last_words[line]
        possible_rhymes = find_rhyming_words(last_word)
        for rhyme in possible_rhymes:
            if rhyme.word2 == last_words[line+2]:
                rhyme_score_counter.append(tuple([1., float(rhyme.score)]))
            else:
                pass
    couplet_rhymes = find_rhyming_words(last_words[12])
    for rhyme in couplet_rhymes:
        if rhyme.word2 == last_words[13]:
            rhyme_score_counter.append(tuple([1., float(rhyme.score)]))
        else:
            pass

    rhymes_found = sum(rhyme[0] for rhyme in rhyme_score_counter)
    rhyme_score_average = sum(score[1] for score in rhyme_score_counter)/rhymes_found
    rhyme_score_summary = tuple([rhymes_found, rhyme_score_average])

    return last_words, rhyme_score_counter, rhyme_score_summary


def find_rhyming_words(word: str) -> List[datatypes.Rhyme]:
    with rhymes_db.create_db_connection() as conn:
        if not rhymes_db.datamuse_rhymes_populated(conn, word):
            with conn:
                rhymes_db.populate_datamuse_rhymes(conn, word, lookup_datamuse_rhymes(word))
        return rhymes_db.find_datamuse_rhymes(conn, word)


def lookup_datamuse_rhymes(word: str) -> List[datatypes.Rhyme]:
    rhyme_list = requests.get('https://api.datamuse.com/words?rel_rhy=' + word).json()
    return [datatypes.Rhyme(word1=word, word2=rhyme['word'], score=rhyme['score'], num_syllables=rhyme['numSyllables'])
            for rhyme in rhyme_list if 'score' in rhyme]


def histogram_sonnet_scores(sonnets):

    rhymes_found_list = []
    rhyme_score_list = []

    for i, j in enumerate(sonnets[0:60]):
        words, score, summary = rhyme_scheme(j)
        rhymes_found_list.append(summary[0])
        rhyme_score_list.append(summary[1])

    rhymes_found = np.asarray(rhymes_found_list)
    rhyme_scores = np.asanyarray(rhyme_score_list)

    print(rhymes_found)
    print(rhyme_scores)

    fig, axs = plt.subplots(2, 1, tight_layout=True)

    axs[0].hist(rhymes_found, bins=6, color='darkslategrey', alpha=1.0)
    axs[0].set_title('Sonnet rhyming lines found')

    axs[1].hist(rhyme_scores, bins=6, color='darkmagenta', alpha=1.0)
    axs[1].set_title('Sonnet mean rhyme scores')

    timestamp = time.time()

    plt.show()
    fig.savefig(('sonnets_{0}.svg'.format(timestamp)))

    return 0


def main():
    sonnets = pull_sonnets()
    # rhyme_scheme(sonnets[1])
    histogram_sonnet_scores(sonnets)


if __name__ == '__main__':
    main()
