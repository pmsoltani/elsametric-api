FROM python:3.7.5

WORKDIR /elsaserver

COPY . .

RUN pip install -r requirements.txt

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${BACKEND_PORT}"]