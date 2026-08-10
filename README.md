# NightZero Test Project

This intentionally broken Python service is the safe target repository for the
NightZero remediation demo. It models a checkout-total regression: `format_total`
rounds `$12.34` down to `$12.00`.

It is intentionally independent of the Agent and Control Panel repositories.
NightZero clones it into a temporary sandbox before testing a candidate patch;
the checked-out `main` branch must not be changed by remediation runs.

## Test

```bash
python -m unittest demo_target.test_pricing
```

## Agent access

The default Agent target URL is:

```text
git@github.com:sudhir-asuracore/NightZero-TestProject.git
```

The Agent requires read access for the current sandbox-only MVP. A future
GitHub credential for branch and pull-request automation must be dedicated to
this repository and must not grant deployment access.