FROM python:3.10-alpine


#Tells python to run in unbuffered - recommended for docker. Doesnt allow python to buffer outputs
#to avoid complications
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

RUN mkdir /app
WORKDIR /app
COPY ./app /app

#Add user responsible for running applications only -D
#Not used for login
RUN adduser -D user
USER user

