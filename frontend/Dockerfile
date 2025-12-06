FROM node:latest AS ui-build
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . .
RUN npm install && npm run build


FROM nginx:alpine

#!/bin/sh

COPY ./.nginx/nginx.conf /etc/nginx/nginx.conf

## Remove default nginx index page
RUN rm -rf /usr/share/nginx/html/*

# Copy from the stahg 1
COPY --from=ui-build /app/build/ /usr/share/nginx/html

EXPOSE 4200 8080

ENTRYPOINT ["nginx", "-g", "daemon off;"]