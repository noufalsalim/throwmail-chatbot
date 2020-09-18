FROM python:3.6-slim
RUN apt-get update -qq \
 && apt-get install -y --no-install-recommends \
    # required by psycopg2 at build and runtime
    libpq-dev \
     # required for health check
    curl \
 && apt-get autoremove -y
RUN apt-get update -qq && \
  apt-get install -y --no-install-recommends \
  build-essential \
  wget \
  openssh-client \
  graphviz-dev \
  pkg-config \
  git-core \
  openssl \
  libssl-dev \
  libffi6 \
  libffi-dev \
  libpng-dev
COPY . /var/www
WORKDIR /var/www
RUN pip install rasa==1.10.2
RUN rasa train
RUN ["chmod", "+x", "run.sh"]
ENTRYPOINT ["bash", "run.sh"]
