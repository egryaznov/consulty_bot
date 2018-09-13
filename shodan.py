import time
import datetime
import requests
import sys
import json
from nltk.stem import SnowballStemmer


telegram_timeout_sec = 1
logfile = open('/app/log.txt', 'a')
main_url = 'https://api.telegram.org/bot692098368:AAEAJgjs76mbN7L4q4sw3miBJmu8BeF-UyI/'
send_message_url = main_url + 'sendMessage'
get_updates_url = main_url + 'getUpdates'
qna_url = 'https://shodanapp.azurewebsites.net/qnamaker/knowledgebases/fc674829-efde-4a8f-b767-2d4349b8681e/generateAnswer'
MIN_WORD_LEN = 4
WORDS_IN_KEY = int(sys.argv[1]) if len(sys.argv) > 1 else 3
stemmer      = SnowballStemmer('russian')
print('stemmer loaded')
corpus = json.load(open('nalkod.json', 'rt'))
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


def prune(token):
    letters = [char for char in token.lower() if char in 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя-']
    return ''.join(letters)


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
        return ('', '', 'No answer')
    #
    stemmed_words = [stemmer.stem(prune(word)) for word in words]
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
        return (corpus[article]['no'], clause[article]['clauses'[clause]['no']], corpus[article]['clauses'][clause]['text'])
    return (-1, -1, False)


def log(message):
    print(message)
    timestamp = datetime.datetime.now()
    logfile.writelines(['[', str(timestamp), '] ', str(message), '\n'])
    logfile.flush()


def extract_answer(json):
    answers = json['answers']
    if len(answers) > 0:
        return answers[0]['answer']
    else:
        return 'Internal error: ' + str(json)


def ask(question):
    json_question = {'question': question, 'userId' : 'Default', 'isTest': True}
    json_headers = {'Content-Type': 'application/json; charset=utf-8',
                    'Authorization': 'endpointKey efd34d6a-b60b-477f-b1af-91daa3af9013'}
    r = requests.post(qna_url, json=json_question, headers=json_headers)
    log('Asked Shodan ' + str(r.json()))
    return extract_answer(r.json())


def greetings():
    greeting = 'Привет! Я твой юридический советник, спроси меня про Водный Кодекс РФ. Например:\n'
    qna_pairs = ['* Кто входит в состав бассейновых советов?\n',
                 '* Что является гидрографической единицей?\n',
                 '* В каких случаях может быть приостановлено водопользование?\n',
                 '* Что должен содержать договор водопользования?\n',
                 '* Кем ещё регулируются водные отношения?\n']
    qna_pairs.insert(0, greeting)
    respond(chat_id, '\n'.join(qna_pairs))


def fetch_last_update(offset, limit=2, timeout=telegram_timeout_sec):
    json = {'offset': offset, 'limit': limit, 'timeout' : timeout}
    json_updates = requests.get(get_updates_url, data=json).json()
    log('fetching last update: ' + str(json_updates['ok']))
    return json_updates['result'][-1]


def respond(chat_id, text):
    json = {'chat_id': chat_id, 'text': text}
    requests.get(send_message_url, data=json)
    log('Sending "%s" to %d' % (text, chat_id))


json_updates = requests.get(get_updates_url).json()
if json_updates['ok']:
    log('Fetched updates OK')
else:
    log('Error occured when fetching updates, app stops')
    log(json_updates)
    exit(1)
# Starting main cycle
last_update = json_updates['result'][-1]
while True:
    time.sleep(telegram_timeout_sec)
    last_update_id = last_update['update_id']
    last_update = fetch_last_update(last_update_id)
    if last_update_id != last_update['update_id']:
        # we have a new message
        log('Hurray! New message!')
        chat_id = last_update['message']['chat']['id']
        question = last_update['message']['text']
        # Answer to users question
        if question == '/start':
            answer = greetings()
        else:
            # Ask Microsoft QnA service
            answer = ask(question)
            if answer == 'No good match found in KB.':
                words = [stemmer.stem(prune(word.lower())) for word in question.split(' ')]
                respond(chat_id, 'Статья %s, Пункт %s:\n %s' % search_in_corpus(words, WORDS_IN_KEY))
            # Send answer to telegram
            respond(chat_id, answer)
