#!/usr/bin/env sh
export API_URL
envsubst '${API_URL}' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf
exec "$@"