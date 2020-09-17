FROM python:3.6-slim
COPY . /var/www
WORKDIR /var/www
RUN pip install rasa==1.10.2
RUN rasa train
RUN ["chmod", "+x", "run.sh"]
ENTRYPOINT ["bash", "run.sh"]
