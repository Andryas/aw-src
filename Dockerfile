FROM python:3.9

WORKDIR /scrapy

COPY . /scrapy/

RUN apt update

RUN pip3 install -r requirements.txt

EXPOSE 8080

ENTRYPOINT [ "sh", "/scrapy/start.sh" ]
