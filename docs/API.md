# API Documentation

FastAPI REST API for the Crypto Trading System.

## Base URL

```
http://localhost:8001
```

## API Endpoints

### Health Check

#### `GET /health`

Check if the API is running.

**Response:**
```json
{
  "status": "healthy"
}
```

---

## Strategies

### List All Strategies

#### `GET /api/strategies/`

Get list of all available trading strategies.

**Response:**
```json
{
  "strategies": [
    {
      "name": "SMA_Crossover",
      "description": "Simple Moving Average crossover strategy",
      "tags": ["trend_following", "moving_average"],
      "parameters": {
        "fast_period": 50,
        "slow_period": 200
      }
    }
  ]
}
```

### Get Strategy Details

#### `GET /api/strategies/{strategy_name}`

Get detailed information about a specific strategy.

**Path Parameters:**
- `strategy_name` (string): Name of the strategy

**Response:**
```json
{
  "name": "SMA_Crossover",
  "description": "Simple Moving Average crossover strategy (Golden/Death Cross)",
  "module": "crypto_trader.strategies.library.sma_crossover",
  "tags": ["trend_following", "moving_average", "crossover"],
  "parameters": {
    "fast_period": 50,
    "slow_period": 200
  }
}
```

---

## Data

### Get Available Symbols

#### `GET /api/data/symbols`

Get list of available trading pairs.

**Response:**
```json
{
  "symbols": ["BTC/USDT", "ETH/USDT", "BNB/USDT", ...]
}
```

### Get Available Timeframes

#### `GET /api/data/timeframes`

Get list of available candlestick timeframes.

**Response:**
```json
{
  "timeframes": ["1m", "5m", "15m", "1h", "4h", "1d"]
}
```

---

## Backtest

### Run Backtest

#### `POST /api/backtest/run`

Start a new backtest job.

**Request Body:**
```json
{
  "strategy_name": "SMA_Crossover",
  "symbol": "BTC/USDT",
  "timeframe": "1h",
  "days": 90,
  "initial_capital": 10000.0,
  "commission": 0.001,
  "parameters": {
    "fast_period": 50,
    "slow_period": 200
  }
}
```

**Response:**
```json
{
  "job_id": "ce3b5279-5329-4d35-a70f-4b4b2366bb03",
  "status": "pending",
  "progress": 0.0,
  "message": "Backtest queued for SMA_Crossover on BTC/USDT",
  "started_at": "2025-10-20T18:41:07.423Z"
}
```

### Get Backtest Status

#### `GET /api/backtest/{job_id}/status`

Get the current status of a backtest job.

**Path Parameters:**
- `job_id` (string): Unique job identifier

**Response:**
```json
{
  "job_id": "ce3b5279-5329-4d35-a70f-4b4b2366bb03",
  "status": "running",
  "progress": 0.5,
  "message": "Running backtest...",
  "started_at": "2025-10-20T18:41:07.423Z",
  "completed_at": null
}
```

**Status values:**
- `pending`: Job queued, not started yet
- `running`: Job currently executing
- `completed`: Job finished successfully
- `failed`: Job encountered an error

### Get Backtest Results

#### `GET /api/backtest/{job_id}/results`

Get results from a completed backtest.

**Path Parameters:**
- `job_id` (string): Unique job identifier

**Response:**
```json
{
  "job_id": "ce3b5279-5329-4d35-a70f-4b4b2366bb03",
  "strategy_name": "SMA_Crossover",
  "symbol": "BTC/USDT",
  "timeframe": "1h",
  "metrics": {
    "total_return": 0.152,
    "sharpe_ratio": 1.83,
    "max_drawdown": -0.08,
    "win_rate": 0.58,
    "total_trades": 42
  },
  "trades": [
    {
      "timestamp": "2025-09-15T10:00:00",
      "side": "buy",
      "price": 62500.0,
      "pnl": 125.50
    }
  ],
  "equity_curve": [
    {
      "timestamp": "2025-09-01T00:00:00",
      "equity": 10000.0
    },
    {
      "timestamp": "2025-09-01T01:00:00",
      "equity": 10125.5
    }
  ]
}
```

### List Recent Backtest Jobs

#### `GET /api/backtest/jobs?limit=50`

List recent backtest jobs.

**Query Parameters:**
- `limit` (integer, optional): Maximum number of jobs to return (default: 50)

