import argparse
import py4j.protocol
from modules import word2vec
import modules.common as common

model = None

def get_model():
    global model
    if model is None:
        model = word2vec.get_word2vec_model()
    return model

# Определяет синонимы для слова
def get_synonyms(word, count=5):
    model = get_model()
    word = common.clear_lemma(word)
    try:
        return model.findSynonyms(word, count)
    except py4j.protocol.Py4JJavaError:
        return None


def interactive_mode():
    while True:
            try:
                word = input('Input word: ')
                synonyms = get_synonyms(word)
                if synonyms:
                    print('Synonyms:')
                    synonyms.show()
                else:
                    print('No synonyms')
            except KeyboardInterrupt:
                break

def main(cfg):
    if cfg.interactive:
        interactive_mode()
        return

    print('Nothing to do')

# Парсинг аргументов командной строки
def parse_args():
    parser = argparse.ArgumentParser(description='Find synonyms using word2vec')
    parser.add_argument('-i', '--interactive', action=argparse.BooleanOptionalAction,
        help='Interactive mode')
    return parser.parse_args()

if __name__ == '__main__':
    cfg = parse_args()
    main(cfg)
