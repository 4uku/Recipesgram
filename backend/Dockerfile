FROM python:3.10
WORKDIR /app
COPY requirements.txt /app
RUN python -m pip install --upgrade pip
RUN pip install -r /app/requirements.txt --no-cache-dir
COPY api_foodgram/ /app
CMD ["gunicorn", "api_foodgram.wsgi:application", "--bind", "0:8000"]