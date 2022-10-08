## Установка

Докер
```
ssh-keygen
cp $HOME/.ssh/id_rsa.pub tomita/
sudo docker-compose build
```

NLTK
```
python -m nltk.downloader punkt wordnet averaged_perceptron_tagger stopwords
```

## Запуск

```
sudo docker-compose up
```
