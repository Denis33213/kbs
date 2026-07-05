# ---------- Стадия 1: сборка приложения ----------
FROM node:20-alpine AS build

WORKDIR /app

# VITE_API_URL встраивается в статический бандл на этапе сборки —
# в отличие от backend, переменные окружения Vite не читаются в runtime.
ARG VITE_API_URL=http://localhost:8000
ENV VITE_API_URL=$VITE_API_URL

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

# ---------- Стадия 2: отдача статики через Nginx ----------
FROM nginx:1.27-alpine

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]