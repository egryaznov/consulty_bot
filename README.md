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

**Внимание!** Перед запуском проверьте, что у вас есть доступ к сайту api.telegram.org
Из-за блокировки Telegram роскомпозором API телеграма может быть недоступно.
