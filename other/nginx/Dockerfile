# using nginx as base image
FROM nginx

# removing default nginx - default.conf
RUN rm /etc/nginx/conf.d/default.conf

# Replacing it with our dice_9_.conf instead
COPY dice_9_.conf /etc/nginx/conf.d/