# using alpine as a parent image
FROM alpine

# updating the apk && installing dependencies && upgrading pip
RUN apk update --no-cache && \
apk add --no-cache python3 py3-pip && \
pip3 install --no-cache-dir --upgrade pip

# coping all the contents of current dir into container at dice_9_API/app
COPY ./ ./dice_9_API/app/

#setting Working Directory
WORKDIR ./dice_9_API/app/

# installing all the app requirements & dependencies
RUN apk add --no-cache python3-dev build-base linux-headers pcre-dev && \
pip3 install --no-cache-dir -r requirements.txt uwsgi

#Setting Environment variables
# ENV MAIL_USERNAME # this you will get from docker-compose.yml
# ENV MAIL_PASSWORD # this you will get from docker-compose.yml
ENV ENCRYPTION_KEY nBGYyqlYDwC9_hlB_Gdp62mDobA7frfMyUmsweYmQz4=

# run -run.py as soon as container launches
CMD ["uwsgi","app.ini"]