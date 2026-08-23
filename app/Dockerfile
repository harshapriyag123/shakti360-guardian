FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
ARG EXPO_PUBLIC_ANDROID_DOWNLOAD_URL
ARG EXPO_PUBLIC_IOS_DOWNLOAD_URL
ENV EXPO_PUBLIC_API_URL=/api \
    EXPO_PUBLIC_ANDROID_DOWNLOAD_URL=${EXPO_PUBLIC_ANDROID_DOWNLOAD_URL} \
    EXPO_PUBLIC_IOS_DOWNLOAD_URL=${EXPO_PUBLIC_IOS_DOWNLOAD_URL}
RUN npm run build:web

FROM nginx:1.29-alpine
ENV PORT=80 \
    API_UPSTREAM=http://api.railway.internal:8000
RUN rm -f /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/templates/default.conf.template
COPY start-nginx.sh /usr/local/bin/start-nginx.sh
RUN chmod +x /usr/local/bin/start-nginx.sh
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
HEALTHCHECK --interval=30s --timeout=3s CMD wget -q -O /dev/null "http://127.0.0.1:${PORT:-80}/" || exit 1
