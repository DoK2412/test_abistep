FROM python:3.11-slim

WORKDIR /app

COPY src/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt --root-user-action=ignore

COPY src /app/

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8082"]