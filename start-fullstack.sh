#!/bin/sh
set -eu

export PORT="${PORT:-8080}"
export API_UPSTREAM="http://127.0.0.1:8000"
resolver="$(awk '/^nameserver[[:space:]]+/{print $2; exit}' /etc/resolv.conf)"
resolver="${resolver:-127.0.0.1}"
case "$resolver" in
  *:*) resolver="[$resolver]" ;;
esac
export NGINX_RESOLVER="$resolver"

envsubst '${PORT} ${API_UPSTREAM} ${NGINX_RESOLVER}' \
  < /etc/nginx/templates/default.conf.template \
  > /etc/nginx/conf.d/default.conf

python -m uvicorn app.main:app \
  --host 127.0.0.1 \
  --port 8000 \
  --proxy-headers \
  --forwarded-allow-ips='*' &
api_pid=$!

nginx -g 'daemon off;' &
nginx_pid=$!

terminate() {
  kill "$api_pid" "$nginx_pid" 2>/dev/null || true
}
trap terminate INT TERM EXIT

while kill -0 "$api_pid" 2>/dev/null && kill -0 "$nginx_pid" 2>/dev/null; do
  sleep 2
done

terminate
wait "$api_pid" 2>/dev/null || api_status=$?
wait "$nginx_pid" 2>/dev/null || nginx_status=$?
exit "${api_status:-${nginx_status:-1}}"
