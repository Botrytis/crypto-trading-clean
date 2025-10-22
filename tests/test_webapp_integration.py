#!/usr/bin/env python3
"""
Comprehensive Web App Integration Tests

Tests all major functionality of the crypto trading platform:
1. API connectivity
2. Strategy loading
3. Backtest execution
4. Benchmark execution
5. Data fetching
6. Error handling
"""

import requests
import time
import json
from datetime import datetime

API_BASE = "http://localhost:8001"

class Colors:
    PASS = '\033[92m'
    FAIL = '\033[91m'
    INFO = '\033[94m'
    WARN = '\033[93m'
    END = '\033[0m'

def print_test(name, passed, details=""):
    status = f"{Colors.PASS}✓ PASS{Colors.END}" if passed else f"{Colors.FAIL}✗ FAIL{Colors.END}"
    print(f"{status} {name}")
    if details:
        print(f"     {details}")

def test_api_health():
    """Test API health endpoint"""
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        passed = response.status_code == 200 and response.json().get("status") == "healthy"
        print_test("API Health Check", passed, f"Status: {response.json().get('status')}")
        return passed
    except Exception as e:
        print_test("API Health Check", False, f"Error: {e}")
        return False

def test_list_strategies():
    """Test listing all strategies"""
    try:
        response = requests.get(f"{API_BASE}/api/strategies/", timeout=10)
        data = response.json()

        strategies = data.get("strategies", [])
        passed = response.status_code == 200 and len(strategies) > 0

        print_test("List Strategies", passed, f"Found {len(strategies)} strategies")

        if passed:
            print(f"     Sample strategies: {', '.join([s['name'] for s in strategies[:5]])}")

        return passed, strategies
    except Exception as e:
        print_test("List Strategies", False, f"Error: {e}")
        return False, []

def test_get_strategy_details(strategy_name="SMA_Crossover"):
    """Test getting strategy details"""
    try:
        response = requests.get(f"{API_BASE}/api/strategies/{strategy_name}", timeout=5)
        data = response.json()

        passed = response.status_code == 200 and data.get("name") == strategy_name
        print_test(f"Get Strategy Details ({strategy_name})", passed,
                   f"Description: {data.get('description', 'N/A')[:60]}...")
        return passed
    except Exception as e:
        print_test(f"Get Strategy Details ({strategy_name})", False, f"Error: {e}")
        return False

def test_get_data_symbols():
    """Test getting available symbols"""
    try:
        response = requests.get(f"{API_BASE}/api/data/symbols", timeout=5)
        data = response.json()

        # API returns list of symbol objects
        symbols = [s["symbol"] for s in data] if isinstance(data, list) else []
        passed = response.status_code == 200 and "BTC/USDT" in symbols

        print_test("Get Data Symbols", passed, f"Found {len(symbols)} symbols")
        return passed
    except Exception as e:
        print_test("Get Data Symbols", False, f"Error: {e}")
        return False

def test_get_timeframes():
    """Test getting available timeframes"""
    try:
        response = requests.get(f"{API_BASE}/api/data/timeframes", timeout=5)
        data = response.json()

        # API returns list of timeframe objects
        timeframes = [t["value"] for t in data] if isinstance(data, list) else []
        passed = response.status_code == 200 and "1h" in timeframes

        print_test("Get Timeframes", passed, f"Timeframes: {', '.join(timeframes[:8])}")
        return passed
    except Exception as e:
        print_test("Get Timeframes", False, f"Error: {e}")
        return False

