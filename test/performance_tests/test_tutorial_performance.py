"""
Performance tests — measure wall-clock execution time of tutorial scripts.

Each test runs a tutorial script as a subprocess (same mechanism as the
functional tests) and fails if elapsed time exceeds the configured threshold.

Thresholds
----------
Constants are defined per complexity tier below.  Every value is marked TBD
until the team sets a project-specific budget.  Any threshold can be
overridden at runtime by setting the corresponding environment variable:

  CORTO_PERF_LIGHTWEIGHT_S   (default: TBD — placeholder 60 s)
  CORTO_PERF_FAST_RENDER_S   (default: TBD — placeholder 120 s)
  CORTO_PERF_FULL_RENDER_S   (default: TBD — placeholder 300 s)
  CORTO_PERF_COMPLEX_S       (default: TBD — placeholder 600 s)

Usage
-----
Run only performance tests:
    pytest test/performance_tests/ -v

Skip during regular CI:
    pytest --ignore=test/performance_tests/

Override a threshold on the fly:
    CORTO_PERF_FAST_RENDER_S=90 pytest test/performance_tests/ -v
"""
from __future__ import annotations

import os
import sys
import time

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
import cortopy as corto


# ---------------------------------------------------------------------------
# Thresholds  (TBD — replace placeholder values with measured budgets)
# ---------------------------------------------------------------------------

def _threshold(env_var: str, tbd_default: float) -> float:
    """Return the threshold in seconds, preferring an env-var override."""
    raw = os.environ.get(env_var)
    if raw is not None:
        return float(raw)
    return tbd_default


# NOTE: base performance assessed on a MacBook Air 
# No Blender render — data generation / visualisation scripts
THRESHOLD_LIGHTWEIGHT_S = _threshold("CORTO_PERF_LIGHTWEIGHT_S", 5.0)   # TBD
# EEVEE render, single body
THRESHOLD_FAST_RENDER_S = _threshold("CORTO_PERF_FAST_RENDER_S", 35.0)  # TBD
# CYCLES render, single body
THRESHOLD_FULL_RENDER_S = _threshold("CORTO_PERF_FULL_RENDER_S", 65.0)  # TBD
# Multi-body or multi-sensor CYCLES render
THRESHOLD_COMPLEX_S = _threshold("CORTO_PERF_COMPLEX_S", 600.0)          # TBD


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def run_timed(script_path: str, threshold_s: float) -> None:
    """
    Run a tutorial script and assert it completes within *threshold_s* seconds.
    On failure the assertion message reports both elapsed and allowed time.
    """
    t0 = time.perf_counter()
    corto.Utils.run_script(script_path)
    elapsed = time.perf_counter() - t0

    assert elapsed <= threshold_s, (
        f"\nPerformance budget exceeded for: {script_path}"
        f"\n  elapsed : {elapsed:.1f} s"
        f"\n  allowed : {threshold_s:.1f} s"
        f"\n  overage : {elapsed - threshold_s:.1f} s"
    )


# ---------------------------------------------------------------------------
# Tier 1 — Lightweight (no Blender render)
# ---------------------------------------------------------------------------


def test_perf_basics_generate_cloud_input():
    """Cloud input generation — no rendering, expected to be fast."""
    run_timed("tutorials/basics_GenerateCloud_input.py", THRESHOLD_LIGHTWEIGHT_S)

# ---------------------------------------------------------------------------
# Tier 2 — Fast render (EEVEE, single body)
# ---------------------------------------------------------------------------

def test_perf_S01b_Eros_eevee():
    """S01b — Eros single body, EEVEE rasteriser."""
    run_timed("tutorials/S01b_Eros.py", THRESHOLD_FAST_RENDER_S)


def test_perf_S05a_Didymos_Milani():
    """S05a — Didymos/Milani binary system, fast render path."""
    run_timed("tutorials/S05a_Didymos_Milani.py", THRESHOLD_FAST_RENDER_S)


# ---------------------------------------------------------------------------
# Tier 3 — Full render (CYCLES, single or multi-body)
# ---------------------------------------------------------------------------

def test_perf_S02_Itokawa():
    """S02 — Itokawa, CYCLES render."""
    run_timed("tutorials/S02_Itokawa.py", THRESHOLD_FULL_RENDER_S)


def test_perf_S07a_Mars_Phobos_Deimos():
    """S07a — Three-body scene (Mars + Phobos + Deimos), CYCLES."""
    run_timed("tutorials/S07a_Mars_Phobos_Deimos.py", THRESHOLD_FULL_RENDER_S)

def test_perf_S10_Spacecraft():
    """S10 — Spacecraft with LiDAR + ToF + StructuredLight sensors."""
    run_timed("tutorials/S10_Spacecraft.py", THRESHOLD_FULL_RENDER_S)


# ---------------------------------------------------------------------------
# Tier 4 — Complex (multi-body or multi-sensor)
# ---------------------------------------------------------------------------

def test_perf_S04_Bennu():
    """S04 — Bennu, CYCLES render."""
    run_timed("tutorials/S04_Bennu.py", THRESHOLD_COMPLEX_S)

def test_perf_S08_Earth():
    """S08 — Earth, CYCLES render."""
    run_timed("tutorials/S08_Earth.py", THRESHOLD_COMPLEX_S)
