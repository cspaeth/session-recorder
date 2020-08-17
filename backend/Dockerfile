FROM ubuntu:20.04
ENV PYTHONUNBUFFERED 1

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get -qy update
RUN apt-get -qy install python3 python3-pip postgresql postgresql-contrib libpq-dev
RUN pip3 install virtualenv
RUN virtualenv /env

WORKDIR /tmp
COPY requirements.txt ./

RUN /env/bin/pip install -r requirements.txt
RUN /env/bin/pip install gunicorn

RUN echo ". /env/bin/activate" >> /root/.bashrc

WORKDIR /src

COPY ./entrypoint.sh /
ENTRYPOINT ["/entrypoint.sh"]