FROM ubuntu:14.04

ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8
ENV AWS_ACCESS_KEY_ID       AKIAJTR3SNZYRNF4CKYA
ENV AWS_SECRET_ACCESS_KEY   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
ENV AWS_DEFAULT_REGION      us-west-2 

RUN apt-get update
RUN apt-get install -y python
RUN apt-get install -y python-pip python-dev build-essential
RUN pip install boto
RUN pip install python-twitter

RUN mkdir /scripts

COPY ishmael.py /scripts/ 
RUN chmod a+x /scripts/ishmael.py

ENTRYPOINT /scripts/ishmael.py
