import sys
import requests


def extract_answer(json):
    answers = json['answers']
    if len(answers) > 0:
        return answers[0]['answer']
    else:
        return 'Internal error: ' + json


def ask(question):
    url = 'https://shodanapp.azurewebsites.net/qnamaker/knowledgebases/fc674829-efde-4a8f-b767-2d4349b8681e/generateAnswer'
    json_question = {'question': question, 'top': 3, 'userId' : 'Default', 'isTest': True}
    json_headers = {'Content-Type': 'application/json; charset=utf-8',
                    'Authorization': 'endpointKey efd34d6a-b60b-477f-b1af-91daa3af9013'}
    r = requests.post(url, json=json_question, headers=json_headers)
    return extract_answer(r.json())


question = ''
while question != 'quit':
    print('Q: ', end='', flush=True)
    question = sys.stdin.readline()[:-1]
    print('A:', ask(question))