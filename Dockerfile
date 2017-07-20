FROM ubuntu:17.04

ENV DEBIAN_FRONTEND=noninteractive \
    WORKDIR='/' \
    DATADIR='/data' \
    EPOINT='/entry-point.sh' \
    NAME='userline'

WORKDIR $WORKDIR

RUN apt-get update && \
    apt-get -y dist-upgrade && \
    apt-get -y install \
            gosu \
            python3-pip

RUN mkdir /$NAME && \
    mkdir -p $DATADIR
ADD src/ /$NAME
ADD requirements.txt /$NAME
RUN cd $NAME && \
    pip3 install -U -r requirements.txt

RUN echo "#!/bin/bash\n\
set -e\n\
\n\
if [ \"\$1\" = \"$NAME\" ]\n\
then\n\
    shift\n\
    chown -R $NAME:$NAME $DATADIR\n\
    exec gosu $NAME /$NAME/$NAME.py \"\$@\"\n\
fi\n\
\n\
exec \"\$@\"" > $EPOINT && \
    chmod +x $EPOINT && \
    useradd -r -s /sbin/nologin -d /$NAME $NAME

WORKDIR $WORKDIR$NAME
ENTRYPOINT ["/entry-point.sh"]
