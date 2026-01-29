"""CalibrationPipeline service for importing, comparing, and calibrating baselines.

Handles CSV/JSON import of real user data, YAML persistence of baselines,
overlap calculation between synthetic and real distributions, and
generation of persona adjustment recommendations.
"""

import csv
import json
import uuid
from collections import defaultdict
from datetime import date
from pathlib import Path
from statistics import mean, stdev
from typing import Optional

import yaml

from models.calibration import (
    CalibrationBaseline,
    CalibrationComparison,
    CategoricalDistribution,
    NumericDistribution,
    QuestionComparison,
    QuestionDistribution,
    Recommendation,
)
from models.enums import AlignmentStatus, RecommendationPriority, RecommendationType


class CalibrationPipeline:
    """Service for calibrating synthetic personas against real user data.

    Provides import from CSV/JSON, YAML persistence, distribution overlap
    calculation, comparison analysis, and recommendation generation.
    """

    def __init__(
        self,
        baselines_dir: Path | None = None,
        comparisons_dir: Path | None = None,
    ) -> None:
        self.baselines_dir = baselines_dir or Path("calibration/baselines")
        self.comparisons_dir = comparisons_dir or Path("calibration/comparisons")

    # ------------------------------------------------------------------
    # Import
    # ------------------------------------------------------------------

    def import_csv(
        self,
        file_path: Path,
        name: str,
        source: str = "",
        tags: list[str] | None = None,
        collection_date: date | None = None,
    ) -> CalibrationBaseline:
        """Parse a CSV file into a CalibrationBaseline.

        Expected columns: question_id, response_type, response_value,
        demographic_tag (optional).
        """
        rows: list[dict[str, str]] = []
        with open(file_path, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)

        return self._build_baseline(rows, name, source, tags, collection_date)

    def import_json(
        self,
        file_path: Path,
        name: str,
        source: str = "",
        tags: list[str] | None = None,
        collection_date: date | None = None,
    ) -> CalibrationBaseline:
        """Parse a JSON file into a CalibrationBaseline.

        Expected structure: {"responses": [{"question_id": ..., "type": ..., "value": ...}]}
        """
        with open(file_path) as f:
            data = json.load(f)

        # Normalise JSON entries to the same dict shape used by _build_baseline
        rows: list[dict[str, str]] = []
        for entry in data.get("responses", []):
            rows.append({
                "question_id": str(entry["question_id"]),
                "response_type": str(entry["type"]),
                "response_value": str(entry["value"]),
                "demographic_tag": str(entry.get("tag", "")),
            })

        return self._build_baseline(rows, name, source, tags, collection_date)

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save_baseline(self, baseline: CalibrationBaseline) -> Path:
        """Serialize a CalibrationBaseline to YAML and write to disk."""
        self.baselines_dir.mkdir(parents=True, exist_ok=True)
        path = self.baselines_dir / f"{baseline.id}.yaml"
        data = json.loads(baseline.model_dump_json())
        with open(path, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        return path

    def load_baseline(self, baseline_id: str) -> CalibrationBaseline:
        """Load a CalibrationBaseline from a YAML file."""
        path = self.baselines_dir / f"{baseline_id}.yaml"
        with open(path) as f:
            data = yaml.safe_load(f)
        return CalibrationBaseline(**data)

    def list_baselines(self, tags: list[str] | None = None) -> list[CalibrationBaseline]:
        """List all saved baselines, optionally filtering by tags."""
        if not self.baselines_dir.exists():
            return []
        baselines: list[CalibrationBaseline] = []
        for path in sorted(self.baselines_dir.glob("*.yaml")):
            with open(path) as f:
                data = yaml.safe_load(f)
            bl = CalibrationBaseline(**data)
            if tags is not None:
                if any(t in bl.demographic_tags for t in tags):
                    baselines.append(bl)
            else:
                baselines.append(bl)
        return baselines

    def delete_baseline(self, baseline_id: str) -> bool:
        """Delete a baseline YAML file. Returns True if deleted."""
        path = self.baselines_dir / f"{baseline_id}.yaml"
        if path.exists():
            path.unlink()
            return True
        return False

    # ------------------------------------------------------------------
    # Overlap calculation
    # ------------------------------------------------------------------

    def calculate_overlap(
        self,
        synthetic_dist: dict,
        baseline_dist: QuestionDistribution,
    ) -> float:
        """Calculate distribution overlap percentage (0-100).

        For numeric: histogram intersection.
        For categorical: frequency intersection.
        """
        if baseline_dist.distribution_type == "numeric" and baseline_dist.numeric is not None:
            return self._numeric_overlap(synthetic_dist, baseline_dist.numeric)
        if (
            baseline_dist.distribution_type == "categorical"
            and baseline_dist.categorical is not None
        ):
            return self._categorical_overlap(synthetic_dist, baseline_dist.categorical)
        return 0.0

    # ------------------------------------------------------------------
    # Comparison
    # ------------------------------------------------------------------

    def compare(
        self,
        baseline_id: str,
        synthetic_results: list[dict],
    ) -> CalibrationComparison:
        """Compare synthetic results against a saved baseline."""
        baseline = self.load_baseline(baseline_id)

        # Index synthetic results by question_id
        synthetic_by_q: dict[str, list[dict]] = defaultdict(list)
        for result in synthetic_results:
            synthetic_by_q[result["question_id"]].append(result)

        question_comparisons: list[QuestionComparison] = []
        divergence_points: list[str] = []

        for dist in baseline.distributions:
            synth_entries = synthetic_by_q.get(dist.question_id, [])
            if not synth_entries:
                question_comparisons.append(QuestionComparison(
                    question_id=dist.question_id,
                    overlap_percentage=0.0,
                    divergence_detected=True,
                ))
                divergence_points.append(dist.question_id)
                continue

            # Build synthetic distribution dict
            synth_dist = self._build_synthetic_distribution(synth_entries, dist)
            overlap = self.calculate_overlap(synth_dist, dist)

            synth_mean: Optional[float] = synth_dist.get("mean")
            base_mean: Optional[float] = (
                dist.numeric.mean if dist.numeric else None
            )
            mean_diff: Optional[float] = None
            if synth_mean is not None and base_mean is not None:
                mean_diff = synth_mean - base_mean

            divergent = overlap < 60.0
            qc = QuestionComparison(
                question_id=dist.question_id,
                overlap_percentage=overlap,
                synthetic_mean=synth_mean,
                baseline_mean=base_mean,
                mean_difference=mean_diff,
                synthetic_distribution=synth_dist,
                baseline_distribution=dist.model_dump(),
                divergence_detected=divergent,
            )
            question_comparisons.append(qc)
            if divergent:
                divergence_points.append(dist.question_id)

        overall = (
            mean([qc.overlap_percentage for qc in question_comparisons])
            if question_comparisons
            else 0.0
        )

        if overall > 70.0:
            status = AlignmentStatus.ALIGNED
        elif overall >= 60.0:
            status = AlignmentStatus.PARTIAL
        else:
            status = AlignmentStatus.DIVERGENT

        comparison = CalibrationComparison(
            id=str(uuid.uuid4()),
            baseline_id=baseline_id,
            overall_overlap=overall,
            alignment_status=status,
            question_comparisons=question_comparisons,
            divergence_points=divergence_points,
            divergence_summary=f"{len(divergence_points)} divergent question(s) detected",
            synthetic_sample_size=len(synthetic_results),
            baseline_sample_size=baseline.sample_size,
        )
        return comparison

    # ------------------------------------------------------------------
    # Recommendations
    # ------------------------------------------------------------------

    def generate_recommendations(
        self,
        comparison: CalibrationComparison,
    ) -> list[Recommendation]:
        """Generate persona adjustment recommendations from a comparison."""
        recommendations: list[Recommendation] = []

        for qc in comparison.question_comparisons:
            if not qc.divergence_detected:
                continue

            if qc.synthetic_mean is not None and qc.baseline_mean is not None:
                diff = qc.synthetic_mean - qc.baseline_mean
                if diff > 0:
                    # Synthetic is more positive -> increase criticism
                    rec = Recommendation(
                        recommendation_id=str(uuid.uuid4()),
                        target="persona",
                        recommendation_type=RecommendationType.INCREASE,
                        parameter="criticism_tendency",
                        current_value="balanced",
                        suggested_value="critical",
                        rationale=(
                            f"Question {qc.question_id}: synthetic mean ({qc.synthetic_mean:.1f}) "
                            f"exceeds baseline mean ({qc.baseline_mean:.1f}) by {abs(diff):.1f}. "
                            "Increase criticism to reduce positive bias."
                        ),
                        priority=(
                            RecommendationPriority.HIGH
                            if abs(diff) > 2
                            else RecommendationPriority.MEDIUM
                        ),
                        impact_estimate=(
                            f"Expected overlap improvement: ~{min(abs(diff) * 5, 30):.0f}%"
                        ),
                    )
                    recommendations.append(rec)
                elif diff < 0:
                    # Synthetic is more negative -> decrease criticism
                    rec = Recommendation(
                        recommendation_id=str(uuid.uuid4()),
                        target="persona",
                        recommendation_type=RecommendationType.DECREASE,
                        parameter="criticism_tendency",
                        current_value="critical",
                        suggested_value="balanced",
                        rationale=(
                            f"Question {qc.question_id}: synthetic mean ({qc.synthetic_mean:.1f}) "
                            f"is below baseline mean ({qc.baseline_mean:.1f}) by {abs(diff):.1f}. "
                            "Decrease criticism to reduce negative bias."
                        ),
                        priority=(
                            RecommendationPriority.HIGH
                            if abs(diff) > 2
                            else RecommendationPriority.MEDIUM
                        ),
                        impact_estimate=(
                            f"Expected overlap improvement: ~{min(abs(diff) * 5, 30):.0f}%"
                        ),
                    )
                    recommendations.append(rec)

        return recommendations

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _build_baseline(
        self,
        rows: list[dict[str, str]],
        name: str,
        source: str,
        tags: list[str] | None,
        collection_date: date | None,
    ) -> CalibrationBaseline:
        """Build a CalibrationBaseline from normalised row dicts."""
        grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
        for row in rows:
            grouped[row["question_id"]].append(row)

        distributions: list[QuestionDistribution] = []
        total_responses = 0

        for qid, entries in grouped.items():
            resp_type = entries[0]["response_type"]
            if resp_type == "open_ended":
                continue

            total_responses = max(total_responses, len(entries))

            if resp_type == "rating":
                values = [float(e["response_value"]) for e in entries]
                dist = self._build_numeric_distribution(values)
                distributions.append(QuestionDistribution(
                    question_id=qid,
                    distribution_type="numeric",
                    numeric=dist,
                ))
            elif resp_type == "multiple_choice":
                dist = self._build_categorical_distribution(entries)
                distributions.append(QuestionDistribution(
                    question_id=qid,
                    distribution_type="categorical",
                    categorical=dist,
                ))

        sample_size = max(total_responses, 10)

        return CalibrationBaseline(
            id=str(uuid.uuid4()),
            name=name,
            source=source or "imported",
            sample_size=sample_size,
            collection_date=collection_date or date.today(),
            demographic_tags=tags or [],
            distributions=distributions,
        )

    @staticmethod
    def _build_numeric_distribution(values: list[float]) -> NumericDistribution:
        """Compute numeric distribution statistics from raw values."""
        v_mean = mean(values)
        v_stdev = stdev(values) if len(values) > 1 else 0.0
        v_min = min(values)
        v_max = max(values)

        # Build histogram with integer buckets from floor(min) to ceil(max)
        lo = int(v_min)
        hi = int(v_max)
        if hi < v_max:
            hi += 1
        buckets = list(range(lo, hi + 1))
        histogram = [0] * len(buckets)
        for v in values:
            idx = int(v) - lo
            if idx >= len(histogram):
                idx = len(histogram) - 1
            histogram[idx] += 1

        bucket_labels = [str(b) for b in buckets]

        return NumericDistribution(
            mean=v_mean,
            stdev=v_stdev,
            min_value=v_min,
            max_value=v_max,
            histogram=histogram,
            bucket_labels=bucket_labels,
        )

    @staticmethod
    def _build_categorical_distribution(
        entries: list[dict[str, str]],
    ) -> CategoricalDistribution:
        """Compute categorical distribution from raw entries."""
        counts: dict[str, int] = defaultdict(int)
        for e in entries:
            counts[e["response_value"]] += 1
        total = len(entries)
        frequencies = {k: v / total for k, v in counts.items()}
        return CategoricalDistribution(frequencies=frequencies, total_responses=total)

    @staticmethod
    def _numeric_overlap(synthetic: dict, baseline: NumericDistribution) -> float:
        """Histogram intersection overlap for numeric distributions."""
        synth_hist = synthetic.get("histogram", [])
        base_hist = baseline.histogram

        if not base_hist or not synth_hist:
            return 0.0

        # Pad shorter histogram with zeros
        max_len = max(len(synth_hist), len(base_hist))
        sh = list(synth_hist) + [0] * (max_len - len(synth_hist))
        bh = list(base_hist) + [0] * (max_len - len(base_hist))

        intersection = sum(min(s, b) for s, b in zip(sh, bh, strict=False))
        baseline_total = sum(bh)
        if baseline_total == 0:
            return 0.0
        return (intersection / baseline_total) * 100.0

    @staticmethod
    def _categorical_overlap(
        synthetic: dict, baseline: CategoricalDistribution,
    ) -> float:
        """Frequency intersection overlap for categorical distributions."""
        synth_freq = synthetic.get("frequencies", {})
        base_freq = baseline.frequencies

        if not base_freq:
            return 0.0

        all_keys = set(synth_freq.keys()) | set(base_freq.keys())
        intersection = sum(
            min(synth_freq.get(k, 0.0), base_freq.get(k, 0.0))
            for k in all_keys
        )
        baseline_total = sum(base_freq.values())
        if baseline_total == 0:
            return 0.0
        return (intersection / baseline_total) * 100.0

    @staticmethod
    def _build_synthetic_distribution(
        entries: list[dict],
        baseline_dist: QuestionDistribution,
    ) -> dict:
        """Build a synthetic distribution dict matching the baseline type."""
        if baseline_dist.distribution_type == "numeric":
            values = [float(e.get("value", e.get("response_value", 0))) for e in entries]
            v_mean = mean(values) if values else 0.0
            lo = int(min(values))
            hi = int(max(values))
            if hi < max(values):
                hi += 1
            buckets = list(range(lo, hi + 1))
            histogram = [0] * len(buckets)
            for v in values:
                idx = int(v) - lo
                if idx >= len(histogram):
                    idx = len(histogram) - 1
                histogram[idx] += 1
            return {"histogram": histogram, "mean": v_mean}
        else:
            counts: dict[str, int] = defaultdict(int)
            for e in entries:
                val = str(e.get("value", e.get("response_value", "")))
                counts[val] += 1
            total = len(entries)
            frequencies = {k: v / total for k, v in counts.items()}
            return {"frequencies": frequencies}
