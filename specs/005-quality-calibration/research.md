# Research: Quality & Calibration

**Feature**: Quality & Calibration (Phase 4)
**Date**: 2026-01-27
**Status**: Complete

## Overview

This document captures research findings and design decisions for implementing quality metrics, bias detection, variance monitoring, character drift detection, and calibration pipelines for synthetic user research.

---

## 1. Consistency Scoring Algorithm

### Decision

Extend existing trait-keyword matching with weighted scoring and Schwartz value integration.

### Rationale

The Phase 1 QualityMetricsCalculator uses simple keyword presence detection. Phase 4 requires:
- Per-response breakdown (not just session-level)
- Schwartz value alignment (not just Big Five)
- Weighted scoring based on trait extremity

### Approach

**Scoring Formula:**
```
consistency_score = (
    big_five_alignment * 0.6 +
    schwartz_alignment * 0.4
)

big_five_alignment = Σ(trait_match_score × trait_weight) / Σ(trait_weight)
- trait_weight = |trait_value - 5| / 5  (extremity: 0.0 for neutral, 1.0 for extreme)
- trait_match_score = keywords_found / expected_keywords

schwartz_alignment = priority_values_reflected / priority_values_defined
```

**Per-Response Analysis:**
- Window each response independently
- Track cumulative scores across session
- Flag responses that deviate >25% from session mean

### Alternatives Considered

| Alternative | Why Rejected |
|-------------|--------------|
| ML-based semantic similarity | Requires additional dependencies (sentence-transformers); overkill for v1 |
| LLM-as-judge evaluation | Adds latency and cost per response; better for spot-checking |
| Simple keyword counting | Insufficient for Schwartz values which have abstract concepts |

---

## 2. Sycophancy Detection

### Decision

Multi-signal detection combining phrase patterns, sentiment ratios, and reasoning analysis.

### Rationale

Single-signal detection (e.g., just phrase counting) produces false positives. Sycophancy manifests through:
1. Excessive positive phrases ("This is amazing", "I love it")
2. Absence of expected criticism from skeptical personas
3. Identical sentiment across diverse panel members
4. Agreement without substantive reasoning

### Approach

**Detection Signals:**

| Signal | Weight | Threshold |
|--------|--------|-----------|
| Positive phrase count | 0.25 | >3 in single response |
| Positive:negative ratio | 0.25 | >4:1 |
| Missing criticism (skeptical personas) | 0.30 | 0 concerns when expected |
| Sentiment clustering (panel) | 0.20 | >80% same sentiment |

**Sycophancy Rate Formula:**
```
sycophancy_rate = (flagged_responses / total_responses) × 100%
```

**Phrase Detection (Extended from Phase 1):**
```python
SYCOPHANCY_PHRASES = [
    # Existing Phase 1
    "I absolutely love", "This is amazing", "What a great idea",
    # Extended for Phase 4
    "This is exactly what I need", "I can't find any issues",
    "This is perfect", "I would definitely recommend",
    "No concerns at all", "I'm completely satisfied",
    "This exceeds expectations", "I have no complaints"
]
```

### Alternatives Considered

| Alternative | Why Rejected |
|-------------|--------------|
| Sentiment-only analysis | Legitimate positive feedback would be flagged |
| LLM classification | Added latency; phrase matching is sufficient for known patterns |
| User feedback loop | Requires manual review; not scalable for automated gates |

---

## 3. Variance Monitoring

### Decision

Use standard statistical measures with domain-specific baseline comparisons.

### Rationale

Variance monitoring ensures panel diversity. Key metrics:
- Rating distribution spread (quantitative)
- Sentiment diversity (qualitative)
- Theme coverage (qualitative)

### Approach

