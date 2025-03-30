import pLimit from 'p-limit';
import { Kafka } from 'kafkajs';
import { getMarkets, fetchOHLCVForSymbol } from './bybit-api.js';
import { saveBulkOhlcvData } from './db.js';
import logger from './logger.js';

const limit = pLimit(10);

// Настройка Kafka
const kafka = new Kafka({
  clientId: 'bybit-data-fetch',
  brokers: [process.env.KAFKA_BROKER || 'kafka:9092']
});
const producer = kafka.producer();

async function initKafka() {
  try {
    await producer.connect();
    logger.info('Kafka producer connected');
  } catch (error) {
    logger.error(`Kafka connection error: ${error.message}`);
  }
}

async function sendKafkaNotification() {
  try {
    await producer.send({
      topic: 'bybit-data-fetched',
      messages: [
        { value: JSON.stringify({ timestamp: new Date().toISOString(), status: 'done' }) }
      ],
    });
    logger.info('Sent Kafka notification after data fetch.');
  } catch (error) {
    logger.error(`Error sending Kafka message: ${error.message}`);
  }
}

async function retrySaveOhlcvData(data, collectedAt, retries = 3) {
  for (let attempt = 1; attempt <= retries; attempt++) {
    try {
      await saveBulkOhlcvData(data, collectedAt);
      return;
    } catch (error) {
      if (attempt === retries) throw error;
      logger.warn(`Attempt ${attempt} failed for ${data[0]?.symbol}: ${error.message}`);
      await new Promise(r => setTimeout(r, 2000 * attempt));
    }
  }
}

async function retryFetchOHLCV(symbol, retries = 3) {
  for (let attempt = 1; attempt <= retries; attempt++) {
    try {
      return await fetchOHLCVForSymbol(symbol);
    } catch (error) {
      logger.warn(`Attempt ${attempt} failed for ${symbol}: ${error.message}`);
      if (attempt === retries) return [];
      await new Promise(r => setTimeout(r, 2000 * attempt));
    }
  }
}

async function processSymbol(symbol) {
  try {
    logger.debug(`Fetching data for ${symbol}`);
    const data = await retryFetchOHLCV(symbol);
    
    if (data.length === 0) return;

    await retrySaveOhlcvData(data, new Date().toISOString());
    logger.info(`Saved ${data.length} candles for ${symbol}`);
  } catch (error) {
    logger.error(`Final failure for ${symbol}: ${error.message}`);
  }
}

// Функция для расчёта задержки до следующего XX:10
function getDelayToNextOccurrence() {
  const now = new Date();
  const next = new Date(now);
  next.setMinutes(10, 0, 0); // Устанавливаем минуты = 10, секунды и миллисекунды = 0
  if (now >= next) { 
    // Если текущее время уже прошло XX:10, планируем на следующий час
    next.setHours(next.getHours() + 1);
  }
  return next - now;
}

export async function startScheduler() {
  await initKafka();
  logger.info('Scheduler started. Job will run once per hour at minute 10 (XX:10).');

  async function job() {
    try {
      const batchSize = parseInt(process.env.BATCH_SIZE, 10) || 20;
      const markets = await getMarkets();
      const symbols = Object.keys(markets);
      
      for (let i = 0; i < symbols.length; i += batchSize) {
        const batch = symbols.slice(i, i + batchSize);
        logger.info(`Processing batch ${i}-${i + batchSize} out of ${symbols.length}`);
        await Promise.all(batch.map(symbol => limit(() => processSymbol(symbol))));
      }
      
      logger.info('Scheduler cycle completed');
      // После успешного завершения цикла отправляем уведомление в Kafka
      await sendKafkaNotification();
    } catch (error) {
      logger.error(`Scheduler error: ${error.message}`);
    }
  }

  async function scheduleNextRun() {
    const delay = getDelayToNextOccurrence();
    logger.info(`Next job scheduled to run in ${Math.round(delay / 1000)} seconds`);
    setTimeout(async () => {
      await job();
      scheduleNextRun();
    }, delay);
  }

  scheduleNextRun();
}
