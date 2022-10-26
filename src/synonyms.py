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

class SynonymFinder:
    """Класс, осуществляющий поиск синонимов"""
    def __init__(self):
        self.model = word2vec.get_word2vec_model()

    def find(self, word, count=5):
        word = common.clear_lemma(word)
        try:
            return self.model.findSynonyms(word, count).toPandas()
        except py4j.protocol.Py4JJavaError:
            return None

# Работа в режиме интерактивной командной строки
def interactive_mode():
    finder = SynonymFinder()
    while True:
            try:
                word = input('Input word: ')
                synonyms = finder.find(word)
                if synonyms is not None:
                    print('Synonyms:')
                    print(synonyms)
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