def test_run_backtest():
    """Test running a backtest"""
    try:
        # Start backtest
        request_data = {
            "strategy_name": "SMA_Crossover",
            "symbol": "BTC/USDT",
            "timeframe": "1h",
            "days": 30,  # Short test
            "initial_capital": 10000.0,
            "commission": 0.001,
            "parameters": {
                "fast_period": 20,
                "slow_period": 50
            }
        }

        response = requests.post(f"{API_BASE}/api/backtest/run", json=request_data, timeout=30)
        data = response.json()

        job_id = data.get("job_id")
        passed = response.status_code == 200 and job_id is not None

        print_test("Start Backtest", passed, f"Job ID: {job_id}")

        if not passed:
            return False, None

        # Poll for completion
        max_wait = 60  # 60 seconds max
        start_time = time.time()

        while time.time() - start_time < max_wait:
            status_response = requests.get(f"{API_BASE}/api/backtest/{job_id}/status", timeout=5)
            status_data = status_response.json()

            status = status_data.get("status")
            progress = status_data.get("progress", 0)

            if status == "completed":
                print_test("Backtest Completion", True,
                          f"Completed in {int(time.time() - start_time)}s")
                return True, job_id
            elif status == "failed":
                print_test("Backtest Completion", False,
                          f"Failed: {status_data.get('message')}")
                return False, None

            print(f"     Progress: {progress:.0%} ({status})")
            time.sleep(2)

        print_test("Backtest Completion", False, "Timeout waiting for completion")
        return False, None

    except Exception as e:
        print_test("Run Backtest", False, f"Error: {e}")
        return False, None

def test_get_backtest_results(job_id):
    """Test getting backtest results"""
    try:
        response = requests.get(f"{API_BASE}/api/backtest/{job_id}/results", timeout=10)
        data = response.json()

        metrics = data.get("metrics", {})
        trades = data.get("trades", [])
        equity_curve = data.get("equity_curve", [])

        passed = (
            response.status_code == 200 and
            "total_return" in metrics and
            isinstance(trades, list) and
            isinstance(equity_curve, list)
        )

        if passed:
            details = (
                f"Return: {metrics.get('total_return', 0):.2%}, "
                f"Sharpe: {metrics.get('sharpe_ratio', 0):.2f}, "
                f"Trades: {metrics.get('total_trades', 0)}, "
                f"Equity points: {len(equity_curve)}"
            )
        else:
            details = "Invalid response format"

        print_test("Get Backtest Results", passed, details)
        return passed
    except Exception as e:
        print_test("Get Backtest Results", False, f"Error: {e}")
        return False

def test_list_backtest_jobs():
    """Test listing backtest jobs"""
    try:
        response = requests.get(f"{API_BASE}/api/backtest/jobs?limit=5", timeout=5)
        data = response.json()

        passed = response.status_code == 200 and isinstance(data, list)
        print_test("List Backtest Jobs", passed, f"Found {len(data)} recent jobs")
        return passed
    except Exception as e:
        print_test("List Backtest Jobs", False, f"Error: {e}")
        return False

def test_benchmark_workflow():
    """Test benchmark workflow (without waiting for completion due to time)"""
    try:
        request_data = {
            "symbols": ["BTC/USDT"],
            "timeframes": ["1h"],
            "periods": [7],  # Very short for testing
            "strategies": ["SMA_Crossover", "RSI_MeanReversion"],  # Just 2 strategies
            "initial_capital": 10000.0,
            "commission": 0.001
        }

        response = requests.post(f"{API_BASE}/api/benchmark/run", json=request_data, timeout=10)
        data = response.json()

        job_id = data.get("job_id")
        total_tests = data.get("total_tests", 0)

        passed = response.status_code == 200 and job_id is not None
        print_test("Start Benchmark", passed,
                   f"Job ID: {job_id}, Total tests: {total_tests}")

        if passed:
            # Check status once
            time.sleep(2)
            status_response = requests.get(f"{API_BASE}/api/benchmark/{job_id}/status", timeout=5)
            status_data = status_response.json()

            print(f"     Initial status: {status_data.get('status')}, "
                  f"Progress: {status_data.get('progress', 0):.0%}")

        return passed
    except Exception as e:
        print_test("Benchmark Workflow", False, f"Error: {e}")
        return False

