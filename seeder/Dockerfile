FROM python:3.8-slim


COPY main.py /app/main.py
COPY data.json /app/data.json

RUN pip install redis
RUN pip install python-dotenv

CMD ["python", "/app/main.py"]
