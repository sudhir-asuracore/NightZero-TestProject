#!/usr/bin/env bash
# ==============================================================================
# NightZero Test Traffic & Outage Trigger CLI
#
# Usage:
#   ./trigger_traffic.sh                    # Exercise all 5 modules once
#   ./trigger_traffic.sh --module tax       # Exercise only Tax & Fees
#   ./trigger_traffic.sh --module pricing   # Exercise only Pricing (Checkout)
#   ./trigger_traffic.sh --module discounts # Exercise only Discounts
#   ./trigger_traffic.sh --module currency  # Exercise only FX Currency
#   ./trigger_traffic.sh --module billing   # Exercise only Billing Proration
#   ./trigger_traffic.sh --loop 5           # Run traffic loop 5 times (or --loop for infinite)
#   ./trigger_traffic.sh --target http://localhost:8080 # Target local instance
# ==============================================================================

set -euo pipefail

TARGET_URL="${NIGHTZERO_TARGET_URL:-https://demo-payment-gateway-164161200079.us-central1.run.app}"
MODULE="all"
LOOP_COUNT=1
DELAY_SEC=2

# Parse arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    -m|--module)
      MODULE="$2"
      shift 2
      ;;
    -t|--target|--url)
      TARGET_URL="$2"
      shift 2
      ;;
    -l|--loop|--repeat)
      if [[ $# -gt 1 && "$2" =~ ^[0-9]+$ ]]; then
        LOOP_COUNT="$2"
        shift 2
      else
        LOOP_COUNT=999999
        shift 1
      fi
      ;;
    -d|--delay)
      DELAY_SEC="$2"
      shift 2
      ;;
    -h|--help)
      echo "NightZero Test Traffic Trigger"
      echo "Usage: ./trigger_traffic.sh [--module all|pricing|discounts|currency|billing|tax] [--target <url>] [--loop <count>]"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

TARGET_URL="${TARGET_URL%/}"

echo "================================================================="
echo " 🎯 Target Gateway : ${TARGET_URL}"
echo " 📦 Module Scope   : ${MODULE}"
echo " 🔁 Iterations     : ${LOOP_COUNT}"
echo "================================================================="

call_endpoint() {
  local name="$1"
  local path="$2"
  local payload="$3"

  printf "  🔹 [%-18s] Calling %s ... " "${name}" "${path}"
  
  local response
  local http_code
  response=$(curl -s -w "\n%{http_code}" -X POST "${TARGET_URL}${path}" \
    -H "Content-Type: application/json" \
    -d "${payload}" --max-time 10 || echo -e '{"error":"connection failed"}\n000')

  http_code=$(echo "${response}" | tail -n1)
  local body
  body=$(echo "${response}" | sed '$d')

  if [[ "${http_code}" -ge 200 && "${http_code}" -lt 300 ]]; then
    echo -e "\033[32m✔ OK (${http_code})\033[0m -> ${body}"
  else
    echo -e "\033[31m✖ DISCREPANCY / ERROR (${http_code})\033[0m -> \033[33mCaptured by Cloud Logging!\033[0m"
    echo "     Response: ${body}"
  fi
}

iter=0
while [[ ${iter} -lt ${LOOP_COUNT} ]]; do
  iter=$((iter + 1))
  if [[ ${LOOP_COUNT} -gt 1 ]]; then
    echo ""
    echo "--- [Cycle ${iter}/${LOOP_COUNT}] $(date +%H:%M:%S) ---"
  fi

  if [[ "${MODULE}" == "all" || "${MODULE}" == "pricing" || "${MODULE}" == "checkout" ]]; then
    call_endpoint "Pricing" "/api/v1/checkout" '{"cents": 1234}'
  fi

  if [[ "${MODULE}" == "all" || "${MODULE}" == "discounts" || "${MODULE}" == "discount" ]]; then
    call_endpoint "Discounts" "/api/v1/discounts/apply" '{"cents": 1000, "discount_pct": 20.0}'
  fi

  if [[ "${MODULE}" == "all" || "${MODULE}" == "currency" || "${MODULE}" == "fx" ]]; then
    call_endpoint "Currency FX" "/api/v1/currency/convert" '{"cents": 1000, "fx_rate": 0.92}'
  fi

  if [[ "${MODULE}" == "all" || "${MODULE}" == "billing" || "${MODULE}" == "proration" ]]; then
    call_endpoint "Billing Prorate" "/api/v1/billing/prorate" '{"monthly_cents": 3000, "days_used": 15, "total_days": 30}'
  fi

  if [[ "${MODULE}" == "all" || "${MODULE}" == "tax" || "${MODULE}" == "taxes" ]]; then
    call_endpoint "Tax & Fees" "/api/v1/tax/calculate" '{"subtotal_cents": 10000, "tax_rate_bps": 825}'
  fi

  if [[ ${iter} -lt ${LOOP_COUNT} ]]; then
    sleep "${DELAY_SEC}"
  fi
done

echo ""
echo "✅ Traffic trigger run completed."