def test_error_handling():
    """Test API error handling"""
    tests_passed = 0
    total_tests = 3

    # Test 1: Invalid strategy
    try:
        response = requests.get(f"{API_BASE}/api/strategies/InvalidStrategy", timeout=5)
        if response.status_code == 404:
            print_test("Error Handling - Invalid Strategy", True, "Returns 404")
            tests_passed += 1
        else:
            print_test("Error Handling - Invalid Strategy", False,
                      f"Expected 404, got {response.status_code}")
    except Exception as e:
        print_test("Error Handling - Invalid Strategy", False, f"Error: {e}")

    # Test 2: Invalid job ID
    try:
        response = requests.get(f"{API_BASE}/api/backtest/invalid-job-id/status", timeout=5)
        if response.status_code == 404:
            print_test("Error Handling - Invalid Job ID", True, "Returns 404")
            tests_passed += 1
        else:
            print_test("Error Handling - Invalid Job ID", False,
                      f"Expected 404, got {response.status_code}")
    except Exception as e:
        print_test("Error Handling - Invalid Job ID", False, f"Error: {e}")

    # Test 3: Invalid backtest request
    try:
        response = requests.post(f"{API_BASE}/api/backtest/run",
                                json={"invalid": "data"}, timeout=5)
        if response.status_code == 422:  # Validation error
            print_test("Error Handling - Invalid Request", True, "Returns 422")
            tests_passed += 1
        else:
            print_test("Error Handling - Invalid Request", False,
                      f"Expected 422, got {response.status_code}")
    except Exception as e:
        print_test("Error Handling - Invalid Request", False, f"Error: {e}")

    return tests_passed == total_tests

def main():
    """Run all tests"""
    print(f"\n{Colors.INFO}{'=' * 70}{Colors.END}")
    print(f"{Colors.INFO}Crypto Trading Platform - Integration Tests{Colors.END}")
    print(f"{Colors.INFO}{'=' * 70}{Colors.END}\n")

    print(f"Testing API at: {API_BASE}")
    print(f"Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    results = []

    # Core API Tests
    print(f"\n{Colors.INFO}=== Core API Tests ==={Colors.END}")
    results.append(("API Health", test_api_health()))

    # Strategy Tests
    print(f"\n{Colors.INFO}=== Strategy Tests ==={Colors.END}")
    passed, strategies = test_list_strategies()
    results.append(("List Strategies", passed))
    results.append(("Get Strategy Details", test_get_strategy_details()))

    # Data Tests
    print(f"\n{Colors.INFO}=== Data Tests ==={Colors.END}")
    results.append(("Get Data Symbols", test_get_data_symbols()))
    results.append(("Get Timeframes", test_get_timeframes()))

    # Backtest Tests
    print(f"\n{Colors.INFO}=== Backtest Tests ==={Colors.END}")
    backtest_passed, job_id = test_run_backtest()
    results.append(("Run Backtest", backtest_passed))

    if backtest_passed and job_id:
        results.append(("Get Backtest Results", test_get_backtest_results(job_id)))
    else:
        print_test("Get Backtest Results", False, "Skipped (backtest failed)")
        results.append(("Get Backtest Results", False))

    results.append(("List Backtest Jobs", test_list_backtest_jobs()))

    # Benchmark Tests
    print(f"\n{Colors.INFO}=== Benchmark Tests ==={Colors.END}")
    results.append(("Benchmark Workflow", test_benchmark_workflow()))

    # Error Handling Tests
    print(f"\n{Colors.INFO}=== Error Handling Tests ==={Colors.END}")
    results.append(("Error Handling", test_error_handling()))

    # Summary
    print(f"\n{Colors.INFO}{'=' * 70}{Colors.END}")
    print(f"{Colors.INFO}Test Summary{Colors.END}")
    print(f"{Colors.INFO}{'=' * 70}{Colors.END}\n")

    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    pass_rate = (passed_count / total_count * 100) if total_count > 0 else 0

    for name, passed in results:
        status = f"{Colors.PASS}PASS{Colors.END}" if passed else f"{Colors.FAIL}FAIL{Colors.END}"
        print(f"  {status}  {name}")

    print(f"\n{Colors.INFO}Overall: {passed_count}/{total_count} tests passed ({pass_rate:.1f}%){Colors.END}\n")

    if pass_rate == 100:
        print(f"{Colors.PASS}✓ All tests passed!{Colors.END}\n")
        return 0
    elif pass_rate >= 80:
        print(f"{Colors.WARN}⚠ Most tests passed, but some failures detected{Colors.END}\n")
        return 1
    else:
        print(f"{Colors.FAIL}✗ Multiple test failures detected{Colors.END}\n")
        return 1

if __name__ == "__main__":
    exit(main())
