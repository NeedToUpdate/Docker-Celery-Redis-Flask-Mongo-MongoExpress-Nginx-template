FROM nginx

LABEL MAINTAINER=$MAINTAINER

RUN ln -sf /dev/stdout /var/log/nginx/access.log && \
    ln -sf /dev/stderr /var/log/nginx/error.log && \
    rm -f /etc/nginx/conf.d/default.conf && \
    mkdir -p /run/nginx

COPY conf.d/nginx.conf /etc/nginx/conf.d/nginx.conf
COPY conf.d/nginx.conf /etc/nginx/sites-enabled/flask_app

CMD ["nginx", "-g", "daemon off;"]
