FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
ARG EXPO_PUBLIC_API_URL
ARG EXPO_PUBLIC_APP_URL
ENV EXPO_PUBLIC_API_URL=$EXPO_PUBLIC_API_URL
ENV EXPO_PUBLIC_APP_URL=$EXPO_PUBLIC_APP_URL
RUN test -n "$EXPO_PUBLIC_API_URL" || (echo "EXPO_PUBLIC_API_URL build variable is required" && exit 1)
RUN case "$EXPO_PUBLIC_API_URL" in https://*) ;; *) echo "EXPO_PUBLIC_API_URL must be a public HTTPS URL"; exit 1 ;; esac
RUN npm run build:web

FROM nginx:1.29-alpine
ENV PORT=80
RUN rm -f /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/templates/default.conf.template
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
HEALTHCHECK --interval=30s --timeout=3s CMD wget -q -O /dev/null "http://127.0.0.1:${PORT:-80}/" || exit 1
