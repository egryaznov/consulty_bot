# consulty_bot
Телеграм чат-бот, отвечающий на ваши вопросы по Водному Кодексу РФ.

Ссылка: [t.me/consultybot](t.me/consultybot)

Бот интегрируется с QnA Maker Service от Microsoft'a для обработки вопросов на русском языке.

# Инструкция по запуску проекта
1. Установить третью версию Python: https://www.python.org/ftp/python/3.7.0/python-3.7.0.exe
2. Скачать все необходимые библиотеки командами:

```pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org nltk```

```pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org json```

```pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org requests```

3. Запустить бота командой:

```python shodan.py```

**Внимание!** Перед запуском проверьте, что у вас есть доступ к api.telegram.org

Из-за блокировки Telegram роскомпозором его API может быть недоступно.

# Описание аргументов к скрипту shodan.py
Скрипт принимает на вход 4 аргумента:

```python shodan.py WORDS_IN_KEY MIN_PASSABLE_SCORE USE_COSINE PROXY_URL```

WORDS_IN_KEY       -- Кол-во слов в ключе словарей vocabN.json. По-умолчанию равно трём.

MIN_PASSABLE_SCORE -- Наименьший допустимый счет ответа от QnA. По-умолчанию равно 75.

USE_COSINE         -- Использовать ли [косинусный коэффицент](https://ru.wikipedia.org/wiki/%D0%9A%D0%BE%D1%8D%D1%84%D1%84%D0%B8%D1%86%D0%B8%D0%B5%D0%BD%D1%82_%D0%9E%D1%82%D0%B8%D0%B0%D0%B8) для сравнения строк, по-умолчанию True. С этим коэффициентом поиск похожих статей работает лучше.

PROXY_URL          -- Ссылка на прокси-сервер для обхода блокировки Telegram. По-умолчанию пусто.

# Запуск с прокси:

```python shodan.py 3 75 True http://123.123.123.123:0000```
