import winston from 'winston';
import DailyRotateFile from 'winston-daily-rotate-file';

const { combine, timestamp, printf, colorize } = winston.format;

const logFilePath = process.env.LOG_FILE_PATH?.trim() || './logs/application-%DATE%.log';

const logFormat = printf(({ level, message, timestamp }) => {
  return `${timestamp} [${level.toUpperCase()}]: ${message}`;
});

const consoleFormat = combine(
  colorize({ all: true }),
  timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
  printf(({ level, message, timestamp }) => {
    return `${timestamp} [${level}]: ${message}`;
  })
);

const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: combine(timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }), logFormat),
  transports: [
    new DailyRotateFile({
      filename: logFilePath,
      datePattern: 'YYYY-MM-DD',
      maxSize: '500m',
      maxFiles: '14d',
      level: 'debug',
    }),
    new winston.transports.Console({
      format: consoleFormat,
      level: 'info',
    })
  ]
});

export default logger;
export { logger };
