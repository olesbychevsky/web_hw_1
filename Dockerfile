FROM python:3.9.18-alpine3.18

WORKDIR \exponenta_app

COPY . .

RUN pip install -r requirements.txt

ENTRYPOINT [ "python", "exponenta_main.py" ]