**Response:**
```json
[
  {
    "job_id": "ce3b5279-5329-4d35-a70f-4b4b2366bb03",
    "status": "completed",
    "progress": 1.0,
    "message": "Backtest completed successfully",
    "started_at": "2025-10-20T18:41:07.423Z",
    "completed_at": "2025-10-20T18:41:19.347Z"
  }
]
```

---

## Benchmark

### Run Benchmark

#### `POST /api/benchmark/run`

Start automated benchmark comparing all strategies.

**Request Body:**
```json
{
  "symbols": ["BTC/USDT", "ETH/USDT"],
  "timeframes": ["1h", "4h", "1d"],
  "periods": [30, 90, 180],
  "strategies": null,
  "initial_capital": 10000.0,
  "commission": 0.001
}
```

**Fields:**
- `symbols`: Trading pairs to test
- `timeframes`: Candlestick timeframes to test
- `periods`: Historical periods in days
- `strategies`: Specific strategies to test (null = all strategies)
- `initial_capital`: Starting capital
- `commission`: Trading commission rate

**Response:**
```json
{
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "pending",
  "progress": 0.0,
  "message": "Queued 342 tests (19 strategies × 2 symbols × 3 timeframes × 3 periods)",
  "started_at": "2025-10-20T18:45:00.000Z",
  "total_tests": 342,
  "completed_tests": 0,
  "failed_tests": 0
}
```

### Get Benchmark Status

#### `GET /api/benchmark/{job_id}/status`

Get current status of a benchmark job.

**Path Parameters:**
- `job_id` (string): Unique job identifier

**Response:**
```json
{
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "running",
  "progress": 0.45,
  "message": "Testing SMA_Crossover on BTC/USDT 1h (154/342)",
  "started_at": "2025-10-20T18:45:00.000Z",
  "completed_at": null,
  "total_tests": 342,
  "completed_tests": 154,
  "failed_tests": 3
}
```

### Get Benchmark Results

#### `GET /api/benchmark/{job_id}/results`

Get results from a completed benchmark.

**Path Parameters:**
- `job_id` (string): Unique job identifier

**Response:**
```json
{
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "config": {
    "symbols": ["BTC/USDT", "ETH/USDT"],
    "timeframes": ["1h", "4h", "1d"],
    "periods": [30, 90, 180],
    "initial_capital": 10000.0,
    "commission": 0.001
  },
  "results": [
    {
      "strategy": "SMA_Crossover",
      "symbol": "BTC/USDT",
      "timeframe": "1h",
      "period_days": 90,
      "metrics": {
        "total_return": 0.152,
        "sharpe_ratio": 1.83,
        "max_drawdown": -0.08,
        "win_rate": 0.58,
        "total_trades": 42
      },
      "timestamp": "2025-10-20T18:45:30.123Z"
    }
  ],
  "summary": {
    "total_tests": 342,
    "profitable_tests": 198,
    "profitability_rate": 0.579,
    "avg_return": 0.089,
    "avg_sharpe": 1.23,
    "avg_drawdown": -0.12,
    "avg_win_rate": 0.52,
    "best_return": 0.452,
    "worst_return": -0.31
  },
  "rankings": {
    "by_return": [
      {
        "strategy": "Supertrend_ATR",
        "tests": 18,
        "avg_return": 0.234,
        "avg_sharpe": 2.1,
        "avg_drawdown": -0.09,
        "avg_win_rate": 0.61,
        "profitable_tests": 16,
        "profitability_rate": 0.889
      }
    ],
    "by_sharpe": [...],
    "by_drawdown": [...],
    "by_win_rate": [...],
    "by_consistency": [...]
  },
  "started_at": "2025-10-20T18:45:00.000Z",
  "completed_at": "2025-10-20T18:50:25.543Z"
}
```

### List Benchmark Jobs

#### `GET /api/benchmark/jobs?limit=50`

List recent benchmark jobs.

**Query Parameters:**
- `limit` (integer, optional): Maximum number of jobs to return (default: 50)

**Response:**
```json
[
  {
    "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "status": "completed",
    "progress": 1.0,
    "message": "Completed 339 tests (3 failed)",
    "started_at": "2025-10-20T18:45:00.000Z",
    "completed_at": "2025-10-20T18:50:25.543Z",
    "total_tests": 342,
    "completed_tests": 339,
    "failed_tests": 3
  }
]
```

---

## Error Responses

All endpoints return standard error responses:

### 400 Bad Request
```json
{
  "detail": "Job not completed yet. Status: running"
}
```

