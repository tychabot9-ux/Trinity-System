#!/bin/bash
# Trinity VR Endpoint Testing Script
# Tests all API endpoints and network connectivity

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "╔════════════════════════════════════════════════════════╗"
echo "║        TRINITY VR ENDPOINT TESTING                     ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Get network info
get_local_ip() {
    python3 -c "import socket; s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.connect(('8.8.8.8', 80)); print(s.getsockname()[0]); s.close()" 2>/dev/null || echo "Not available"
}

get_tailscale_ip() {
    tailscale ip -4 2>/dev/null || echo "Not available"
}

LOCAL_IP=$(get_local_ip)
TAILSCALE_IP=$(get_tailscale_ip)
PORT=8503

echo "🌐 Testing Network Addresses:"
echo "   Local IP:      $LOCAL_IP"
echo "   Tailscale IP:  $TAILSCALE_IP"
echo ""

# Test function
test_endpoint() {
    local name="$1"
    local url="$2"
    local method="${3:-GET}"
    local data="$4"

    echo -n "Testing $name... "

    if [ "$method" = "POST" ]; then
        response=$(curl -s -w "\n%{http_code}" -X POST "$url" \
                   -H "Content-Type: application/json" \
                   -d "$data" 2>/dev/null)
    else
        response=$(curl -s -w "\n%{http_code}" "$url" 2>/dev/null)
    fi

    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)

    if [ "$http_code" = "200" ]; then
        echo -e "${GREEN}✅ PASS${NC} (HTTP $http_code)"
        if [ -n "$body" ]; then
            echo "$body" | python3 -m json.tool 2>/dev/null | head -10 | sed 's/^/   /'
        fi
        return 0
    else
        echo -e "${RED}❌ FAIL${NC} (HTTP $http_code)"
        if [ -n "$body" ]; then
            echo "$body" | head -5 | sed 's/^/   /'
        fi
        return 1
    fi
}

# Test counter
TOTAL_TESTS=0
PASSED_TESTS=0

# Test localhost
echo "════════════════════════════════════════════════════════════"
echo "1. Testing Localhost (127.0.0.1)"
echo "════════════════════════════════════════════════════════════"
echo ""

((TOTAL_TESTS++))
if test_endpoint "GET /" "http://localhost:$PORT/vr"; then
    ((PASSED_TESTS++))
fi
echo ""

((TOTAL_TESTS++))
if test_endpoint "GET /api/status" "http://localhost:$PORT/api/status"; then
    ((PASSED_TESTS++))
fi
echo ""

((TOTAL_TESTS++))
if test_endpoint "GET /api/models" "http://localhost:$PORT/api/models"; then
    ((PASSED_TESTS++))
fi
echo ""

((TOTAL_TESTS++))
if test_endpoint "POST /api/generate_cad" "http://localhost:$PORT/api/generate_cad" "POST" '{"prompt":"test"}'; then
    ((PASSED_TESTS++))
fi
echo ""

# Test local IP
if [ "$LOCAL_IP" != "Not available" ]; then
    echo "════════════════════════════════════════════════════════════"
    echo "2. Testing Local WiFi ($LOCAL_IP)"
    echo "════════════════════════════════════════════════════════════"
    echo ""

    ((TOTAL_TESTS++))
    if test_endpoint "GET /api/status" "http://$LOCAL_IP:$PORT/api/status"; then
        ((PASSED_TESTS++))
    fi
    echo ""

    ((TOTAL_TESTS++))
    if test_endpoint "GET /api/models" "http://$LOCAL_IP:$PORT/api/models"; then
        ((PASSED_TESTS++))
    fi
    echo ""
fi

# Test Tailscale IP
if [ "$TAILSCALE_IP" != "Not available" ]; then
    echo "════════════════════════════════════════════════════════════"
    echo "3. Testing Tailscale VPN ($TAILSCALE_IP)"
    echo "════════════════════════════════════════════════════════════"
    echo ""

    ((TOTAL_TESTS++))
    if test_endpoint "GET /api/status" "http://$TAILSCALE_IP:$PORT/api/status"; then
        ((PASSED_TESTS++))
    fi
    echo ""

    ((TOTAL_TESTS++))
    if test_endpoint "GET /api/models" "http://$TAILSCALE_IP:$PORT/api/models"; then
        ((PASSED_TESTS++))
    fi
    echo ""
fi

# Test CORS headers
echo "════════════════════════════════════════════════════════════"
echo "4. Testing CORS Headers"
echo "════════════════════════════════════════════════════════════"
echo ""

echo -n "Testing CORS on /api/status... "
CORS_HEADER=$(curl -s -I http://localhost:$PORT/api/status | grep -i "access-control-allow-origin")
if echo "$CORS_HEADER" | grep -q "\*"; then
    echo -e "${GREEN}✅ PASS${NC}"
    echo "   $CORS_HEADER"
    ((TOTAL_TESTS++))
    ((PASSED_TESTS++))
else
    echo -e "${RED}❌ FAIL${NC}"
    echo "   CORS header not found or incorrect"
    ((TOTAL_TESTS++))
fi
echo ""

# Network performance test
echo "════════════════════════════════════════════════════════════"
echo "5. Network Performance Test"
echo "════════════════════════════════════════════════════════════"
echo ""

echo "Testing response times (10 requests)..."
echo ""

for i in {1..10}; do
    TIME=$(curl -s -w "%{time_total}" -o /dev/null http://localhost:$PORT/api/status)
    TIME_MS=$(echo "$TIME * 1000" | bc)
    printf "   Request %2d: %.2f ms\n" $i $TIME_MS
done

echo ""

# Summary
echo "════════════════════════════════════════════════════════════"
echo "TEST SUMMARY"
echo "════════════════════════════════════════════════════════════"
echo ""

PERCENTAGE=$((PASSED_TESTS * 100 / TOTAL_TESTS))

if [ $PASSED_TESTS -eq $TOTAL_TESTS ]; then
    echo -e "${GREEN}✅ ALL TESTS PASSED${NC}"
else
    echo -e "${YELLOW}⚠️  SOME TESTS FAILED${NC}"
fi

echo ""
echo "Results: $PASSED_TESTS / $TOTAL_TESTS passed ($PERCENTAGE%)"
echo ""

if [ $PASSED_TESTS -eq $TOTAL_TESTS ]; then
    echo "╔════════════════════════════════════════════════════════╗"
    echo "║               SYSTEM READY FOR VR                      ║"
    echo "╚════════════════════════════════════════════════════════╝"
    echo ""
    echo "🥽 Quest Access URLs:"
    if [ "$LOCAL_IP" != "Not available" ]; then
        echo "   Local WiFi:  http://$LOCAL_IP:$PORT/vr"
    fi
    if [ "$TAILSCALE_IP" != "Not available" ]; then
        echo "   Tailscale:   http://$TAILSCALE_IP:$PORT/vr"
    fi
    echo ""
    echo "Ready to use! Open one of these URLs in Quest browser."
    exit 0
else
    echo "╔════════════════════════════════════════════════════════╗"
    echo "║           ISSUES DETECTED - TROUBLESHOOTING            ║"
    echo "╚════════════════════════════════════════════════════════╝"
    echo ""
    echo "Common fixes:"
    echo "   1. Ensure server is running: ./AUTO_DEPLOY_VR.sh"
    echo "   2. Check firewall: ./configure_firewall.sh"
    echo "   3. Verify network: ping $LOCAL_IP"
    echo "   4. Check logs: tail -f logs/vr_server.log"
    echo ""
    exit 1
fi
