import json
import logging
import os
import sys
import threading
import time
import traceback
from datetime import datetime, timezone
from flask import Flask, jsonify, request

from demo_target.pricing import format_total
from demo_target.discounts import apply_discount
from demo_target.currency import convert_currency
from demo_target.billing import calculate_proration
from demo_target.tax import calculate_tax_and_fees

logging.basicConfig(level=logging.INFO, stream=sys.stdout, format='%(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)


def emit_error_log(service: str, event: str, message: str, exc: Exception | None = None, file_path: str = "") -> None:
    now_iso = datetime.now(timezone.utc).isoformat()
    tb_str = traceback.format_exc() if exc else f"Traceback (most recent call last):\n  File '{file_path}', in calculation\nAssertionError: {message}"
    payload = {
        "severity": "ERROR",
        "service": service,
        "event": event,
        "timestamp": now_iso,
        "message": message,
        "stacktrace": tb_str,
    }
    logger.error(json.dumps(payload))


def continuous_traffic_worker() -> None:
    """Continuously tests and simulates traffic across all 5 payment & financial services."""
    cycle = 0
    while True:
        time.sleep(5)
        cycle += 1
        
        # 1. Exercise Pricing / Format Total
        try:
            total = format_total(1234)
            if total != "$12.34":
                emit_error_log(
                    service="demo-payment-gateway",
                    event="pricing_calculation_failed",
                    message=f"Calculation Discrepancy in checkout/pricing: Expected $12.34, got {total} at demo_target/pricing.py:2 in format_total",
                    file_path="demo_target/pricing.py",
                )
        except Exception as exc:
            emit_error_log(
                service="demo-payment-gateway",
                event="pricing_exception",
                message=f"Unhandled exception in checkout/pricing format_total: {str(exc)}",
                exc=exc,
                file_path="demo_target/pricing.py",
            )

        # 2. Exercise Discounts
        try:
            discounted = apply_discount(1000, 20.0)
            if discounted != 800:
                emit_error_log(
                    service="demo-payment-gateway",
                    event="discount_calculation_failed",
                    message=f"Discount calculation mismatch: Expected 800 cents, got {discounted} cents at demo_target/discounts.py:5 in apply_discount",
                    file_path="demo_target/discounts.py",
                )
        except Exception as exc:
            emit_error_log(
                service="demo-payment-gateway",
                event="discount_exception",
                message=f"Unhandled exception in discount calculation: {str(exc)}",
                exc=exc,
                file_path="demo_target/discounts.py",
            )

        # 3. Exercise Currency FX Conversion
        try:
            eur_cents = convert_currency(1000, 0.92)
            if eur_cents != 920:
                emit_error_log(
                    service="demo-payment-gateway",
                    event="currency_conversion_failed",
                    message=f"FX conversion discrepancy: Expected 920 EUR cents, got {eur_cents} at demo_target/currency.py:4 in convert_currency",
                    file_path="demo_target/currency.py",
                )
        except Exception as exc:
            emit_error_log(
                service="demo-payment-gateway",
                event="currency_conversion_exception",
                message=f"Unhandled exception in FX conversion: {str(exc)}",
                exc=exc,
                file_path="demo_target/currency.py",
            )

        # 4. Exercise Billing Proration
        try:
            prorated = calculate_proration(3000, 15, 30)
            if prorated != 1500:
                emit_error_log(
                    service="demo-payment-gateway",
                    event="billing_proration_failed",
                    message=f"Billing proration mismatch: Expected 1500 cents for 15/30 days, got {prorated} at demo_target/billing.py:4 in calculate_proration",
                    file_path="demo_target/billing.py",
                )
        except Exception as exc:
            emit_error_log(
                service="demo-payment-gateway",
                event="billing_proration_exception",
                message=f"Unhandled exception in billing proration: {str(exc)}",
                exc=exc,
                file_path="demo_target/billing.py",
            )

        # 5. Exercise Tax & Fees
        try:
            tax = calculate_tax_and_fees(10000, 825)
            if tax != 825:
                emit_error_log(
                    service="demo-payment-gateway",
                    event="tax_calculation_failed",
                    message=f"Tax calculation discrepancy: Expected 825 cents (8.25%), got {tax} at demo_target/tax.py:4 in calculate_tax_and_fees",
                    file_path="demo_target/tax.py",
                )
        except Exception as exc:
            emit_error_log(
                service="demo-payment-gateway",
                event="tax_calculation_exception",
                message=f"Unhandled exception in tax calculation: {str(exc)}",
                exc=exc,
                file_path="demo_target/tax.py",
            )


# Start the background traffic worker daemon only if explicitly requested
if os.environ.get("ENABLE_BACKGROUND_TRAFFIC", "").lower() in ("true", "1", "yes"):
    threading.Thread(target=continuous_traffic_worker, daemon=True).start()


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "UP", "service": "demo-payment-gateway", "modules": ["pricing", "discounts", "currency", "billing", "tax"]}), 200


