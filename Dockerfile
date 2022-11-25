FROM python:3.9.6-alpine

WORKDIR /app

COPY requirements.txt /app

RUN pip install -r requirements.txt

COPY . .

CMD ["python", "telegram_bot.py"]