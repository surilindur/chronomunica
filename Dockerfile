FROM python:3-alpine

WORKDIR /opt/chronomunica

COPY . .

RUN python -m pip install -r requirements.txt

CMD [ "python", "app.py" ]
