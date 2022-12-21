FROM nginx
COPY public /home/public
RUN echo ' \
proxy_hide_header X-Frame-Options; \n\r \
server { \n\r \
  listen       3333; \n\r \
  listen  [::]:3333; \n\r \
  server_name  localhost; \n\r \
  root /home/public; \n\r \
}' > /etc/nginx/conf.d/default.conf