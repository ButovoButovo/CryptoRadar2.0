//db.js
import pg from 'pg';
const { Pool } = pg;
import 'dotenv/config';
import logger from './logger.js';

const pool = new Pool({
  host: process.env.DB_HOST,
  port: process.env.DB_PORT,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME,
  max: 10,
  idleTimeoutMillis: 30000,
});

async function initDatabase() {
  try {
    const table = process.env.DB_TABLE_NAME;
    const query = `
    CREATE TABLE IF NOT EXISTS ${table} (
      symbol VARCHAR(255) NOT NULL,
      timestamp_unix_utc BIGINT NOT NULL,
      open NUMERIC NOT NULL,
      high NUMERIC NOT NULL,
      low NUMERIC NOT NULL,
      close NUMERIC NOT NULL,
      volume NUMERIC NOT NULL,
      collected_at_utc TIMESTAMP NOT NULL,
      timestamp_iso_utc TIMESTAMP GENERATED ALWAYS AS (
        to_timestamp(timestamp_unix_utc / 1000.0) AT TIME ZONE 'UTC'
      ) STORED,
      CONSTRAINT unique_symbol_timestamp UNIQUE (symbol, timestamp_unix_utc)
    );
  `;  
    await pool.query(query);
    
    logger.info('Database initialized successfully');
  } catch (error) {
    logger.error(`Database initialization failed: ${error.message}`);
    throw error;
  }
}

async function saveBulkOhlcvData(dataArray, collectedAt, retries = 3) {
  if (dataArray.length === 0) return;

  const client = await pool.connect();
  const table = process.env.DB_TABLE_NAME;

  try {
    await client.query('BEGIN');

    const query = `
      INSERT INTO ${table} 
        (symbol, timestamp_unix_utc, open, high, low, close, volume, collected_at_utc)
      VALUES ${dataArray.map((_, i) => `($${i * 8 + 1}, $${i * 8 + 2}, $${i * 8 + 3}, $${i * 8 + 4}, $${i * 8 + 5}, $${i * 8 + 6}, $${i * 8 + 7}, $${i * 8 + 8})`).join(', ')}
      ON CONFLICT (symbol, timestamp_unix_utc) DO NOTHING
    `;
    
    const values = dataArray.flatMap(data => [
      data.symbol, data.timestamp, data.open, data.high, 
      data.low, data.close, data.volume, collectedAt
    ]);

    const result = await client.query(query, values);
    
    await client.query('COMMIT');
    logger.info(`Inserted ${result.rowCount} OHLCV records`);

  } catch (error) {
    await client.query('ROLLBACK');
    logger.error(`Database error: ${error.message}`);

    if (retries > 0) {
      logger.warn(`Retrying... (${retries} attempts left)`);
      return saveBulkOhlcvData(dataArray, collectedAt, retries - 1);
    }

    throw error;
  } finally {
    client.release();
  }
}

export { initDatabase, saveBulkOhlcvData };
