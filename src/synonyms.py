import argparse
from modules import word2vec
import modules.common as common

def main():
    model = word2vec.get_word2vec_model()

    persons = ["Андрей Бочаров", "Владимир Марченко", "Бочаров", "Вячеслав Черепахин", "Виталий Лихачев",
               "Валерий Бахин",  "Анатолий Себелев", "Денис Долгов ", "Николай Алимов", "Ольга Зубарева"]

    for p in persons:
        p = common.clear_lemma(p)
        print(f'Синонимы для {p}')
        model.findSynonyms(p, 5).show()
        print('----')

# Парсинг аргументов командной строки
def parse_args():
    parser = argparse.ArgumentParser(description='Find synonyms using word2vec')
    return parser.parse_args()

if __name__ == '__main__':
    cfg = parse_args()
    main()
