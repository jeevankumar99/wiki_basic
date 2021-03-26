FROM python:3
COPY . /usr/src/app
WORKDIR /usr/src/app
RUN pip3 install -r requirements.txt
CMD ["python", "manage.py", "runserver", "0.0.0.0:8080"]