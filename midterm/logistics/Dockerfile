FROM python:3.12.4-slim-bullseye

WORKDIR /src

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install && apt-get install gettext -y --no-install-recommends libpq-dev bash gunicorn wkhtmltopdf poppler-utils

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -Ur requirements.txt
#COPY --from=base /usr/local/lib/python3.10/site-packages/ /usr/local/lib/python3.10/site-packages/

COPY . .
