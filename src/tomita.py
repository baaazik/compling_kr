import argparse
import os
import subprocess
import traceback

import common

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
TOMITA_INPUT_PATH = os.path.join(SCRIPT_DIR, '../tomita/tomita/input.txt')

DOCKER_CONN = "root@localhost"
DOCKER_PORT = 2022

# Обрабатывает текст с помощью томита-парсера
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


def main():
    # db = common.get_db()
    # news_cl = db['news']
    text = run_tomita(
        """
        Какой-то текст.
        Бочаров Андрей и Илья Кошкарев пошли Казанский кафедральный собор, а затем в речной порт.
        Еще текст.
        """
    )
    print(text)

# Парсинг аргументов командной строки
def parse_args():
    parser = argparse.ArgumentParser(description='Find people and places in news using Tomita')
    return parser.parse_args()

if __name__ == '__main__':
    cfg = parse_args()
    main()