**Quantitative Variance (Ratings):**
```python
from statistics import mean, stdev, variance

# Calculate panel variance
rating_stdev = stdev(panel_ratings)
rating_variance = variance(panel_ratings)

# Expected human variance baselines
EXPECTED_VARIANCE = {
    "rating_1_10": 2.5,      # Expected stdev for 1-10 scales
    "rating_1_5": 1.2,       # Expected stdev for 1-5 scales
    "nps_0_10": 2.8          # Expected stdev for NPS
}

# Flag if synthetic variance < 60% of expected
variance_ratio = rating_stdev / EXPECTED_VARIANCE[scale_type]
clustering_detected = variance_ratio < 0.6
```

**Qualitative Variance (Sentiment):**
```python
sentiment_distribution = {
    "positive": count_positive / total,
    "negative": count_negative / total,
    "mixed": count_mixed / total,
    "neutral": count_neutral / total
}

# Flag if any single sentiment > 80% (except legitimate consensus)
clustering_detected = any(pct > 0.8 for pct in sentiment_distribution.values())
```

**Variance Stability:**
- Track variance across multiple sessions with same panel
- Flag if relative difference > 20%

### Alternatives Considered

| Alternative | Why Rejected |
|-------------|--------------|
| Entropy-based diversity | Harder to interpret; stdev is more intuitive |
| Clustering algorithms (k-means) | Overkill for 5-10 persona panels |
| Custom variance formulas | Standard statistics are well-understood and verifiable |

---

## 4. Character Drift Detection

### Decision

Window-based trait alignment comparison across session segments.

### Rationale

Character drift occurs when a persona's responses deviate from their defined traits over time. This is critical for:
- Long interview sessions (20+ exchanges)
- Focus group discussions (multi-turn)
- Extended survey sessions

### Approach

**Segmentation Strategy:**
```python
def segment_session(responses: list, segments: int = 3):
    """Divide session into segments for drift analysis."""
    segment_size = len(responses) // segments
    return [
        responses[i*segment_size:(i+1)*segment_size]
        for i in range(segments)
    ]
```

**Drift Score Formula:**
```
drift_score = |consistency_first_segment - consistency_last_segment|

# Thresholds
drift_warning = drift_score > 15%   # Yellow flag
drift_critical = drift_score > 25%  # Red flag
```

**Drift Point Detection:**
```python
def find_drift_point(segment_scores: list) -> int:
    """Find index where drift began."""
    max_delta = 0
    drift_point = 0
    for i in range(1, len(segment_scores)):
        delta = abs(segment_scores[i] - segment_scores[i-1])
        if delta > max_delta:
            max_delta = delta
            drift_point = i
    return drift_point
```

**Per-Trait Tracking:**
- Track each Big Five trait independently
- Report which traits drifted most
- Highlight specific trait-response mismatches

### Alternatives Considered

| Alternative | Why Rejected |
|-------------|--------------|
| Rolling window analysis | More complex; fixed segments sufficient for v1 |
| Per-response drift | Too noisy; segment aggregation smooths variance |
| Embedding-based similarity | Requires additional dependencies |

---

## 5. Calibration Pipeline Architecture

### Decision

Import-compare-recommend pipeline with YAML/CSV baseline storage.

### Rationale

Calibration validates synthetic research against real user data. The pipeline must:
1. Import real user baselines (anonymized)
2. Compare synthetic distributions
3. Generate actionable recommendations

### Approach

**Baseline Import Format (CSV):**
```csv
question_id,response_type,response_value,demographic_tag
q1,rating,7,early_adopter
q1,rating,5,late_majority
q2,multiple_choice,A,early_adopter
```

**Baseline Storage (YAML):**
```yaml
baseline:
  id: feature-feedback-2026q1
  source: "Real User Survey - Jan 2026"
  sample_size: 150
  collection_date: 2026-01-15
  demographic_tags: [early_adopter, late_majority, privacy_conscious]

distributions:
  q1_rating:
    type: numeric
    mean: 6.2
    stdev: 2.3
    histogram: [0, 5, 12, 25, 35, 40, 20, 8, 3, 2]  # buckets 1-10
  q2_choice:
    type: categorical
    frequencies:
      A: 0.45
      B: 0.30
      C: 0.20
      D: 0.05
```

