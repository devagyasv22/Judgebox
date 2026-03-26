FROM python:3.14

WORKDIR /app

RUN apt-get update && apt-get install -y libpq-dev gcc

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV DJANGO_SETTINGS_MODULE=OJ.settings
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD sh -c "python manage.py migrate --noinput && \
python manage.py collectstatic --noinput && \
python manage.py seed_problems_if_empty --path OJ/data/problems_seed.json && \
gunicorn OJ.wsgi:application --bind 0.0.0.0:${PORT:-8000}"