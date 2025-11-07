#!/bin/bash

# Load Testing Script for ResuMatch AI
# Tests API performance with different load levels

echo "=========================================="
echo "ResuMatch AI - Load Testing Suite"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
HOST="http://localhost:8001"
RESULTS_DIR="/app/tests/load_test_results"

# Create results directory
mkdir -p $RESULTS_DIR

echo -e "${YELLOW}Creating demo user for testing...${NC}"
curl -X POST "$HOST/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Load Test User",
    "email": "loadtest@resumatch.com",
    "password": "LoadTest123!"
  }' 2>/dev/null
echo ""
echo ""

# Test 1: Light Load (10 users)
echo -e "${GREEN}Test 1: Light Load - 10 concurrent users${NC}"
echo "Duration: 2 minutes"
echo "Starting..."
locust -f /app/tests/load_test.py \
  --host=$HOST \
  --users 10 \
  --spawn-rate 2 \
  --run-time 2m \
  --headless \
  --html=$RESULTS_DIR/light_load_report.html \
  --csv=$RESULTS_DIR/light_load

echo ""
echo -e "${GREEN}✓ Light load test complete${NC}"
echo "Report saved to: $RESULTS_DIR/light_load_report.html"
echo ""
sleep 5

# Test 2: Medium Load (50 users)
echo -e "${GREEN}Test 2: Medium Load - 50 concurrent users${NC}"
echo "Duration: 3 minutes"
echo "Starting..."
locust -f /app/tests/load_test.py \
  --host=$HOST \
  --users 50 \
  --spawn-rate 5 \
  --run-time 3m \
  --headless \
  --html=$RESULTS_DIR/medium_load_report.html \
  --csv=$RESULTS_DIR/medium_load

echo ""
echo -e "${GREEN}✓ Medium load test complete${NC}"
echo "Report saved to: $RESULTS_DIR/medium_load_report.html"
echo ""
sleep 5

# Test 3: High Load (100 users)
echo -e "${GREEN}Test 3: High Load - 100 concurrent users${NC}"
echo "Duration: 3 minutes"
echo "Starting..."
locust -f /app/tests/load_test.py \
  --host=$HOST \
  --users 100 \
  --spawn-rate 10 \
  --run-time 3m \
  --headless \
  --html=$RESULTS_DIR/high_load_report.html \
  --csv=$RESULTS_DIR/high_load

echo ""
echo -e "${GREEN}✓ High load test complete${NC}"
echo "Report saved to: $RESULTS_DIR/high_load_report.html"
echo ""

# Summary
echo ""
echo "=========================================="
echo -e "${GREEN}ALL LOAD TESTS COMPLETE${NC}"
echo "=========================================="
echo ""
echo "Results saved in: $RESULTS_DIR"
echo ""
echo "Reports:"
echo "  - Light Load (10 users):  $RESULTS_DIR/light_load_report.html"
echo "  - Medium Load (50 users): $RESULTS_DIR/medium_load_report.html"
echo "  - High Load (100 users):  $RESULTS_DIR/high_load_report.html"
echo ""
echo "CSV Data:"
echo "  - Light Load:  $RESULTS_DIR/light_load_stats.csv"
echo "  - Medium Load: $RESULTS_DIR/medium_load_stats.csv"
echo "  - High Load:   $RESULTS_DIR/high_load_stats.csv"
echo ""
echo "=========================================="

# Generate summary report
echo ""
echo "📊 PERFORMANCE BENCHMARKS SUMMARY"
echo "=========================================="
echo ""

if [ -f "$RESULTS_DIR/light_load_stats.csv" ]; then
    echo "Light Load (10 users):"
    tail -1 "$RESULTS_DIR/light_load_stats.csv" | awk -F',' '{printf "  Avg Response: %sms | RPS: %s | Failures: %s\n", $5, $10, $4}'
fi

if [ -f "$RESULTS_DIR/medium_load_stats.csv" ]; then
    echo "Medium Load (50 users):"
    tail -1 "$RESULTS_DIR/medium_load_stats.csv" | awk -F',' '{printf "  Avg Response: %sms | RPS: %s | Failures: %s\n", $5, $10, $4}'
fi

if [ -f "$RESULTS_DIR/high_load_stats.csv" ]; then
    echo "High Load (100 users):"
    tail -1 "$RESULTS_DIR/high_load_stats.csv" | awk -F',' '{printf "  Avg Response: %sms | RPS: %s | Failures: %s\n", $5, $10, $4}'
fi

echo ""
echo "=========================================="
echo ""
echo -e "${YELLOW}To run interactive load test:${NC}"
echo "  locust -f /app/tests/load_test.py --host=$HOST"
echo "  Then open http://localhost:8089 in your browser"
echo ""
