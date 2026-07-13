# Compatibility Test Corpus

Golden-input → expected-output fixtures, one folder per rule. This is the
**regression suite for the Compatibility Layer itself**: the compiler must turn
each `golden.*` (19.0) into the matching `expected-<series>.*`.

```
corpus/
  orm/    R-ORM-002/   golden.py   expected-17.py
  views/  R-VIEW-001/  golden.xml  expected-17.xml
          R-VIEW-002/  golden.xml  expected-17.xml
```

## Conventions
- `golden.*` is the 19.0 canonical form (also valid for 18.0 unless noted).
- `expected-<series>.*` is the required layer output for that series. Absence of
  a file means "identical to golden" (no transform for that series).
- A rule graduates to `Stable` only when the compiler reproduces every
  `expected-*` byte-for-byte **and** the produced module passes Docker tests.

## Intended runner (future)
```
for rule in corpus/**:
    for series in [18,17,16,15,14]:
        assert layer.compile(rule/golden, target=series) == rule/expected-series
```

When a boundary is identity (e.g. R-ORM-002 for 18.0), no `expected-18` file is
present and the runner asserts output == golden.
