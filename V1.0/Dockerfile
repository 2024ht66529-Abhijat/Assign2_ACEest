FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir flask gunicorn pytest pytest-cov

ENV FLASK_ENV=production

EXPOSE 5000

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app.app:app"]