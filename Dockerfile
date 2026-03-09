FROM python:3.10.20-slim
LABEL authors="midnight"

WORKDIR app/

COPY . .

CMD ["python", "main.py"]