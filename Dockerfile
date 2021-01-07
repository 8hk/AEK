FROM python:3

ENV PYTHONUNBUFFERED 1
RUN mkdir /mentisparchment_docker
WORKDIR /mentisparchment_docker
COPY . /mentisparchment_docker/
RUN pip install -r requirements.txt
RUN [ "python", "-c", "import nltk; nltk.download('all')" ]