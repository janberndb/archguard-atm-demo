# ArchGuard ATM Demo

Demonstriert 4+1-Architekturprüfung.

* `architecture.yaml` — Logical & Development View
* `analyzer.py`       — Python-AST-Analyse → JUnit + HTML
* `GOOD/` · `BAD/`    — Zwei Codevarianten

## Bamboo
1. Plan GOOD → Checkout GOOD, run `python analyzer.py`
2. Plan BAD  → Checkout BAD,  run `python analyzer.py`
3. Test results: `tests-results/*.xml`
4. Artifact: `archguard_report.html`
