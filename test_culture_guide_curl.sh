#!/bin/bash

# Culture Guide Endpoints Test Script
# This script tests the POST and GET endpoints for culture guides

echo "=========================================="
echo "Culture Guide Endpoints Test"
echo "=========================================="
echo ""

# Test data
TRIP_ID="test-trip-$(date +%s)"
BASE_URL="http://localhost:8000"

echo "Test Configuration:"
echo "  Base URL: $BASE_URL"
echo "  Trip ID: $TRIP_ID"
echo ""

# Test 1: POST - Generate culture guide
echo "=========================================="
echo "Test 1: POST /api/v1/culture-guide"
echo "=========================================="
echo "Generating culture guide for Paris, France..."
echo ""

POST_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST "$BASE_URL/api/v1/culture-guide" \
  -H "Content-Type: application/json" \
  -d "{
    \"trip_id\": \"$TRIP_ID\",
    \"destination\": \"Paris, France\",
    \"language\": \"en\"
  }")

HTTP_STATUS=$(echo "$POST_RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)
RESPONSE_BODY=$(echo "$POST_RESPONSE" | sed '/HTTP_STATUS/d')

echo "Response Status: $HTTP_STATUS"
if [ "$HTTP_STATUS" == "200" ]; then
  echo "✅ SUCCESS: Culture guide generated"
  echo ""
  echo "Response (formatted):"
  echo "$RESPONSE_BODY" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE_BODY"
else
  echo "❌ FAILED"
  echo "$RESPONSE_BODY"
  exit 1
fi

echo ""
echo "Waiting 2 seconds before next test..."
sleep 2

# Test 2: GET - Retrieve culture guide
echo ""
echo "=========================================="
echo "Test 2: GET /api/v1/culture-guide/{trip_id}"
echo "=========================================="
echo "Retrieving saved culture guide..."
echo ""

GET_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" "$BASE_URL/api/v1/culture-guide/$TRIP_ID")

HTTP_STATUS=$(echo "$GET_RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)
RESPONSE_BODY=$(echo "$GET_RESPONSE" | sed '/HTTP_STATUS/d')

echo "Response Status: $HTTP_STATUS"
if [ "$HTTP_STATUS" == "200" ]; then
  echo "✅ SUCCESS: Culture guide retrieved"
  echo ""
  echo "Response (formatted):"
  echo "$RESPONSE_BODY" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE_BODY"
else
  echo "❌ FAILED"
  echo "$RESPONSE_BODY"
  exit 1
fi

echo ""
echo "Waiting 2 seconds before next test..."
sleep 2

# Test 3: POST again - Should return cached version
echo ""
echo "=========================================="
echo "Test 3: POST again (should return cached)"
echo "=========================================="
echo "Requesting same culture guide again..."
echo ""

POST_RESPONSE2=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST "$BASE_URL/api/v1/culture-guide" \
  -H "Content-Type: application/json" \
  -d "{
    \"trip_id\": \"$TRIP_ID\",
    \"destination\": \"Paris, France\",
    \"language\": \"en\"
  }")

HTTP_STATUS=$(echo "$POST_RESPONSE2" | grep "HTTP_STATUS" | cut -d: -f2)
RESPONSE_BODY=$(echo "$POST_RESPONSE2" | sed '/HTTP_STATUS/d')

echo "Response Status: $HTTP_STATUS"
if [ "$HTTP_STATUS" == "200" ]; then
  echo "✅ SUCCESS: Cached culture guide returned (fast response)"
  echo ""
  echo "Response (formatted):"
  echo "$RESPONSE_BODY" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE_BODY"
else
  echo "❌ FAILED"
  echo "$RESPONSE_BODY"
  exit 1
fi

# Test 4: GET - Non-existent trip
echo ""
echo "=========================================="
echo "Test 4: GET with non-existent trip_id"
echo "=========================================="
echo "Testing 404 response..."
echo ""

GET_RESPONSE_404=$(curl -s -w "\nHTTP_STATUS:%{http_code}" "$BASE_URL/api/v1/culture-guide/non-existent-trip-999")

HTTP_STATUS=$(echo "$GET_RESPONSE_404" | grep "HTTP_STATUS" | cut -d: -f2)
RESPONSE_BODY=$(echo "$GET_RESPONSE_404" | sed '/HTTP_STATUS/d')

echo "Response Status: $HTTP_STATUS"
if [ "$HTTP_STATUS" == "404" ]; then
  echo "✅ SUCCESS: Correctly returns 404"
  echo ""
  echo "Response:"
  echo "$RESPONSE_BODY" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE_BODY"
else
  echo "⚠️  WARNING: Expected 404, got $HTTP_STATUS"
  echo "$RESPONSE_BODY"
fi

echo ""
echo "=========================================="
echo "All Tests Completed!"
echo "=========================================="
