import json
from nltk.stem import SnowballStemmer


MIN_WORD_LEN = 4
WORDS_IN_KEY = 3
stemmer      = SnowballStemmer('russian')
raw          = open('nalkod.json', 'rt')
vocab        = {}
corpus       = json.load(raw)


def phrases(sentence, n=2):
    words   = sentence.split(' ')
    phrases = []
    first   = 0
    last    = min(n, len(words))
    while last <= len(words):
        phrases.append(words[first:last])
        first += 1
        last  += 1
    return phrases


def prune(token):
    letters = [char for char in token.lower() if char in 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя-']
    return ''.join(letters)


def check_length(words):
    result = True
    for word in words:
        result &= len(word) >= MIN_WORD_LEN
    return result


def normalize(phrase):
    normalized = [stemmer.stem(prune(word)) for word in phrase]
    long_enough = check_length(normalized)
    return (' '.join(normalized), long_enough)


i = 0
print('codex loaded, generating vocab, n = ', WORDS_IN_KEY)
for article in corpus:
    j = 0
    for clause in article['clauses']:
        bag = phrases(clause['text'], WORDS_IN_KEY)
        for phrase in bag:
            root, long_enough = normalize(phrase)
            if long_enough:
                if root in vocab:
                    vocab[root].append([i, j])
                else:
                    vocab[root] = [[i, j]]
        j += 1
    i += 1
print('vocab completed, saving')
# словарь сформирован
dump = open('vocab_nalkod%d.json' % (WORDS_IN_KEY), 'wt')
raw = str(vocab).replace("'", '"')
dump.write(raw)
dump.flush()
dump.close()
print('done')
