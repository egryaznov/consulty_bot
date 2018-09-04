import time
import datetime
import requests


telegram_timeout_sec = 1
logfile = open('log.txt', 'a')
main_url = 'https://api.telegram.org/bot692098368:AAEAJgjs76mbN7L4q4sw3miBJmu8BeF-UyI/'
send_message_url = main_url + 'sendMessage'
get_updates_url = main_url + 'getUpdates'
qna_url = 'https://shodanapp.azurewebsites.net/qnamaker/knowledgebases/fc674829-efde-4a8f-b767-2d4349b8681e/generateAnswer'


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


def download_kb_entries():
    result = []
    json_headers = {'Ocp-Apim-Subscription-Key' : 'dd5d9813819c4943aa2ff8f7a520455d'}
    r = requests.get('https://westus.api.cognitive.microsoft.com/qnamaker/v4.0/knowledgebases/fc674829-efde-4a8f-b767-2d4349b8681e/prod/qna', headers=json_headers)
    if r.ok:
        kb_entries = r.json()['qnaDocuments']
        for json_entry in kb_entries:
            result.append(json_entry['questions'][0])
    # we done here
    return result


def pluck(array, length):
    return array[:length]


def greetings(chat_id, n_questions=10):
    greeting = 'Привет! Я твой юридический советник, спроси меня про Водный Кодекс РФ. Например:'
    qna_pairs = pluck(download_kb_entries(), n_questions)
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
        chat_id = last_update['message']['chat']['id']
        question = last_update['message']['text']
        # Answer to users question
        if question == '/start':
            answer = greetings(chat_id)
        else:
            # Ask Microsoft QnA service
            answer = ask(question)
            # Send answer to telegram
            respond(chat_id, answer)
