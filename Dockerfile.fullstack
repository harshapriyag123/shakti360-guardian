FROM node:22-alpine AS web-build

WORKDIR /web
COPY app/package.json app/package-lock.json ./
RUN npm ci
COPY app ./
ARG EXPO_PUBLIC_ANDROID_DOWNLOAD_URL
ARG EXPO_PUBLIC_IOS_DOWNLOAD_URL
ENV EXPO_PUBLIC_API_URL=/api \
    EXPO_PUBLIC_ANDROID_DOWNLOAD_URL=${EXPO_PUBLIC_ANDROID_DOWNLOAD_URL} \
    EXPO_PUBLIC_IOS_DOWNLOAD_URL=${EXPO_PUBLIC_IOS_DOWNLOAD_URL}
RUN npm run typecheck && npm run build:web

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080 \
    API_UPSTREAM=http://127.0.0.1:8000

WORKDIR /srv/shakti360

RUN apt-get update \
    && apt-get install -y --no-install-recommends nginx gettext-base curl \
    && rm -rf /var/lib/apt/lists/* \
    && rm -f /etc/nginx/sites-enabled/default /etc/nginx/conf.d/default.conf

COPY backend/requirements.txt ./requirements.txt
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY backend/app ./app
COPY app/nginx.conf /etc/nginx/templates/default.conf.template
COPY start-fullstack.sh /usr/local/bin/start-fullstack.sh
COPY --from=web-build /web/dist /usr/share/nginx/html

RUN chmod +x /usr/local/bin/start-fullstack.sh

EXPOSE 8080
CMD ["/usr/local/bin/start-fullstack.sh"]
