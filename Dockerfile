FROM python:3.12-slim

WORKDIR /app

COPY  .venv/lib/python3.12/site-packages/requirements.txt .

RUN pip install -r requirements.txt

RUN apt-get update && apt-get install firefox-esr -y

COPY pexels_scraper.py  .

CMD ["python","pexels_scraper.py"]

