# mistralai/mistral-nemo — §7.3 pre-publication review

2026-09-06T04:25:55.344035+00:00

---

The `DEVIATION_LOG.md` file contains the following entries:

* D1: serial collection of the first 358 rows; latency excluded
* D2: scorer failed its own controls on first contact; 6 defects fixed before scoring
* D3: definition of tsp/tbt/cup identities changed; family-1 EXACT rate 76.7% → 80.2%
* D4: added the `sens` column
* D5: families 8–11 built from the frozen §4.2 text; 2 scorer rules adjusted on a 16-control pilot
* D6: kimi-k2 token cap (90,000) on families 8–11
* D7: 1,004 duplicate keys on families 8–11 deduplicated keep-earliest
* D8: H3 accuracy = EXACT ∪ OVER_BENIGN, EXACT beside
