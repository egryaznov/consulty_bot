import time
import datetime
import requests

main_url = 'https://api.telegram.org/bot692098368:AAEAJgjs76mbN7L4q4sw3miBJmu8BeF-UyI/'
send_message_url = main_url + 'sendMessage'
get_updates_url = main_url + 'getUpdates'
qna_url = 'https://shodanapp.azurewebsites.net/qnamaker/knowledgebases/fc674829-efde-4a8f-b767-2d4349b8681e/generateAnswer'
log = open('log.txt', 'a')


def log(message):
    timestamp = datetime.datetime.now()
    log.writelines([timestamp, message, '\n'])
    log.flush()


def extract_answer(json):
    answers = json['answers']
    if len(answers) > 0:
        return answers[0]['answer']
    else:
        return 'Internal error: ' + json


def ask(question):
    json_question = {'question': question, 'userId' : 'Default', 'isTest': True}
    json_headers = {'Content-Type': 'application/json; charset=utf-8',
                    'Authorization': 'endpointKey efd34d6a-b60b-477f-b1af-91daa3af9013'}
    r = requests.post(qna_url, json=json_question, headers=json_headers)
    log('Asked Shodan ' + r.json())
    return extract_answer(r.json())


def fetch_last_update(offset, limit=2, timeout=3):
    json = {'offset': offset, 'limit': limit, 'timeout' : timeout}
    json_updates = requests.get(get_updates_url, data=json)
    log('fetching last update: ' + json_updates['ok'])
    return json_updates['result'][-1]


def respond(chat_id, text):
    json = {'chat_id': chat_id, 'text': text}
    requests.get(send_message_url, data=json)
    log('Sending "%s" to %d' % text, chat_id)


json_updates = requests.get(get_updates_url)
if json_updates['ok']:
    log('Fetched updates OK')
else:
    log('Error occured when fetching updates, app stops')
    log(json_updates)
    exit(1)
# Starting main cycle
last_update = json_updates['result'][-1]
while True:
    time.sleep(3)
    last_update_id = last_update['update_id']
    last_update = fetch_last_update(last_update_id)
    if last_update_id != last_update['update_id']:
        # we have a new message
        chat_id = last_update['message']['chat']['id']
        question = last_update['message']['text']
        # Ask Microsoft QnA service
        answer = ask(question)
        # Send answer to telegram
        respond(chat_id, answer)
