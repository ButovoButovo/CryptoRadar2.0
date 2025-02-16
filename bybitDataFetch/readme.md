# Cryptocurrency Data Pipeline

A Node.js solution for fetching, storing, and managing cryptocurrency market data from Bybit exchange.

## Project Structure

### 📦 bybit-api
- Connects to Bybit API using API keys
- Loads and caches available trading pairs
- Fetches OHLCV (candlestick) data with automatic retries on network failures
- Implements rate limiting and error handling

### 🗃️ db.js
- Handles database initialization and connection
- Creates necessary database tables/collections
- Provides methods for saving OHLCV data to persistent storage
- Supports SQLite/PostgreSQL/MySQL (configurable)

### 📝 logger.js
- Centralized logging configuration
- Implements log rotation policy
- Supports multiple transport types (console, file, remote)
- Configurable log levels (debug, info, warn, error)

### ⏰ scheduler.js
- Manages periodic data fetching tasks
- Configurable intervals for different trading pairs
- Implements job queueing and concurrency control
- Integrates with bybit-api and db.js modules

## 🚀 Getting Started

### Prerequisites
- Node.js (v18+ recommended)
- npm/yarn package manager
- Bybit API keys
- Database system (SQLite/PostgreSQL/MySQL)

### Installation
```bash
npm install