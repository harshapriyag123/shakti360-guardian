#!/bin/sh
set -eu

resolver="$(awk '/^nameserver[[:space:]]+/{print $2; exit}' /etc/resolv.conf)"
resolver="${resolver:-127.0.0.11}"
case "$resolver" in
  *:*) resolver="[$resolver]" ;;
esac

export NGINX_RESOLVER="$resolver"
exec /docker-entrypoint.sh nginx -g 'daemon off;'
