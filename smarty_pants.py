# python smarty_pants.py corpus.json
import sys
import json
from nltk.stem import SnowballStemmer


MIN_WORD_LEN = 4
WORDS_IN_KEY = 3
if len(sys.argv) == 1:
    print('Не указан путь к размеченному корпусу кодекса')
    exit(1)
stemmer = SnowballStemmer('russian')
CORPUS_JSON_FILENAME = sys.argv[1]
print('stemmer loaded')
corpus = json.load(open(CORPUS_JSON_FILENAME, 'rt'))
print('corpus loaded')
vocab1 = json.load(open('vocab1.json', 'rt'))
print('vocab1 loaded')
vocab2 = json.load(open('vocab2.json', 'rt'))
print('vocab2 loaded')
vocab3 = json.load(open('vocab3.json', 'rt'))
print('vocab3 loaded')


def add_frequency(union, clauses):
    clause_found = False
    for clause in clauses:
        for j in range(0, len(union)):
            freq, u_clause = union[j]
            if clause == u_clause:
                union[j] = (freq + 1, u_clause)
                clause_found = True
        if not clause_found:
            union.append((1, clause))


def phrases(words, n):
    phrases = []
    first   = 0
    last    = min(n, len(words))
    while last <= len(words):
        phrases.append(words[first:last])
        first += 1
        last  += 1
    return phrases


def get_vocab(n):
    if n == 1:
        return vocab1
    elif n == 2:
        return vocab2
    elif n == 3:
        return vocab3
    return False


def search_in_corpus(words, n):
    if n == 0:
        return ('No answer', -1, -1)
    #
    stemmed_words = [stemmer.stem(word) for word in words]
    bags = phrases(stemmed_words, n)
    vocab = get_vocab(n)
    union = []
    for phrase in bags:
        key = ' '.join(phrase)
        if key in vocab:
            add_frequency(union, vocab[key])
    union.sort(key=lambda x: x[0], reverse=True)
    if len(union) > 0:
        article_and_clause = union[0][1]
        article = article_and_clause[0]
        clause = article_and_clause[1]
        return (corpus[article]['clauses'][clause]['text'], article, clause)
    return (False, -1, -1)


words = []
for i in range(1, len(sys.argv)):
    words.append(sys.argv[i])
n = WORDS_IN_KEY
response = False
print('start answering')
while not response:
    response, article, clause = search_in_corpus(words, n)
    n -= 1
print('Статья %d, Пункт %d:\n%s' % (article, clause, response))
