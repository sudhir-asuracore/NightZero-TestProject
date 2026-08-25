import json
import logging
import os
import sys
import threading
import time
from datetime import datetime, timezone
from flask import Flask, jsonify, request
from demo_target.pricing import format_total

# Configure structured JSON logging for GCP Cloud Logging
logging.basicConfig(level=logging.INFO, stream=sys.stdout, format='%(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)


def continuous_traffic_worker() -> None:
    """Continuously processes dummy orders in the background every 5 seconds."""
    order_id = 1000
    while True:
        time.sleep(5)
        order_id += 1
        cents = 1234
        try:
            total = format_total(cents)
            if total == "$12.00":
                # The code regression is active! Emit structured GCP ERROR log
                error_payload = {
                    "severity": "ERROR",
                    "service": "demo-payment-gateway",
                    "event": "transaction_failed",
                    "order_id": order_id,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "message": "TypeError in checkout/pricing calculation: Expected $12.34, got $12.00 at demo_target/pricing.py:2 in format_total",
                    "stacktrace": "Traceback (most recent call last):\n  File 'demo_target/pricing.py', line 3, in format_total\n    return f'${cents // 100}.00'\nAssertionError: '$12.34' != '$12.00' (Precision lost: Decimal cents truncated)",
                }
                logger.error(json.dumps(error_payload))
            else:
                logger.info(
                    json.dumps({
                        "severity": "INFO",
                        "service": "demo-payment-gateway",
                        "event": "transaction_completed",
                        "order_id": order_id,
                        "total": total,
                        "status": "HEALTHY",
                    })
                )
        except Exception as exc:
            logger.error(
                json.dumps({
                    "severity": "ERROR",
                    "service": "demo-payment-gateway",
                    "message": f"Unhandled exception in checkout processing: {str(exc)}",
                })
            )


# Start the background traffic worker daemon
threading.Thread(target=continuous_traffic_worker, daemon=True).start()


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "UP", "service": "demo-payment-gateway"}), 200


@app.route("/checkout", methods=["POST", "GET"])
def checkout():
    cents = 1234
    if request.is_json and request.json:
        cents = request.json.get("cents", 1234)
    try:
        total = format_total(cents)
        if total == "$12.00":
            error_payload = {
                "severity": "ERROR",
                "service": "demo-payment-gateway",
                "message": "TypeError in checkout/pricing calculation: Expected $12.34, got $12.00 at demo_target/pricing.py:2 in format_total",
                "stacktrace": "Traceback (most recent call last):\n  File 'demo_target/pricing.py', line 3, in format_total\n    return f'${cents // 100}.00'\nAssertionError: '$12.34' != '$12.00'",
            }
            logger.error(json.dumps(error_payload))
            return jsonify({"error": "Calculation error", "total": total}), 500
        return jsonify({"status": "SUCCESS", "total": total})
    except Exception as exc:
        logger.error(
            json.dumps({
                "severity": "ERROR",
                "service": "demo-payment-gateway",
                "message": str(exc),
            })
        )
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
