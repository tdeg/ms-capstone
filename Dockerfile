FROM python:3.8-slim


COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt --no-cache

RUN rm /tmp/requirements.txt

ENV PYTHONPATH=/opt/app

WORKDIR /opt/app

COPY . /opt/app

ENTRYPOINT ["python", "main.py" ]