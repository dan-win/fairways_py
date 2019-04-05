# FROM pypy:3
# FROM pypy:3.6-7.1-slim
FROM python:3.6

WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y \
        python3-dev \
        libffi-dev \
        default-libmysqlclient-dev \
        gcc \
    && rm -rf /var/lib/apt/lists/* 

COPY requirements.txt ./
# ENV CFLAGS=-I/usr/include/libffi/include
RUN export CFLAGS=$(pkg-config --cflags libffi) \
    && export LDFLAGS=$(pkg-config --libs libffi) \
    && pip install --no-cache-dir -r requirements.txt \
    && mkdir -p buffer && cd /usr/src/app \
    && apt-get remove -y\
        python3-dev \
        libffi-dev \
        default-libmysqlclient-dev \
        gcc \
    && apt-get autoremove -y && apt-get purge -y

# COPY . .
ENV EVENTMACHINE_BUFFER="/tmp/buffer"

VOLUME [ "/usr/src/app" ]
VOLUME [ "/tmp/buffer" ]
CMD [ "python", "./main.py" ]