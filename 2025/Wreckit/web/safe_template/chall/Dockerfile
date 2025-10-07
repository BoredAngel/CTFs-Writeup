FROM python:3.9-slim

RUN apt-get update && apt-get install -y nginx iputils-ping && rm -rf /var/lib/apt/lists/*

ADD /app /app

# ✅ Make dirs traversable and files read-only
RUN find /app -type d -exec chmod 555 {} + && \
    find /app -type f -exec chmod 444 {} +

RUN pip install Flask gunicorn bcrypt

USER nobody

CMD gunicorn --chdir /app app:app -b 0.0.0.0:10103
