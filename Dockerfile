FROM python:3.6-slim
COPY . /var/www
WORKDIR /var/www
RUN pip install rasa==1.10.2
RUN rasa train
CMD ["rasa", "run", "actions", "&"]
ENTRYPOINT [ "rasa", "run", "-p", "8080"]
