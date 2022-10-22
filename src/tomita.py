import argparse
import os
import subprocess
import traceback
import json
import tqdm

import modules.common

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
TOMITA_INPUT_PATH = os.path.join(SCRIPT_DIR, '../tomita/tomita/input.txt')

DOCKER_CONN = "root@localhost"
DOCKER_PORT = 2022

# Запускает томита парсер
def run_tomita(text):
    try:
        # Сохраняем текст в файл
        with open(TOMITA_INPUT_PATH, 'w') as f:
            f.write(text)
    except:
        print('Failed to write data:')
        print(traceback.format_exc())
        return None

    try:
        # Запускаем томита-парсер в докер контейнере по SSH
        proc = subprocess.Popen([
            '/usr/bin/ssh', DOCKER_CONN, '-p', str(DOCKER_PORT),
            'cd /data; tomita-parser config.proto'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()

        if proc.returncode != 0:
            print(f'Tomita failed with non-zero code {proc.returncode}')
            print(stderr.decode('utf-8'))
            return None

        return stdout.decode('utf-8')
    except:
        print('Failed to run Tomita:')
        print(traceback.format_exc())
        return None

# Находит факты и заменяет в их предложениях на униграммы
def replace_facts(obj):
    sentenses = obj[0]['Lead']
    processed = []
    for sentense in sentenses:
        text = sentense['Text']
        facts = set()
        for span in sentense['Span']:
            lemma = span['Lemma']
            length = len(lemma)

            # Нормализуем факт
            lemma = modules.common.clear_lemma(lemma)

            facts.add(lemma)

            # Если получившееся строка меньше исходной, дополним пробелами
            lemma = lemma.ljust(length, ' ')

            # Заменяем факт в исходном тексте на нормализованный
            start = span['StartChar']
            stop = span['StopChar']
            text = text[:start] + lemma + text[stop:]
        processed.append({
            'keys': list(facts),
            'text': text
        })
    return processed

# Находит факты и сохраняет их
def find_facts(obj):

    found_facts = {}

    fact_groups = obj[0]['FactGroup']
    for fact_group in fact_groups:
        fact_type = fact_group['Type']
        facts = fact_group['Fact']
        for fact in facts:
            name = fact['Field'][0]['Value']
            name = modules.common.clear_lemma(name)
            found_facts[name] = fact_type

    return found_facts

# Сохраняет факт в базу
def save_facts(facts, collection):
    for fact, type in facts.items():
        collection.update_one(
            {'_id': fact},
            {
                '$set': {'type': type},
                '$inc': {'count': 1}
            },
            upsert=True
        )

# Парсит вывод томиты
def parse_tomita_output(output):
    #print(output)
    obj = json.loads(output)
    sentenses = replace_facts(obj)
    facts = find_facts(obj)
    #print('---')
    return sentenses, facts

# Парсит статью
def process_news(news):
    out = run_tomita(news)
    if len(out) > 0:
        return parse_tomita_output(out)
    else:
        # Ничего не найдено, томита возвращает пустую строку
        return [], []

def main():
    db = modules.common.get_db()
    news_cl = db['news']
    sentenses_cl = db['sentenses']
    facts_cl = db['facts']

    if sentenses_cl.count_documents({}) > 0 or facts_cl.count_documents({}) > 0:
        print('WARNING! Overwrite existing data')
        sentenses_cl.drop()
        facts_cl.drop()

    news_count = news_cl.count_documents({})
    view = news_cl.find({})
    for news in tqdm.tqdm(view, total=news_count):
        sentenses, facts = process_news(news['text'])

        # Добавление предложения с фактами в базу
        if sentenses:
            sentenses_cl.insert_one({
                'news_id': news['_id'],
                'news_date': news['date'],
                'sentenses': sentenses
            })

        # Добавление фактов в базу
        if facts:
            save_facts(facts, facts_cl)


# Парсинг аргументов командной строки
def parse_args():
    parser = argparse.ArgumentParser(description='Find people and places in news using Tomita')
    return parser.parse_args()

if __name__ == '__main__':
    cfg = parse_args()
    main()
