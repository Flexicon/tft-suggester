FROM python:3.9-alpine

WORKDIR /app

RUN apk --no-cache add curl

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "api:app", "--host=0.0.0.0"]
