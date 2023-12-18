FROM joyzoursky/python-chromedriver:3.9-alpine-selenium

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "api:app", "--host=0.0.0.0"]
