//bybit-api.js
import ccxt from 'ccxt';
import 'dotenv/config';
import logger from './logger.js';

const bybit = new ccxt.bybit({
  apiKey: process.env.BYBIT_API_KEY,
  secret: process.env.BYBIT_SECRET_KEY,
  enableRateLimit: true,
  options: {
    defaultType: process.env.BYBIT_DEFAULT_TYPE ?? 'spot',
    adjustmentForDowntime: process.env.BYBIT_ADJUSTMENT_FOR_DOWNTIME ?? true,
    throttle: {
      maxRequestsPerSecond: process.env.BYBIT_MAX_REQUESTS_PER_SECOND ?? 5,
      maxCapacity: process.env.BYBIT_MAX_CAPACITY ?? 1000,
    },
  },
});

let marketsCache = null;

async function getMarkets() {
  if (!marketsCache) {
    try {
      marketsCache = await bybit.loadMarkets();
      logger.info(`Markets loaded: ${Object.keys(marketsCache).length} pairs available`);
    } catch (error) {
      logger.error(`Failed to load markets: ${error.message}`);
      throw error;
    }
  }
  return marketsCache;
}

function validateCandle(candle) {
  return Array.isArray(candle) && candle.length === 6 && candle.every(val => val !== undefined);
}

async function fetchOHLCVForSymbol(symbol, retries = 3) {
  try {
    const candles = await bybit.fetchOHLCV(symbol, process.env.BYBIT_OHLCV_INTERVAL, undefined, process.env.BYBIT_OHLCV_LIMIT);
    return candles
      .filter(validateCandle)
      .map(candle => ({
        symbol,
        timestamp: candle[0],
        open: candle[1],
        high: candle[2],
        low: candle[3],
        close: candle[4],
        volume: candle[5],
      }));
  } catch (error) {
    if (retries > 0 && error instanceof ccxt.NetworkError) {
      logger.warn(`Network error for ${symbol}, retrying... (${retries} retries left)`);
      return fetchOHLCVForSymbol(symbol, retries - 1);
    }
    logger.error(`Fetch error for ${symbol}: ${error.message}`);
    return [];
  }
}

export { getMarkets, fetchOHLCVForSymbol };

