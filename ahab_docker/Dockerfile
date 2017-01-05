FROM ubuntu:14.04

RUN apt-get update
RUN apt-get install -y python
RUN apt-get install -y python-pip python-dev build-essential
RUN pip install boto
RUN pip install pyyaml 
RUN pip install numpy
RUN apt-get install -y awscli
RUN apt-get install -y openssh-server


ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8
#ENV AWS_ACCESS_KEY_ID       AKIAJTR3SNZYRNF4CKYA
#ENV AWS_SECRET_ACCESS_KEY   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

ENV AWS_ACCESS_KEY_ID       AKIAIX5Z7D5FJARYWZSQ
ENV AWS_SECRET_ACCESS_KEY   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

ENV AWS_DEFAULT_REGION      us-west-2 
#ENV PEQUOD_SPARK_URL       spark://52.10.53.231:7077
ENV PEQUOD_PUBLIC_IP    52.10.53.231

#ENV PEQUOD_SPARK_URL        spark://$PEQUOD_PUBLIC_IP:7077
ENV PEQUOD_HOME             /scripts



RUN  mkdir /root/.ssh
RUN  echo "IdentityFile  /scripts/wietsche.pem" >> /etc/ssh/ssh_config
RUN  ssh-keyscan -t rsa $PEQUOD_PUBLIC_IP >> /root/.ssh/known_hosts
#RUN  ssh-keygen -R $PEQUOD_PUBLIC_IP
RUN  echo "Host *" >> /root/.ssh/config
RUN  echo "    StrictHostKeyChecking no" >> /root/.ssh/config

RUN mkdir /scripts
COPY scripts/ /scripts/

WORKDIR /scripts
#RUN chmod a+x /scripts/ishmael.py
#ENTRYPOINT /scripts/ishmael.py

