from pyspark.sql import SparkSession
import pyspark.sql.functions as f
from pyspark.ml.feature import Tokenizer, StopWordsRemover, CountVectorizer, \
     Word2Vec, Word2VecModel
import string
import os

from . import common

punctuation = '!"#$%&\'()*+,-./:;<=>?@[\\]^`{|}~'
TRANSLATION = str.maketrans('', '', punctuation)

_SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
WORD2VEC_DIR = os.path.realpath(os.path.join(_SCRIPT_DIR, '../../word2vec/'))

# Инициализация Spark
def init_spark_mongo():
    return SparkSession.builder \
        .appName('synonyms') \
        .config("spark.mongodb.read.connection.uri", common.MONGO_CONN_STR + ".sentenses") \
        .config("spark.mongodb.write.connection.uri", common.MONGO_CONN_STR + ".sentenses") \
        .config('spark.jars.packages', 'org.mongodb.spark:mongo-spark-connector:10.0.4') \
        .getOrCreate()

def init_spark():
    return SparkSession.builder \
        .appName('synonyms') \
        .getOrCreate()

# Загузка данных
def load_df(spark):
    return spark.read.format("mongodb").load()

# Извлекает только текст из документов
def get_text(df):
    return df.select(f.explode(f.col('sentenses')['text']))

def create_model():
    spark = init_spark_mongo()
    df = load_df(spark)
    df = get_text(df)

    df.show()
    # Удаление пунктуации
    df = df.rdd.map(lambda x: (x[0].translate(TRANSLATION), )).toDF(['text'])
    df.show()

    # Токенизация
    tokenizer = Tokenizer(inputCol='text', outputCol='words')
    df = tokenizer.transform(df)
    df.show()

    # Очистка от стоп-слов
    stop_words = StopWordsRemover.loadDefaultStopWords('russian')
    remover = StopWordsRemover(inputCol="words", outputCol="filtered", stopWords=stop_words)
    df = remover.transform(df)
    df.show()

    # Построение модели word2vec
    word2vec = Word2Vec(vectorSize=50, minCount=0, inputCol='filtered', outputCol='result')
    model = word2vec.fit(df)

    # Сохранение модели
    model.save(WORD2VEC_DIR)

    return model


def get_word2vec_model():
    """
    Создает или возвращает готовую модель word2vec
    """
    if os.path.exists(WORD2VEC_DIR):
        print('Loading existing word2vec model')
        spark = init_spark()
        return Word2VecModel.load(WORD2VEC_DIR)
    else:
        print('Word2vec model not found. Create new.')
        return create_model()
