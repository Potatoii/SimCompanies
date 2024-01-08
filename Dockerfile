FROM python:3.11

ADD . /simbot
WORKDIR /simbot

RUN cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
RUN echo "Asia/Shanghai" >/etc/timezone
RUN pip install -r requirements.txt