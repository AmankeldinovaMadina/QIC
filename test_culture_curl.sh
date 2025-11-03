#!/bin/bash
# cURL test for the culture guide endpoint

echo "================================"
echo "Testing Culture Guide Endpoint"
echo "================================"
echo ""

# Test 1: Tokyo
echo "Test 1: Tokyo, Japan"
echo "--------------------"
curl -X POST "http://localhost:8001/api/v1/culture-guide" \
  -H "Content-Type: application/json" \
  -d '{
    "destination": "Tokyo, Japan",
    "language": "en"
  }' | python3 -m json.tool

echo ""
echo ""

# Test 2: Dubai
echo "Test 2: Dubai, UAE"
echo "------------------"
curl -X POST "http://localhost:8001/api/v1/culture-guide" \
  -H "Content-Type: application/json" \
  -d '{
    "destination": "Dubai, UAE"
  }' | python3 -m json.tool

echo ""
echo ""

# Test 3: Paris
echo "Test 3: Paris, France"
echo "---------------------"
curl -X POST "http://localhost:8001/api/v1/culture-guide" \
  -H "Content-Type: application/json" \
  -d '{
    "destination": "Paris"
  }' | python3 -m json.tool
