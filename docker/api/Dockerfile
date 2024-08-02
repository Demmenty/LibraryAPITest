# Базовый образ, на основе которого будет создан образ для приложения.
FROM python:3.12.1

# Обновляет пакеты в базовом образе и устанавливает gcc и libpq-dev. 
# libpq-dev необходим для компиляции драйвера PostgreSQL для Python.
# gcc обеспечивает компилятор, который может потребоваться при установке некоторых пакетов через pip.
# Производит очистку кэша и временных файлов после установки.
# RUN apt-get update && \
#     apt-get install -y gcc libpq-dev && \
#     apt clean && \
#     rm -rf /var/cache/apt/*

# Создает каталог app и устанавливает в качестве рабочего каталога.
RUN mkdir -p /usr/src/app/
WORKDIR /usr/src/app/

# набор переменных среды для Python: чтобы Python не создавал файлы байт-кода, 
# устанавливал буферизацию ввода-вывода и кодировку по умолчанию.
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONIOENCODING utf-8

# Обновляет установщик пакетов pip и устанавливает зависимости.
RUN pip install --upgrade pip
COPY ../requirements.txt /usr/src/app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Копирует все файлы из текущего рабочего каталога внутрь образа
COPY . /usr/src/app/

# Создает пользователя app с домашним каталогом /src, 
# устанавливает оболочку /bin/bash для этого пользователя, 
# устанавливает права доступа. (из соображений безопасности)
# RUN useradd -m -d /src -s /bin/bash app \
#     && chown -R app:app /src
# USER app