**Comparison Algorithm:**
```python
def calculate_distribution_overlap(synthetic: dict, baseline: dict) -> float:
    """Calculate overlap between synthetic and real distributions."""
    if baseline["type"] == "numeric":
        # Use histogram intersection
        overlap = sum(min(s, b) for s, b in zip(
            synthetic["histogram"], baseline["histogram"]
        )) / sum(baseline["histogram"])
    else:
        # Use frequency overlap for categorical
        overlap = sum(
            min(synthetic["frequencies"].get(k, 0), v)
            for k, v in baseline["frequencies"].items()
        )
    return overlap * 100  # Percentage
```

**Recommendation Generation:**
```python
def generate_recommendations(comparison: dict) -> list[str]:
    """Generate persona adjustment recommendations."""
    recommendations = []
    for question_id, result in comparison.items():
        if result["overlap"] < 60:
            if result["synthetic_mean"] > result["baseline_mean"]:
                recommendations.append(
                    f"{question_id}: Synthetic responses skew positive. "
                    f"Consider increasing criticism_tendency for relevant personas."
                )
            # ... additional patterns
    return recommendations
```

### Alternatives Considered

| Alternative | Why Rejected |
|-------------|--------------|
| Database storage | Overkill; YAML files consistent with existing patterns |
| Real-time calibration | Out of scope; batch comparison sufficient for v1 |
| ML-based distribution matching | Standard statistical methods are interpretable |

---

## 6. Quality Dashboard Design

### Decision

CLI-based dashboard using Rich library with drill-down capability.

### Rationale

Consistent with existing CLI patterns (no web UI until Phase 5). Dashboard must:
- Show aggregated metrics at a glance
- Highlight sessions with warnings
- Support filtering by quality status
- Enable drill-down to individual sessions

### Approach

**Dashboard Layout:**
```
╭─────────────────────── Quality Dashboard ───────────────────────╮
│                                                                  │
│  Overall Health: ⚠️ Warning (2 sessions need review)             │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ Metric              │ Current │ Threshold │ Status          │ │
│  ├─────────────────────┼─────────┼───────────┼─────────────────┤ │
│  │ Avg Consistency     │ 78%     │ 70%       │ ✅ Healthy      │ │
│  │ Sycophancy Rate     │ 35%     │ 30%       │ ⚠️ Warning      │ │
│  │ Variance Score      │ 0.72    │ 0.60      │ ✅ Healthy      │ │
│  │ Max Drift           │ 18%     │ 25%       │ ✅ Healthy      │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  Recent Sessions:                                                │
│  • session-abc123 [Panel: tech-adopters] ✅ Healthy             │
│  • session-def456 [Panel: skeptics] ⚠️ Sycophancy Warning       │
│  • session-ghi789 [Interview] ✅ Healthy                        │
│                                                                  │
╰──────────────────────────────────────────────────────────────────╯
```

**Implementation with Rich:**
```python
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

def render_dashboard(metrics: QualityDashboardMetrics):
    console = Console()

    # Status table
    table = Table(title="Quality Metrics")
    table.add_column("Metric")
    table.add_column("Current")
    table.add_column("Threshold")
    table.add_column("Status")

    # ... populate table

    console.print(Panel(table, title="Quality Dashboard"))
```

### Alternatives Considered

| Alternative | Why Rejected |
|-------------|--------------|
| Web dashboard | Out of scope until Phase 5 |
| JSON-only output | Less user-friendly for interactive use |
| External visualization | Adds dependencies; Rich is sufficient |

---

## 7. Integration with Existing Systems

### Decision

Extend existing services rather than replace; maintain backward compatibility.

### Rationale

