//app.js
import 'dotenv/config';
import express from 'express';
import { initDatabase } from './src/db.js';
import { startScheduler } from './src/scheduler.js';
import logger from './src/logger.js';

// Обработка неожиданных ошибок
process.on('uncaughtException', (error) => {
  logger.error(`Uncaught Exception: ${error.message}`);
  process.exit(1);
});

process.on('unhandledRejection', (reason) => {
  logger.error(`Unhandled Rejection: ${reason}`);
  process.exit(1);
});

(async () => {
  try {
    await initDatabase();
    logger.info('Database initialized');

    const interval = parseInt(process.env.SCHEDULER_INTERVAL, 10) || 3600000; // 1 час по умолчанию
    startScheduler(interval);
    logger.info(`Scheduler started, interval: ${interval / 1000}s`);
  } catch (error) {
    logger.error(`Bootstrap failed: ${error.message}`);
    process.exit(1);
  }
})();

// Создание HTTP-сервера для health-check
const app = express();
const PORT = 3000;

app.get('/health', (req, res) => {
  res.send('OK');
});

app.listen(PORT, '0.0.0.0', () => {
  logger.info(`Health server listening on port ${PORT}`);
});

// Корректное завершение процесса при SIGINT и SIGTERM
process.on('SIGINT', () => {
  logger.info('Received SIGINT, shutting down gracefully...');
  process.exit(0);
});

process.on('SIGTERM', () => {
  logger.info('Received SIGTERM, shutting down gracefully...');
  process.exit(0);
});
