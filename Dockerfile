FROM python:3.10

ADD . /simbot
WORKDIR /simbot

RUN cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && echo "Asia/Shanghai" >/etc/timezone
RUN pip config set global.index-url https://mirrors.cloud.tencent.com/pypi/simple \
    && pip config set install.trusted-host mirrors.cloud.tencent.com \
    && pip install -r requirements.txt