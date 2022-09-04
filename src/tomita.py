import argparse
import os
import subprocess
import traceback
import json
import string
import ctypes

import common

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
TOMITA_INPUT_PATH = os.path.join(SCRIPT_DIR, '../tomita/tomita/input.txt')

DOCKER_CONN = "root@localhost"
DOCKER_PORT = 2022

TRANSLATION = str.maketrans('', '', string.punctuation)

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

def normalize_lemma(lemma):
    return lemma \
        .lower() \
        .translate(TRANSLATION) \
        .replace(' ', '_')

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
            lemma = normalize_lemma(lemma)

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

# Парсит вывод томиты
def parse_tomita_output(output):
    obj = json.loads(output)
    sentenses = replace_facts(obj)
    print(sentenses)

def main():
    # db = common.get_db()
    # news_cl = db['news']
    out = run_tomita(
        """Какой-то текст.
Бочаров Андрей, Андрей Бочаров, еще один Андрей Бочаров и Илья Кошкарев пошли Казанский кафедральный собор, а затем в речной порт.
Еще текст.
Андрей Бочаров посетил Сергея Губанова в доме павлова."""
    )
    # print(out)
    parse_tomita_output(out)

# Парсинг аргументов командной строки
def parse_args():
    parser = argparse.ArgumentParser(description='Find people and places in news using Tomita')
    return parser.parse_args()

if __name__ == '__main__':
    cfg = parse_args()
    main()
