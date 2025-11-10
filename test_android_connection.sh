#!/bin/bash

echo "=========================================="
echo "Android Emulator Connection Test"
echo "=========================================="
echo ""

echo "1. Testing Backend Health from localhost:"
curl -s http://localhost:8001/api/health | python3 -m json.tool || echo "❌ Backend not responding"
echo ""
echo ""

echo "2. Testing Backend Registration Endpoint:"
RANDOM_USER="testuser_$(date +%s)"
RESPONSE=$(curl -s -X POST http://localhost:8001/api/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$RANDOM_USER\",\"password\":\"testpass123\"}")
echo "$RESPONSE" | python3 -m json.tool || echo "$RESPONSE"
echo ""
echo ""

echo "3. Current Frontend Configuration:"
echo "   EXPO_PUBLIC_BACKEND_URL=$(grep EXPO_PUBLIC_BACKEND_URL /app/frontend/.env | cut -d'=' -f2)"
echo ""
echo ""

echo "4. Backend is listening on:"
netstat -tuln | grep 8001 || echo "   ❌ Backend not listening on port 8001"
echo ""
echo ""

echo "=========================================="
echo "Instructions for Android Emulator:"
echo "=========================================="
echo "1. Close the app completely on emulator"
echo "2. Reopen the app"
echo "3. Try to Sign Up with:"
echo "   Username: testuser"
echo "   Password: test123"
echo ""
echo "If still getting Network Error:"
echo "- Make sure backend is running: uvicorn server:app --host 0.0.0.0 --port 8001 --reload"
echo "- Check emulator can reach 10.0.2.2:8001"
echo "=========================================="
