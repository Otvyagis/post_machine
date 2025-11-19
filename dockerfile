# Базовый образ с Python и X11
FROM python:3.11-slim

# Устанавливаем зависимости для GUI (tkinter требует tcl/tk)
RUN apt-get update && apt-get install -y \
    python3-tk \
    tk \
    libx11-6 \
    libxext6 \
    libxrender1 \
    libxft2 \
    libxss1 \
    libxi6 \
    libxrandr2 \
    libxcursor1 \
    libxinerama1 \
    libglu1-mesa \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt || true

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем код в контейнер
COPY . /app

# Устанавливаем переменную окружения для Python
ENV PYTHONUNBUFFERED=1

# Для запуска GUI через X11
CMD ["python", "main.py"]