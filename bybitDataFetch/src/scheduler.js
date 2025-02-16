//scheduler.js
import pLimit from 'p-limit';
import { getMarkets, fetchOHLCVForSymbol } from './bybit-api.js';
import { saveBulkOhlcvData } from './db.js';
import logger from './logger.js';

const limit = pLimit(10);

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

export function startScheduler(interval = 3600000) {
  logger.info(`Scheduler started, interval: ${interval / 1000}s`);

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
    } catch (error) {
      logger.error(`Scheduler error: ${error.message}`);
    }
  }

  setInterval(job, interval);
  job().catch(error => logger.error(`Initial job failed: ${error.message}`));
}
