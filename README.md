# NightZero Test Project

This intentionally broken Python service is the safe target repository for the
NightZero remediation demo. It models a checkout-total regression: `format_total`
rounds `$12.34` down to `$12.00`.

## Test

```bash
python -m unittest demo_target.test_pricing
```

NightZero must copy or clone this repository into an isolated sandbox before
creating a candidate patch. Do not apply generated patches directly to `main`.