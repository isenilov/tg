FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11

WORKDIR /tg_app

COPY ./requirements.txt /tg_app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /tg_app/requirements.txt

COPY src /tg_app/app

CMD ["uvicorn", "app.server:app", "--host", "0.0.0.0", "--port", "8000"]
