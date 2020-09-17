FROM alpine
RUN apk add python3 python3-dev
COPY . /var/www
WORKDIR /var/www
RUN pip install rasa==1.10.12
RUN rasa train
RUN rasa run actions &
ENTRYPOINT [ “rasa”, “run”, “-p”, “8080”]
