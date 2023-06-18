FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11

WORKDIR /tg_app

COPY ./requirements.txt /tg_app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /tg_app/requirements.txt

# caching the TF hub model so that it is not downloaded every time the app starts or receives the first request
ENV TFHUB_CACHE_DIR=/.tfhub_modules
RUN python -c 'import tensorflow_hub; tensorflow_hub.load("https://tfhub.dev/google/universal-sentence-encoder/4")'

COPY src/model.py src/train.py src/__init__.py /tg_app/app/
COPY data/ data/

RUN python /tg_app/app/train.py "data/movies_metadata.csv" && rm -rf data

COPY src/server.py /tg_app/app/

CMD ["uvicorn", "app.server:app", "--host", "0.0.0.0", "--port", "8000"]
