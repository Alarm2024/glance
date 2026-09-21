# glance-status (Python)

Python port of the Glance `glance-status` crate: doctor classification, redaction, and anti-overclaim checks.

**Status:** pre-1.0 · not yet on [PyPI](https://pypi.org/project/glance-status/).

## Install

Editable from this repository:

```bash
pip install -e lib/python
```

After publish (not live yet):

```bash
pip install glance-status
```

## Usage

```python
from glance_status import ClassifyInput, DoctorStatus, assert_no_overclaim, classify, redact

status = classify(
    ClassifyInput(
        blocking_flag=False,
        raw_message="Feed stale for 47s",
        hygiene_phrases=["hygiene"],
        fault_phrases=["stale"],
    )
)
assert status == DoctorStatus.WARN

safe = redact("see https://example.com/x?token=secret")
assert_no_overclaim(safe, ["guaranteed"])
```

## Guide

See [Add Glance in 15 minutes](https://github.com/Alarm2024/glance/blob/main/docs/add-glance-in-15-minutes.md).

## License

MIT
