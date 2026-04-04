# Використовуємо slim версію для зменшення розміру образу
FROM python:3.10-slim

# Встановлюємо системні залежності для psycopg (якщо не використовуєш binary версію)
# libpq-dev потрібен для взаємодії з PostgreSQL
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Встановлюємо робочу директорію
WORKDIR /app

# Налаштовуємо Python, щоб логи виводилися в реальному часі (важливо для вимоги №11)
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Спочатку копіюємо лише requirements.txt (це оптимізує кешування шарів Docker)
COPY requirements.txt .

# Встановлюємо залежності через менеджер пакетів pip [cite: 58]
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо весь інший код
COPY . .

# Відкриваємо порт, який ми обрали (7200)
EXPOSE 7200

# Запускаємо додаток
CMD ["python", "main.py"]