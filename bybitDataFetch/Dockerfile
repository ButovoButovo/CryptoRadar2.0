# Используем официальный образ Node.js версии 22
FROM node:22-alpine

# Установка пакета tzdata для работы с временными зонами
RUN apk add --no-cache tzdata

# Установка временной зоны UTC
ENV TZ=UTC

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем package.json и package-lock.json
COPY package*.json ./

# Устанавливаем зависимости
RUN npm install

# Копируем исходный код приложения
COPY . .

# Указываем порт, который будет использовать приложение
EXPOSE 3000

# Команда для запуска приложения с флагом --no-warnings
CMD ["node", "--no-warnings", "app.js"]