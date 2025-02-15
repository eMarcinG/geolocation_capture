# Use base image
FROM python:3.9

# Set work directory
WORKDIR /code

# Upgrade PIP
RUN pip install --upgrade pip

# Copy and install dependencies
COPY requirements.txt /code/
RUN pip install -r requirements.txt

# Copy the rest of the application
COPY . /code/

# Copy init script and .env file
COPY create_superuser.py /code/
COPY .env /code/

# Run database migrations, load fixtures, and create superuser
CMD ["sh", "-c", "python manage.py makemigrations && python manage.py migrate && python manage.py shell < create_superuser.py && python manage.py runserver 0.0.0.0:8000"]
