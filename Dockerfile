FROM python:3.7.5

WORKDIR /elsaserver

COPY ./requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY ./main.py main.py
COPY ./elsaserver elsaserver

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]