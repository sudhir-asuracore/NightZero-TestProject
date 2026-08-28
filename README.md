# NightZero Test Project 🌌
### Microservice Target (`demo-payment-gateway`) for Chaos Injection & Autonomous Verification

[![Cloud Run Service](https://img.shields.io/badge/Google%20Cloud%20Run-demo--payment--gateway-4285F4?style=for-the-badge&logo=googlecloud)](https://demo-payment-gateway-164161200079.us-central1.run.app)
[![CI/CD](https://img.shields.io/badge/GitHub%20Actions-Automated%20Deploy-2088FF?style=for-the-badge&logo=githubactions)](https://github.com/sudhir-asuracore/NightZero-TestProject/actions)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg?style=for-the-badge)](LICENSE)

---

## 📌 Overview

**NightZero-TestProject** is a realistic financial microservice (`demo-payment-gateway`) deployed on Google Cloud Run. It is used as the live target application to demonstrate NightZero's autonomous detection, triage, root-cause forensics, sandbox verification, and pull request remediation.

---

## 📦 Financial Calculation Modules

The target microservice includes 5 financial business logic modules:
1. **`demo_target/pricing.py`**: Checkout formatting & integer precision pricing.
2. **`demo_target/discounts.py`**: Percentage-based discount deduction logic.
3. **`demo_target/currency.py`**: Foreign exchange (FX) currency conversion in cents.
4. **`demo_target/billing.py`**: Subscription cycle proration calculations.
5. **`demo_target/tax.py`**: Basis-points (bps) tax & fee computations.

---

## 🚦 Traffic & Chaos Outage CLI: `trigger_traffic.sh`

The project includes an automated traffic exercise and failure injection verification script:

```bash
# Exercise all target microservice endpoints
./trigger_traffic.sh

# Exercise specific module after injecting a chaos bug
./trigger_traffic.sh --module tax        # Tax & Fees calculation
./trigger_traffic.sh --module billing    # Billing Proration
./trigger_traffic.sh --module currency   # FX Currency Conversion
./trigger_traffic.sh --module discounts  # Discount Engine
./trigger_traffic.sh --module pricing    # Checkout Pricing

# Run multi-iteration or continuous loop
./trigger_traffic.sh --loop 5
```

---

## 🧪 Local Testing

```bash
# Run the complete unit test suite
python3 -m unittest discover -s demo_target -v
```

---

## 📜 License
Licensed under the [Apache License 2.0](LICENSE).