### 404 Not Found
```json
{
  "detail": "Job ce3b5279-5329-4d35-a70f-4b4b2366bb03 not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Strategy 'InvalidStrategy' not found"
}
```

---

## Rate Limiting

- Binance API: 1200 requests/minute
- Local caching with 5-minute TTL for OHLCV data
- Benchmark jobs reuse single data fetcher instance for performance

---

## Performance Notes

### Benchmark Optimization
The benchmark endpoint has been optimized to reuse a single `BinanceDataFetcher` instance across all tests. This provides ~340x speedup on initialization:

- **Before:** 342 tests × 3 seconds = ~17 minutes initialization
- **After:** 1 × 3 seconds = ~3 seconds initialization

### Data Caching
- OHLCV data is cached with 5-minute TTL
- Cached data served from disk when available
- Reduces API calls to Binance significantly

---

## Examples

### Python Client Example

```python
import requests

API_BASE = "http://localhost:8001"

# Start a backtest
response = requests.post(f"{API_BASE}/api/backtest/run", json={
    "strategy_name": "SMA_Crossover",
    "symbol": "BTC/USDT",
    "timeframe": "1h",
    "days": 90,
    "initial_capital": 10000.0,
    "commission": 0.001,
    "parameters": {
        "fast_period": 50,
        "slow_period": 200
    }
})

job_id = response.json()["job_id"]
print(f"Started backtest: {job_id}")

# Check status
import time
while True:
    status_response = requests.get(f"{API_BASE}/api/backtest/{job_id}/status")
    status = status_response.json()

    if status["status"] == "completed":
        break
    elif status["status"] == "failed":
        print(f"Backtest failed: {status['message']}")
        exit(1)

    print(f"Progress: {status['progress']:.1%}")
    time.sleep(1)

# Get results
results_response = requests.get(f"{API_BASE}/api/backtest/{job_id}/results")
results = results_response.json()

print(f"Total Return: {results['metrics']['total_return']:.2%}")
print(f"Sharpe Ratio: {results['metrics']['sharpe_ratio']:.2f}")
print(f"Max Drawdown: {results['metrics']['max_drawdown']:.2%}")
```

### cURL Example

```bash
# Start a backtest
curl -X POST http://localhost:8001/api/backtest/run \
  -H "Content-Type: application/json" \
  -d '{
    "strategy_name": "SMA_Crossover",
    "symbol": "BTC/USDT",
    "timeframe": "1h",
    "days": 90,
    "initial_capital": 10000.0,
    "commission": 0.001,
    "parameters": {
      "fast_period": 50,
      "slow_period": 200
    }
  }'

# Check status
curl http://localhost:8001/api/backtest/{job_id}/status

# Get results
curl http://localhost:8001/api/backtest/{job_id}/results
```

---

## Starting the API

```bash
# Start API server
./scripts/start_api.sh

# Or manually
source venv/bin/activate
uvicorn crypto_trader.api.main:app --reload --port 8001 --host 0.0.0.0
```

## API Documentation (Interactive)

Once the API is running, visit:
- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

---

## Technical Implementation

### Background Tasks
Backtests and benchmarks run as FastAPI background tasks:
- Non-blocking: API responds immediately with job_id
- Async execution: Multiple jobs can run concurrently
- Status polling: Check progress via status endpoint

### Data Storage
- In-memory storage for jobs (TODO: migrate to database)
- OHLCV data cached on disk in `data/ohlcv/`
- File format: CSV with columns: timestamp, open, high, low, close, volume

### Architecture
```
API Request → Route Handler → Background Task
                ↓
            Job Created (pending)
                ↓
            Background Execution (running)
                ↓
            Store Results (completed)
                ↓
            Client Polls Status/Results
```

---

## Troubleshooting

### API Won't Start
```bash
# Check if port 8001 is in use
lsof -ti:8001

# Kill existing processes
lsof -ti:8001 | xargs kill -9

# Restart API
./scripts/start_api.sh
```

### Backtest Fails with "Insufficient Data"
- Strategy requires more data than available
- Example: SMA(200) needs 200+ candles
- Solution: Increase `days` parameter or use smaller periods

### Benchmark Running Slow
- Should be ~340x faster after optimization
- If still slow, check API logs for errors
- Ensure BinanceDataFetcher is being reused (check logs for "Initialized shared BinanceDataFetcher")

---

## See Also
- [Walk-Forward Optimization](../src/crypto_trader/optimization/README.md)
- [Strategy Development Guide](STRATEGIES.md)
- [CHANGELOG](../CHANGELOG.md)