@app.route("/checkout", methods=["POST", "GET"])
@app.route("/api/v1/checkout", methods=["POST", "GET"])
def checkout():
    cents = 1234
    if request.is_json and request.json:
        cents = request.json.get("cents", 1234)
    try:
        total = format_total(cents)
        expected = f"${cents / 100:.2f}"
        if total != expected:
            emit_error_log(
                service="demo-payment-gateway",
                event="pricing_calculation_failed",
                message=f"Calculation Discrepancy in checkout/pricing: Expected {expected}, got {total} at demo_target/pricing.py:2 in format_total",
                file_path="demo_target/pricing.py",
            )
            return jsonify({"error": "Calculation discrepancy", "total": total, "expected": expected}), 500
        return jsonify({"status": "SUCCESS", "total": total})
    except Exception as exc:
        emit_error_log("demo-payment-gateway", "checkout_exception", str(exc), exc=exc, file_path="demo_target/pricing.py")
        return jsonify({"error": str(exc)}), 500


@app.route("/api/v1/discounts/apply", methods=["POST", "GET"])
def discount_apply():
    cents = 1000
    discount_pct = 20.0
    if request.is_json and request.json:
        cents = request.json.get("cents", 1000)
        discount_pct = float(request.json.get("discount_pct", 20.0))
    try:
        result = apply_discount(cents, discount_pct)
        expected = max(0, cents - int(round(cents * (discount_pct / 100.0))))
        if result != expected:
            emit_error_log(
                service="demo-payment-gateway",
                event="discount_calculation_failed",
                message=f"Discount calculation mismatch: Expected {expected} cents, got {result} cents at demo_target/discounts.py:5 in apply_discount",
                file_path="demo_target/discounts.py",
            )
            return jsonify({"error": "Discount calculation mismatch", "cents": result, "expected": expected}), 500
        return jsonify({"status": "SUCCESS", "cents": result})
    except Exception as exc:
        emit_error_log("demo-payment-gateway", "discount_exception", str(exc), exc=exc, file_path="demo_target/discounts.py")
        return jsonify({"error": str(exc)}), 500


@app.route("/api/v1/currency/convert", methods=["POST", "GET"])
def currency_convert():
    cents = 1000
    fx_rate = 0.92
    if request.is_json and request.json:
        cents = request.json.get("cents", 1000)
        fx_rate = float(request.json.get("fx_rate", 0.92))
    try:
        result = convert_currency(cents, fx_rate)
        expected = int(round(cents * fx_rate))
        if result != expected:
            emit_error_log(
                service="demo-payment-gateway",
                event="currency_conversion_failed",
                message=f"FX conversion discrepancy: Expected {expected} EUR cents, got {result} at demo_target/currency.py:4 in convert_currency",
                file_path="demo_target/currency.py",
            )
            return jsonify({"error": "FX conversion discrepancy", "cents": result, "expected": expected}), 500
        return jsonify({"status": "SUCCESS", "cents": result})
    except Exception as exc:
        emit_error_log("demo-payment-gateway", "currency_exception", str(exc), exc=exc, file_path="demo_target/currency.py")
        return jsonify({"error": str(exc)}), 500


@app.route("/api/v1/billing/prorate", methods=["POST", "GET"])
def billing_prorate():
    monthly_cents = 3000
    days_used = 15
    total_days = 30
    if request.is_json and request.json:
        monthly_cents = request.json.get("monthly_cents", 3000)
        days_used = request.json.get("days_used", 15)
        total_days = request.json.get("total_days", 30)
    try:
        result = calculate_proration(monthly_cents, days_used, total_days)
        expected = int(round((monthly_cents * days_used) / float(total_days)))
        if result != expected:
            emit_error_log(
                service="demo-payment-gateway",
                event="billing_proration_failed",
                message=f"Billing proration mismatch: Expected {expected} cents for {days_used}/{total_days} days, got {result} at demo_target/billing.py:4 in calculate_proration",
                file_path="demo_target/billing.py",
            )
            return jsonify({"error": "Billing proration mismatch", "prorated_cents": result, "expected": expected}), 500
        return jsonify({"status": "SUCCESS", "prorated_cents": result})
    except Exception as exc:
        emit_error_log("demo-payment-gateway", "billing_exception", str(exc), exc=exc, file_path="demo_target/billing.py")
        return jsonify({"error": str(exc)}), 500


@app.route("/api/v1/tax/calculate", methods=["POST", "GET"])
def tax_calculate():
    subtotal_cents = 10000
    tax_rate_bps = 825
    if request.is_json and request.json:
        subtotal_cents = request.json.get("subtotal_cents", 10000)
        tax_rate_bps = request.json.get("tax_rate_bps", 825)
    try:
        result = calculate_tax_and_fees(subtotal_cents, tax_rate_bps)
        expected = int(round(subtotal_cents * (tax_rate_bps / 10000.0)))
        if result != expected:
            emit_error_log(
                service="demo-payment-gateway",
                event="tax_calculation_failed",
                message=f"Tax calculation discrepancy: Expected {expected} cents ({tax_rate_bps / 100.0:.2f}%), got {result} at demo_target/tax.py:4 in calculate_tax_and_fees",
                file_path="demo_target/tax.py",
            )
            return jsonify({"error": "Tax calculation discrepancy", "tax_cents": result, "expected": expected}), 500
        return jsonify({"status": "SUCCESS", "tax_cents": result})
    except Exception as exc:
        emit_error_log("demo-payment-gateway", "tax_exception", str(exc), exc=exc, file_path="demo_target/tax.py")
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
