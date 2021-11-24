FROM python:3.10-alpine


#Tells python to run in unbuffered - recommended for docker. 
#Doesnt allow python to buffer outputs
#to avoid complications
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt
#Uses manager that comes with alpine, update registry before we add it,
#no cache - dont store on docker file
RUN apk add --update --no-cache postgresql-client jpeg-dev
#virtual sets up alias for dependencies so we can remove it easier lately
RUN apk add --update --no-cache --virtual .tmp-build-deps \
        gcc libc-dev linux-headers postgresql-dev musl-dev zlib zlib-dev

RUN pip install -r /requirements.txt
RUN apk del .tmp-build-deps

RUN mkdir /app
WORKDIR /app
COPY ./app /app

#Add user responsible for running applications only -D
#Not used for login
#media for pictures
RUN mkdir -p /vol/web/media
#for staticfiles
RUN mkdir -p /vol/web/static
RUN adduser -D user
RUN chown -R user:user /vol/
RUN chmod -R 755 /vol/web
USER user

