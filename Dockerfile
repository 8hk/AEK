FROM python:3

RUN apt-get update && apt-get -y install cron
#COPY annotator_tool/annotate-cron /etc/cron.d/annotate-cron
#RUN chmod 0644 /etc/cron.d/annotate-cron
#RUN crontab /etc/cron.d/annotate-cron
#RUN touch /var/log/cron.log

ENV PYTHONUNBUFFERED 1
RUN mkdir /mentisparchment_docker
WORKDIR /mentisparchment_docker
COPY . /mentisparchment_docker/
RUN pip install -r requirements.txt
RUN ["python", "-c", "import nltk; nltk.download('stopwords'); nltk.download('punkt');"]
