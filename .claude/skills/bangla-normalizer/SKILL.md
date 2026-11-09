---
name: bangla-normalizer
description: Add or fix Bangla text normalization rules for TTS (numbers, dates, times, currency, units, abbreviations, Latin-script words, digits, punctuation) or pronunciation lexicon entries in bdub.text.bn. Use when a dub mispronounces something, when adding a new normalization case, or when touching Bangla string handling.
---

# Bangla text normalization

The normalizer turns translated Bangla text into text the TTS voice can speak (`bn` → `bn_spoken`). It lives in `src/bdub/text/bn/` and is **pure Python with no Qt import**. SPEC §10.1–10.2 is the source of truth.

Reference: [bangla-numbers.md](../../references/bangla-numbers.md) has the 0–100 table, scales (লাখ/কোটি), ordinals, time-of-day words, dates, currency, and units. Entries marked (verify) need linguist confirmation before becoming test oracles.

## Rules

- NFC-normalize input first (`unicodedata.normalize("NFC", s)`). Preserve ZWJ (U+200D) and ZWNJ (U+200C). Never strip them (e.g. র‍্য depends on ZWJ).
- Never slice or index Bangla text by code point. Use grapheme clusters: `regex.findall(r"\X", s)`.
- Accept Bengali (০–৯), Latin (0–9), and Eastern Arabic (٠–٩) digits everywhere a number is expected.
- Output is plain Bangla words with prosody punctuation (`।`, `,`, `?`), with no digits and no Latin letters left, unless a lexicon entry says otherwise.
- Use the **colloquial Bangladesh** wording by default (e.g. "দুইশো", "সাড়ে বারোটা"). Register-specific variants go through the register setting (SPEC §10.4), not hard-coded.
- Names are transliterated, never translated. Glossary entries override everything.
- Rules are ordered and documented. Each rule is a small function with a docstring showing one input → output example.

## Steps to add or fix a case

1. **Reproduce** with a failing test first, in `tests/unit/text/bn/test_<category>.py`:
   ```python
   @pytest.mark.parametrize("src, expected", [
       ("১,২৫০ টাকা", "এক হাজার দুইশো পঞ্চাশ টাকা"),
       ("1,250 Tk", "এক হাজার দুইশো পঞ্চাশ টাকা"),
   ])
   def test_currency(src, expected):
       assert normalize(src) == expected
   ```
   Cover the same value in all three digit systems when digits are involved.
2. **Decide where the fix belongs:**
   - A one-off word or name pronunciation → add a line to the lexicon (`resources/lexicon/lexicon.bn.tsv`, format `written<TAB>spoken<TAB>note`), not a rule.
   - A pattern (all percentages, all times) → a rule in the matching module (`numbers.py`, `datetime.py`, `currency.py`, `units.py`, `abbrev.py`, `latin.py`, `punct.py`).
3. **Implement** the smallest change. Keep rule order explicit in `pipeline.py`. A new rule must not change existing test outputs. Run the full normalizer suite.
4. **Property tests** (hypothesis) must still pass:
   - idempotent: `normalize(normalize(x)) == normalize(x)`
   - no ASCII digits or Bengali digits in output
   - output is NFC and ZWJ/ZWNJ counts in untouched words are preserved
   - never raises on arbitrary Unicode input
5. **Ask for review on wording.** If you're unsure which spoken form is natural in everyday Bangladeshi Bangla, add `# TODO(linguist): confirm` next to the test case rather than guessing silently, and mention it in your summary.
6. Run `uv run pytest tests/unit/text -q` and `uv run mypy src/bdub/text`.

## Reference examples (from SPEC §10.1)

| Input | Spoken |
|---|---|
| `1,250` | এক হাজার দুইশো পঞ্চাশ |
| `3rd` | তৃতীয় |
| `25%` | পঁচিশ শতাংশ |
| `12:30 PM` | দুপুর সাড়ে বারোটা (or digital style per setting) |

The target is ≥ 1,000 test cases overall (SPEC §15.1). Grow the suite with every fix.
