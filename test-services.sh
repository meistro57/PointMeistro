#!/bin/bash

echo "========================================="
echo "TESTING POINTMEISTRO SERVICES"
echo "========================================="
echo ""

echo "1. Testing Laravel App (http://localhost/)..."
curl -s http://localhost/ | head -20
echo ""
echo ""

echo "2. Testing Horizon Dashboard (http://localhost/horizon)..."
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://localhost/horizon
echo ""

echo "3. Testing Python Segmentation Service (http://localhost:8001/)..."
curl -s http://localhost:8001/
echo ""
echo ""

echo "4. Checking All Container Status..."
docker compose ps
echo ""

echo "5. Checking Container Logs (last 10 lines)..."
echo ""
echo "--- Laravel App ---"
docker compose logs --tail=10 app
echo ""
echo "--- Python Segmenter ---"
docker compose logs --tail=10 python-segmenter
echo ""
echo "--- Horizon ---"
docker compose logs --tail=10 horizon
echo ""

echo "========================================="
echo "TEST COMPLETE"
echo "========================================="
