# Используем официальный образ Node.js версии 22 (на базе Alpine)
FROM node:22-alpine

# Установка пакетов tzdata и curl (curl понадобится для healthcheck)
RUN apk add --no-cache tzdata curl

# Установка временной зоны UTC
ENV TZ=UTC

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файлы зависимостей (package.json и package-lock.json)
COPY package*.json ./

# Устанавливаем зависимости (убедитесь, что в package.json добавлен express)
RUN npm install

# Копируем исходный код приложения
COPY . .

# Открываем порт 3000 (на котором будет слушать Express-сервер)
EXPOSE 3000

# Команда для запуска приложения с флагом --no-warnings
CMD ["node", "--no-warnings", "app.js"]
