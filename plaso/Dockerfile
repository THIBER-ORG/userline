FROM log2timeline/plaso

RUN apt-get update && \
    apt-get dist-upgrade -y

RUN apt-get install -y python-pip python-dev

RUN pip install pyelasticsearch
