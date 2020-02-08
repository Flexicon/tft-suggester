FROM joyzoursky/python-chromedriver:3.7-selenium

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ['uvicorn', 'api:app', '--host=0.0.0.0']
