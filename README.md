# search
Python/Django Web Programming Huge Project.

A lightweight search engine written in Python 2.

# Install

```shell
python -m pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

# Usage

## Initial Crawl

1. Put at least one link into `links/left_links.txt` (you may create this file before)
2. `python spider.py`

You can press Ctrl+C to stop crawling and the progress will be saved.

## Incremental Crawl

```shell
python spider.py
```

You can press Ctrl+C to stop crawling and the progress will be saved.

## Make Indexes

```shell
python index.py
```

## Run Server

```shell
python manage.py runserver
```