Phase 4 builds on Phase 1-3 foundations:
- Extend QualityMetrics model (not replace)
- Reuse SessionResponse structure
- Integrate with existing PanelExecutor output

### Approach

**Model Extension:**
```python
# Existing Phase 1 model (unchanged)
class QualityMetrics(BaseModel):
    consistency_score: float
    sycophancy_indicators: dict
    warnings: list[str]
    passed_gates: bool
    matched_traits: list[str]
    missing_traits: list[str]

# New Phase 4 extended model
class ExtendedQualityMetrics(QualityMetrics):
    """Extended quality metrics with Phase 4 capabilities."""
    schwartz_alignment: float
    per_response_scores: list[float]
    bias_analysis: BiasAnalysis
    variance_report: Optional[VarianceReport]  # Panel sessions only
    drift_analysis: Optional[DriftAnalysis]    # Multi-turn sessions only
```

**Service Composition:**
```python
class QualityAnalyzer:
    """Orchestrates all quality services."""

    def __init__(self):
        self.consistency_checker = ConsistencyChecker()
        self.bias_detector = BiasDetector()
        self.variance_monitor = VarianceMonitor()
        self.drift_detector = DriftDetector()

    def analyze_session(self, session: ResearchSession) -> ExtendedQualityMetrics:
        """Run full quality analysis on a session."""
        return ExtendedQualityMetrics(
            # Phase 1 metrics
            consistency_score=self.consistency_checker.calculate(session),
            sycophancy_indicators=self.bias_detector.detect_sycophancy(session),
            # Phase 4 extensions
            schwartz_alignment=self.consistency_checker.schwartz_score(session),
            bias_analysis=self.bias_detector.full_analysis(session),
            drift_analysis=self.drift_detector.analyze(session) if session.is_multi_turn else None,
        )
```

---

## 8. Testing Strategy

### Decision

Test-first approach with comprehensive fixtures and property-based testing for statistical functions.

### Rationale

Quality metrics are numerical and require precise validation:
- Unit tests for each service
- Property tests for statistical invariants
- Integration tests for full workflow
- Contract tests for CLI interface

### Approach

**Test Categories:**

| Category | Coverage | Focus |
|----------|----------|-------|
| Unit | Each service method | Input/output validation |
| Property | Statistical functions | Invariants (e.g., 0 ≤ score ≤ 100) |
| Integration | End-to-end workflow | Service composition |
| Contract | CLI commands | Interface stability |

**Sample Property Test:**
```python
from hypothesis import given, strategies as st

@given(st.lists(st.floats(min_value=1, max_value=10), min_size=3))
def test_variance_always_non_negative(ratings):
    """Variance must always be >= 0."""
    result = variance_monitor.calculate(ratings)
    assert result.variance >= 0
```

**Fixture Strategy:**
```python
@pytest.fixture
def high_consistency_session():
    """Session with responses perfectly matching persona traits."""
    ...

@pytest.fixture
def sycophantic_session():
    """Session with obvious sycophantic patterns."""
    ...

@pytest.fixture
def drifted_session():
    """Session showing clear character drift."""
    ...
```

---

## Summary of Key Decisions

| Topic | Decision | Key Rationale |
|-------|----------|---------------|
| Consistency Algorithm | Weighted Big Five + Schwartz | Matches persona schema; extensible |
| Sycophancy Detection | Multi-signal (phrases, ratios, clustering) | Reduces false positives |
| Variance Monitoring | Standard statistics with baselines | Interpretable; no new dependencies |
| Drift Detection | Window-based segment comparison | Efficient for variable-length sessions |
| Calibration Pipeline | YAML storage with histogram comparison | Consistent with existing patterns |
| Dashboard | CLI with Rich library | Matches existing UI patterns |
| Integration | Extension over replacement | Backward compatibility |
| Testing | Property-based + comprehensive fixtures | Statistical correctness |

---

**Research Status**: Complete
**Ready for**: Phase 1 Design (data-model.md, contracts/)
