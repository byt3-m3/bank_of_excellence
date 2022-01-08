FROM python

COPY dist/boe-0.0.1.tar.gz /dist/boe-0.0.1.tar.gz
COPY requirements.txt /requirements.txt
COPY bin /boe_bin

RUN cd dist && ls | grep tar.gz | xargs pip3 install

RUN pip install -r /requirements.txt