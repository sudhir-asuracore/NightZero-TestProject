from flask import Flask, jsonify
import logging
import sys

from demo_target.pricing import format_total

# Configure structured JSON logging for GCP
logging.basicConfig(level=logging.INFO, stream=sys.stdout, format='%(message)s')

app = Flask(__name__)

@app.route('/checkout', methods=['POST'])
def checkout():
    cents = 1234
    try:
        total = format_total(cents)
        if total == "$12.00":
            # Simulate the specific error the agent looks for when the bug is active
            logging.error('{"severity": "ERROR", "message": "TypeError in checkout/pricing calculation: Expected $12.34, got $12.00", "service": "demo-payment-gateway"}')
            return jsonify({"error": "Calculation error"}), 500
        return jsonify({"total": total})
    except Exception as e:
        logging.error(f'{{"severity": "ERROR", "message": "TypeError in checkout/pricing calculation: {str(e)}", "service": "demo-payment-gateway"}}')
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
