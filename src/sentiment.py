import argparse
import os
import re
import random
import pickle
import pandas as pd
# from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tag import pos_tag
from nltk.tokenize import word_tokenize
from nltk import FreqDist, classify, NaiveBayesClassifier
import pymorphy2
import tqdm

from modules import common

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
DATA_DIR = os.path.realpath(os.path.join(SCRIPT_DIR, '../data/'))
TRAIN_FILE = os.path.join(DATA_DIR, 'train_processed.csv')
CLASSIFIER_FILE = os.path.join(DATA_DIR, 'classifier.pickle')

morph = pymorphy2.MorphAnalyzer()

punctuation = '!"#$%&\'()*+,-./:;<=>?@[\\]^`{|}~«»”—'
TRANSLATION = str.maketrans('', '', punctuation)


# Обрабатывает текст, удаляет шум, токенизирует
def prepare_text(text, stop_words):
    # Удаляем ссылки
    text = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+#]|[!*\(\),]|'\
                       '(?:%[0-9a-fA-F][0-9a-fA-F]))+','', text)
    # Удаляем @ссылки
    text = re.sub("(@[A-Za-z0-9_]+)","", text)

    # Удаляем оставшиеся знаки препинания (кроме "_")
    text = text.translate(TRANSLATION)

    # Токенизируем
    tokens = word_tokenize(text, language='russian')
    processed_tokens = []
    for token in tokens:
        # Приводим в начальную форму
        token = morph.parse(token)[0].normal_form
        if token not in stop_words:
            processed_tokens.append(token)

    return processed_tokens


# Разделяет датасет на отдельные массивы текстов для каждого класса
def separate_dataset_for_classes(df):
    keys = df['sentiment'].unique()
    data = {}
    for key in keys:
        data[key] = df[df['sentiment'] == key]['text']
    return data


# Обрабатывает массив (Series, df, ...) слов
def prepare_text_list(lines, stop_words):
    return [prepare_text(row, stop_words) for row in tqdm.tqdm(lines)]


# Обрабатывает данные по всем классам
def prepare_text_data(data, stop_words):
    new_data = {}
    print('Processing text...')
    for key, dataset in data.items():
        print(f'Class: {key}')
        new_data[key] = prepare_text_list(dataset, stop_words)
    return new_data


def get_dict(text):
    return {token: True for token in text}

def convert_to_classifier_format(data):
    new_data = []
    for key, dataset in data.items():
        new_dataset = [(get_dict(text), key) for text in dataset]
        new_data += new_dataset

    return new_data


# Обучает модель
def train():
    df = pd.read_csv(TRAIN_FILE)
    stop_words = stopwords.words('russian')

    # Подготовка данных
    data = separate_dataset_for_classes(df)
    data = prepare_text_data(data, stop_words)

    # Представляем данные в виде, необходимым для классификатора
    data = convert_to_classifier_format(data)
    random.shuffle(data)

    # Обучение модели
    print('Training...')
    classifier = NaiveBayesClassifier.train(data)
    print('Done')

    # Сохранение
    with open(CLASSIFIER_FILE, 'wb') as f:
        pickle.dump(classifier, f)


# Определяет тональность переданного текста
def evaluate(text):
    if not os.path.exists(CLASSIFIER_FILE):
        raise FileNotFoundError('Classifier does not exists')

    with open(CLASSIFIER_FILE, 'rb') as f:
        classifier = pickle.load(f)

    stop_words = stopwords.words('russian')
    tokens = prepare_text(text, stop_words)
    sentiment = classifier.classify(get_dict(tokens))
    return sentiment


def main():
    train()

# Парсинг аргументов командной строки
def parse_args():
    parser = argparse.ArgumentParser(description='Text sentiment analysis')
    return parser.parse_args()

if __name__ == '__main__':
    cfg = parse_args()
    main()
