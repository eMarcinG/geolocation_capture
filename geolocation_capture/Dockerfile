
FROM python:3.9

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    gdal-bin \
    libgdal-dev \
    python3-gdal \
    && apt-get clean

ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

WORKDIR /code
COPY requirements.txt /code/
COPY . /code/
RUN chmod +x /code/manage.py

RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONUNBUFFERED=1

CMD ["sh", "-c", "python manage.py makemigrations && python manage.py migrate && python manage.py shell < create_superuser.py && python manage.py runserver 0.0.0.0:8000"]
