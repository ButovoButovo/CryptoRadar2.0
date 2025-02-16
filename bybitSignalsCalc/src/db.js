require('dotenv').config();
const { Pool } = require('pg');
const tulind = require('tulind');
const ss = require('simple-statistics');

const pool = new Pool({
  user: process.env.DB_USER,
  host: process.env.DB_HOST,
  database: process.env.DB_NAME,
  password: process.env.DB_PASSWORD,
  port: process.env.DB_PORT
});

async function initDatabase() {
  try {
    const client = await pool.connect();
    console.log("✅ Database connected");
    client.release();
  } catch (err) {
    console.error("❌ Database connection error:", err);
  }
}

async function getValidSymbols() {
  const query = `SELECT DISTINCT symbol FROM ohlcv WHERE timestamp >= NOW() - INTERVAL '1 month'`;
  console.log("Executing SQL:", query);
  try {
    const { rows } = await pool.query(query);
    console.log("Valid symbols:", rows);
    return rows.map(row => row.symbol);
  } catch (err) {
    console.error("Error fetching valid symbols:", err);
    return [];
  }
}

async function getContinuousOHLCV(symbol) {
  const query = `SELECT timestamp, open, high, low, close, volume FROM ohlcv WHERE symbol = $1 ORDER BY timestamp ASC`;
  console.log(`Executing SQL for ${symbol}:`, query);
  try {
    const { rows } = await pool.query(query, [symbol]);
    console.log(`Data for ${symbol}:`, rows.length, "rows fetched");
    return rows;
  } catch (err) {
    console.error(`Error fetching OHLCV for ${symbol}:`, err);
    return [];
  }
}

async function analyzeMarket() {
  try {
    const symbols = await getValidSymbols();
    const promises = symbols.map(symbol => getContinuousOHLCV(symbol));
    const ohlcvData = await Promise.all(promises);
    
    for (let i = 0; i < symbols.length; i++) {
      const symbol = symbols[i];
      const data = ohlcvData[i];
      if (data.length < 200) continue;
      
      const closes = data.map(d => d.close);
      const highs = data.map(d => d.high);
      const lows = data.map(d => d.low);
      const volumes = data.map(d => d.volume);
      
      try {
        const ema14 = await tulind.indicators.ema.indicator([closes], [14]);
        const ema200 = await tulind.indicators.ema.indicator([closes], [200]);
        const atr = await tulind.indicators.atr.indicator([highs, lows, closes], [14]);
        const boll = await tulind.indicators.bbands.indicator([closes], [20, 2]);
        
        const x = Array.from({ length: closes.length }, (_, i) => i);
        const trend = ss.linearRegression(x.map((_, i) => [i, closes[i]]));
        const trendSlope = trend.m;
        
        console.log(`📊 ${symbol} Analysis:`);
        console.log("EMA 14:", ema14[0].slice(-1)[0]);
        console.log("EMA 200:", ema200[0].slice(-1)[0]);
        console.log("ATR:", atr[0].slice(-1)[0]);
        console.log("Bollinger Upper:", boll[0].slice(-1)[0], "Lower:", boll[2].slice(-1)[0]);
        console.log("Trend Slope:", trendSlope);
      } catch (err) {
        console.error(`❌ Error calculating indicators for ${symbol}:`, err);
      }
    }
  } catch (err) {
    console.error("❌ Error in market analysis:", err);
  }
}

(async () => {
  await initDatabase();
  await analyzeMarket();
  await pool.end();
})();
