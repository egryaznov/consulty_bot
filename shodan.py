# python    0           1              2              3           4
# python shodan.py WORDS_IN_KEY MIN_PASSABLE_SCORE USE_COSINE PROXY_URL
import time
import datetime
import requests
import sys
import json
from nltk.stem import SnowballStemmer
from similarity.cosine import Cosine


# Переводит строку 'true' или 'false' в булевое значение
def str_to_bool(text):
    return 'true' == text.lower()


PROXY_URL            = sys.argv[4] if len(sys.argv) > 4 else ''  # Ссылка на прокси
MIN_PASSABLE_SCORE   = int(sys.argv[2]) if len(sys.argv) > 2 else 75  # Наименьший допустимый счет ответа от QnA
MIN_WORD_LEN         = 4  # наимешньшая допустимая длина токена
USE_COSINE           = str_to_bool(sys.args[3]) if len(sys.argv) > 3 else True  # Использовать ли косинусный коэффицент для сравнения строк
WORDS_IN_KEY         = int(sys.argv[1]) if len(sys.argv) > 1 else 3  # кол-во слов в одном ключе
telegram_timeout_sec = 1
logfile              = open('/app/log.txt', 'a')
main_url             = 'https://api.telegram.org/bot692098368:AAEAJgjs76mbN7L4q4sw3miBJmu8BeF-UyI/'
send_message_url     = main_url + 'sendMessage'
get_updates_url      = main_url + 'getUpdates'
qna_url              = 'https://shodanapp.azurewebsites.net/qnamaker/knowledgebases/fc674829-efde-4a8f-b767-2d4349b8681e/generateAnswer'
stemmer              = SnowballStemmer('russian')
print('stemmer loaded')
corpus = json.load(open('nalkod.json', 'rt'))
print('corpus loaded')
vocab1 = json.load(open('vocab1.json', 'rt'))
print('vocab1 loaded')
vocab2 = json.load(open('vocab2.json', 'rt'))
print('vocab2 loaded')
vocab3 = json.load(open('vocab3.json', 'rt'))
print('vocab3 loaded')


# Выбирает наиболее похожий на вопрос пункт Кодекса
def choose_the_best_clause(union, question):
    if USE_COSINE:
        cos = Cosine(1)
        article_and_clause_no = []
        max_cosine = 0
        for ref in union:
            article, clause = ref[1]
            clause = corpus[article]['clauses'][clause]['text']
            cur_cos = cos.similarity(clause, question)
            if max_cosine < cur_cos:
                max_cosine = cur_cos
                article_and_clause_no = ref[1]
        return article_and_clause_no
    else:
        union.sort(key=lambda x: x[0], reverse=True)
        return union[0][1]


# Добавляет новый пункт Кодекса в список, из которого потом будет выбран наиболее похожий на вопрос пользователя
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


# Возвращает список из k n-кортежей последовательных слов из массива words
# Например: phrases(['Тут', 'был', 'Вася'], 2) = [['Тут', 'был'], ['был', 'Вася']]
def phrases(words, n):
    phrases = []
    first   = 0
    last    = min(n, len(words))
    while last <= len(words):
        phrases.append(words[first:last])
        first += 1
        last  += 1
    return phrases


# Удаляет из слова все символы, не являющиеся буквенными
def prune(token):
    letters = [char for char in token.lower() if char in 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя-']
    return ''.join(letters)


# Возвращает ассощиативный массив, который сопоставляет фразам из Кодекса номера их пунктов
def get_vocab(n):
    if n == 1:
        return vocab1
    elif n == 2:
        return vocab2
    elif n == 3:
        return vocab3
    return False


# Ищет наиболее подходящий под вопрос пункт Кодекса
def search_in_corpus(stemmed_words, question, n):
    if n == 0:
        return ('', '', 'No answer')
    #
    bags = phrases(stemmed_words, n)
    vocab = get_vocab(n)
    union = []
    for phrase in bags:
        key = ' '.join(phrase)
        if key in vocab:
            add_frequency(union, vocab[key])
    if len(union) > 0:
        article_and_clause = choose_the_best_clause(union, question)  # <-- HERE
        article = article_and_clause[0]
        clause = article_and_clause[1]
        return (corpus[article]['no'], corpus[article]['clauses'][clause]['no'], corpus[article]['clauses'][clause]['text'])
    return (-1, -1, False)


# Логирует сообщение в файл и в консоль. Для отладки.
def log(message):
    print(message)
    timestamp = datetime.datetime.now()
    logfile.writelines(['[', str(timestamp), '] ', str(message), '\n'])
    logfile.flush()


# Извлекает ответ из JSON, пришедшего от QnA maker'a
def extract_answer(json):
    answers = json['answers']
    if len(answers) > 0:
        return (answers[0]['answer'], answers[0]['score'])
    else:
        return 'Internal error: ' + str(json)


# Задаёт вопрос QnA maker'у
def ask(question):
    json_question = {'question': question, 'userId' : 'Default', 'isTest': True}
    json_headers = {'Content-Type': 'application/json; charset=utf-8',
                    'Authorization': 'endpointKey efd34d6a-b60b-477f-b1af-91daa3af9013'}
    r = requests.post(qna_url, json=json_question, headers=json_headers)
    log('Asked Shodan ' + str(r.json()))
    return extract_answer(r.json())


# Приветствует пользователя
def greetings():
    greeting = 'Привет! Я твой юридический советник, спроси меня про Налоговый Кодекс РФ. Например:'
    qna_pairs = ['* Что устанавливает налоговый кодекс?',
                 '* На что распространяется действие налогового кодекса?',
                 '* Когда истекает срок, исчисляемый годами?']
    qna_pairs.insert(0, greeting)
    respond(chat_id, '\n'.join(qna_pairs))


# Скачиваем последнее сообщение пользователя в телеграмме
def fetch_last_update(offset, limit=2, timeout=telegram_timeout_sec):
    json = {'offset': offset, 'limit': limit, 'timeout' : timeout}
    if len(PROXY_URL) > 0:
        json_updates = requests.get(get_updates_url, data=json, proxies={'https' : PROXY_URL}).json()
    else:
        json_updates = requests.get(get_updates_url, data=json).json()
    log('fetching last update: ' + str(json_updates['ok']))
    return json_updates['result'][-1]


# Отвечаем пользователю в телеграмме
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
        if 'message' not in last_update:
            log('unknown type of response: ' + str(last_update))
            continue
        chat_id = last_update['message']['chat']['id']
        question = last_update['message']['text']
        # Answer to users question
        if question == '/start':
            answer = greetings()
        else:
            # Ask Microsoft QnA service
            answer, score = ask(question)
            if answer == 'No good match found in KB.' or score < MIN_PASSABLE_SCORE:
                # Не нашли похожего вопроса в QnA maker'e, задействуем механизм ответа на неизвестный вопрос
                stemmed_words = [stemmer.stem(prune(word.lower())) for word in question.split(' ')]
                clause_content = False
                n = WORDS_IN_KEY
                # Ищем пункт в Кодексе, максимально похожий на вопрос пользователя
                while not clause_content:
                    article, clause, clause_content = search_in_corpus(stemmed_words, question, n)
                    n -= 1
                # Отвечаем соответственно
                if len(article) == 0:
                    respond(chat_id, 'Я не могу Вам помочь в этом вопросе.')
                else:
                    respond(chat_id, 'Статья %s Пункт %s\n %s' % (article, clause, clause_content))
            else:
                # Send answer to telegram
                respond(chat_id, answer)
