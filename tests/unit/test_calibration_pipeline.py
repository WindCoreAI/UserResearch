"""Tests for CalibrationPipeline service (T071-T075).

Validates CSV/JSON import, overlap calculation, recommendation generation,
and YAML persistence for calibration baselines.
"""

import pytest
import tempfile
import csv
import json
from pathlib import Path

from services.calibration_pipeline import CalibrationPipeline
from models.calibration import CalibrationBaseline, QualityThresholds


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_csv(path: Path, rows: list[dict]) -> Path:
    """Write a list of dicts as a CSV file."""
    fieldnames = list(rows[0].keys())
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return path


def _write_json(path: Path, data: dict) -> Path:
    """Write a dict as a JSON file."""
    with open(path, "w") as f:
        json.dump(data, f)
    return path


def _rating_csv_rows(question_id: str = "q1", count: int = 20) -> list[dict]:
    """Generate rating-type CSV rows with predictable values (1 to count)."""
    return [
        {
            "question_id": question_id,
            "response_type": "rating",
            "response_value": str((i % 10) + 1),
        }
        for i in range(count)
    ]


def _choice_csv_rows(question_id: str = "q2", count: int = 20) -> list[dict]:
    """Generate multiple_choice CSV rows."""
    options = ["Privacy", "Cost", "Complexity", "None"]
    return [
        {
            "question_id": question_id,
            "response_type": "multiple_choice",
            "response_value": options[i % len(options)],
        }
        for i in range(count)
    ]


def _open_ended_csv_rows(question_id: str = "q3", count: int = 5) -> list[dict]:
    """Generate open_ended CSV rows (should be skipped)."""
    return [
        {
            "question_id": question_id,
            "response_type": "open_ended",
            "response_value": f"Some text response {i}",
        }
        for i in range(count)
    ]


def _json_responses(
    question_id: str = "q1",
    resp_type: str = "rating",
    count: int = 20,
) -> list[dict]:
    """Generate JSON response entries."""
    if resp_type == "rating":
        return [
            {"question_id": question_id, "type": "rating", "value": (i % 10) + 1}
            for i in range(count)
        ]
    else:
        options = ["Privacy", "Cost", "Complexity", "None"]
        return [
            {"question_id": question_id, "type": "multiple_choice", "value": options[i % 4]}
            for i in range(count)
        ]


# ---------------------------------------------------------------------------
# T071: import_csv
# ---------------------------------------------------------------------------


class TestImportCSV:
    """Tests for CalibrationPipeline.import_csv (T071)."""

    def test_import_csv_creates_baseline(self):
        """import_csv returns a CalibrationBaseline with correct name."""
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "data.csv"
            _write_csv(csv_path, _rating_csv_rows("q1", 20))
            pipeline = CalibrationPipeline(baselines_dir=Path(tmpdir) / "baselines")
            baseline = pipeline.import_csv(csv_path, name="Test CSV")
            assert isinstance(baseline, CalibrationBaseline)
            assert baseline.name == "Test CSV"
            assert baseline.sample_size >= 10

    def test_import_csv_numeric_distribution(self):
        """import_csv produces numeric distribution for rating questions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "data.csv"
            _write_csv(csv_path, _rating_csv_rows("q1", 20))
            pipeline = CalibrationPipeline(baselines_dir=Path(tmpdir) / "baselines")
            baseline = pipeline.import_csv(csv_path, name="Ratings")
            dist = baseline.distributions[0]
            assert dist.distribution_type == "numeric"
            assert dist.numeric is not None
            assert dist.numeric.mean > 0

    def test_import_csv_categorical_distribution(self):
        """import_csv produces categorical distribution for multiple_choice questions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "data.csv"
            _write_csv(csv_path, _choice_csv_rows("q2", 20))
            pipeline = CalibrationPipeline(baselines_dir=Path(tmpdir) / "baselines")
            baseline = pipeline.import_csv(csv_path, name="Choices")
            dist = baseline.distributions[0]
            assert dist.distribution_type == "categorical"
            assert dist.categorical is not None
            assert "Privacy" in dist.categorical.frequencies

    def test_import_csv_skips_open_ended(self):
        """import_csv skips open_ended response types."""
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "data.csv"
            rows = _rating_csv_rows("q1", 20) + _open_ended_csv_rows("q3", 5)
            _write_csv(csv_path, rows)
            pipeline = CalibrationPipeline(baselines_dir=Path(tmpdir) / "baselines")
            baseline = pipeline.import_csv(csv_path, name="Mixed")
            question_ids = [d.question_id for d in baseline.distributions]
            assert "q3" not in question_ids
            assert "q1" in question_ids

    def test_import_csv_multiple_questions(self):
        """import_csv handles multiple questions in a single CSV."""
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "data.csv"
            rows = _rating_csv_rows("q1", 20) + _choice_csv_rows("q2", 20)
            _write_csv(csv_path, rows)
            pipeline = CalibrationPipeline(baselines_dir=Path(tmpdir) / "baselines")
            baseline = pipeline.import_csv(csv_path, name="Multi")
            assert len(baseline.distributions) == 2


# ---------------------------------------------------------------------------
# T072: import_json
# ---------------------------------------------------------------------------


class TestImportJSON:
    """Tests for CalibrationPipeline.import_json (T072)."""

    def test_import_json_creates_baseline(self):
        """import_json returns a CalibrationBaseline."""
        with tempfile.TemporaryDirectory() as tmpdir:
            json_path = Path(tmpdir) / "data.json"
            _write_json(json_path, {"responses": _json_responses("q1", "rating", 20)})
            pipeline = CalibrationPipeline(baselines_dir=Path(tmpdir) / "baselines")
            baseline = pipeline.import_json(json_path, name="Test JSON")
            assert isinstance(baseline, CalibrationBaseline)
            assert baseline.name == "Test JSON"

    def test_import_json_numeric_distribution(self):
        """import_json produces numeric distribution for rating responses."""
        with tempfile.TemporaryDirectory() as tmpdir:
            json_path = Path(tmpdir) / "data.json"
            _write_json(json_path, {"responses": _json_responses("q1", "rating", 20)})
            pipeline = CalibrationPipeline(baselines_dir=Path(tmpdir) / "baselines")
            baseline = pipeline.import_json(json_path, name="JSON Ratings")
            dist = baseline.distributions[0]
            assert dist.distribution_type == "numeric"
            assert dist.numeric is not None

    def test_import_json_categorical_distribution(self):
        """import_json produces categorical distribution for multiple_choice responses."""
        with tempfile.TemporaryDirectory() as tmpdir:
            json_path = Path(tmpdir) / "data.json"
            responses = _json_responses("q2", "multiple_choice", 20)
            _write_json(json_path, {"responses": responses})
            pipeline = CalibrationPipeline(baselines_dir=Path(tmpdir) / "baselines")
            baseline = pipeline.import_json(json_path, name="JSON Choices")
            dist = baseline.distributions[0]
            assert dist.distribution_type == "categorical"
            assert dist.categorical is not None


# ---------------------------------------------------------------------------
# T073: calculate_overlap
# ---------------------------------------------------------------------------


class TestCalculateOverlap:
    """Tests for CalibrationPipeline.calculate_overlap (T073)."""

    def test_perfect_numeric_overlap(self):
        """Identical numeric histograms yield 100% overlap."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pipeline = CalibrationPipeline(baselines_dir=Path(tmpdir) / "baselines")
            from models.calibration import NumericDistribution, QuestionDistribution

            nd = NumericDistribution(
                mean=5.0, stdev=1.5, min_value=1.0, max_value=10.0,
                histogram=[1, 2, 3, 4, 5, 5, 4, 3, 2, 1],
                bucket_labels=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
            )
            qd = QuestionDistribution(
                question_id="q1", distribution_type="numeric", numeric=nd,
            )
            synthetic = {"histogram": [1, 2, 3, 4, 5, 5, 4, 3, 2, 1]}
            overlap = pipeline.calculate_overlap(synthetic, qd)
            assert overlap == pytest.approx(100.0)

    def test_zero_numeric_overlap(self):
        """Non-overlapping numeric histograms yield 0% overlap."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pipeline = CalibrationPipeline(baselines_dir=Path(tmpdir) / "baselines")
            from models.calibration import NumericDistribution, QuestionDistribution

            nd = NumericDistribution(
                mean=5.0, stdev=1.5, min_value=1.0, max_value=10.0,
                histogram=[10, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                bucket_labels=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
            )
            qd = QuestionDistribution(
                question_id="q1", distribution_type="numeric", numeric=nd,
            )
            synthetic = {"histogram": [0, 0, 0, 0, 0, 0, 0, 0, 0, 10]}
            overlap = pipeline.calculate_overlap(synthetic, qd)
            assert overlap == pytest.approx(0.0)

    def test_partial_numeric_overlap(self):
        """Partially overlapping histograms yield intermediate overlap."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pipeline = CalibrationPipeline(baselines_dir=Path(tmpdir) / "baselines")
            from models.calibration import NumericDistribution, QuestionDistribution

            nd = NumericDistribution(
                mean=5.0, stdev=1.5, min_value=1.0, max_value=5.0,
                histogram=[2, 4, 6, 4, 2],
                bucket_labels=["1", "2", "3", "4", "5"],
            )
            qd = QuestionDistribution(
                question_id="q1", distribution_type="numeric", numeric=nd,
            )
            synthetic = {"histogram": [4, 4, 4, 4, 4]}
            overlap = pipeline.calculate_overlap(synthetic, qd)
            assert 0 < overlap < 100

    def test_perfect_categorical_overlap(self):
        """Identical categorical frequencies yield 100% overlap."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pipeline = CalibrationPipeline(baselines_dir=Path(tmpdir) / "baselines")
            from models.calibration import CategoricalDistribution, QuestionDistribution

            cd = CategoricalDistribution(
                frequencies={"A": 0.5, "B": 0.3, "C": 0.2},
                total_responses=100,
            )
            qd = QuestionDistribution(
                question_id="q2", distribution_type="categorical", categorical=cd,
            )
            synthetic = {"frequencies": {"A": 0.5, "B": 0.3, "C": 0.2}}
            overlap = pipeline.calculate_overlap(synthetic, qd)
            assert overlap == pytest.approx(100.0)

    def test_zero_categorical_overlap(self):
        """Non-overlapping categorical frequencies yield 0% overlap."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pipeline = CalibrationPipeline(baselines_dir=Path(tmpdir) / "baselines")
            from models.calibration import CategoricalDistribution, QuestionDistribution

            cd = CategoricalDistribution(
                frequencies={"A": 0.5, "B": 0.5},
                total_responses=100,
            )
            qd = QuestionDistribution(
                question_id="q2", distribution_type="categorical", categorical=cd,
            )
            synthetic = {"frequencies": {"C": 0.6, "D": 0.4}}
            overlap = pipeline.calculate_overlap(synthetic, qd)
            assert overlap == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# T074: generate_recommendations
# ---------------------------------------------------------------------------


class TestGenerateRecommendations:
    """Tests for CalibrationPipeline.generate_recommendations (T074)."""

    def test_generates_recommendations_for_divergent(self):
        """generate_recommendations produces recommendations for divergent questions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pipeline = CalibrationPipeline(baselines_dir=Path(tmpdir) / "baselines")
            from models.calibration import (
                CalibrationComparison,
                QuestionComparison,
            )
            from models.enums import AlignmentStatus

            comparison = CalibrationComparison(
                id="comp-test",
                baseline_id="baseline-001",
                overall_overlap=45.0,
                alignment_status=AlignmentStatus.DIVERGENT,
                question_comparisons=[
                    QuestionComparison(
                        question_id="q1",
                        overlap_percentage=40.0,
                        synthetic_mean=8.0,
                        baseline_mean=5.0,
                        mean_difference=3.0,
                        divergence_detected=True,
                    ),
                ],
                synthetic_sample_size=30,
                baseline_sample_size=50,
            )
            recs = pipeline.generate_recommendations(comparison)
            assert len(recs) >= 1
            assert recs[0].parameter == "criticism_tendency"

    def test_increase_criticism_when_synthetic_higher(self):
        """Recommends increasing criticism when synthetic mean > baseline mean."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pipeline = CalibrationPipeline(baselines_dir=Path(tmpdir) / "baselines")
            from models.calibration import CalibrationComparison, QuestionComparison
            from models.enums import AlignmentStatus, RecommendationType

            comparison = CalibrationComparison(
                id="comp-test",
                baseline_id="baseline-001",
                overall_overlap=50.0,
                alignment_status=AlignmentStatus.DIVERGENT,
                question_comparisons=[
                    QuestionComparison(
                        question_id="q1",
                        overlap_percentage=40.0,
                        synthetic_mean=8.5,
                        baseline_mean=5.0,
                        mean_difference=3.5,
                        divergence_detected=True,
                    ),
                ],
                synthetic_sample_size=20,
                baseline_sample_size=50,
            )
            recs = pipeline.generate_recommendations(comparison)
            increase_recs = [r for r in recs if r.recommendation_type == RecommendationType.INCREASE]
            assert len(increase_recs) >= 1

    def test_decrease_criticism_when_synthetic_lower(self):
        """Recommends decreasing criticism when synthetic mean < baseline mean."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pipeline = CalibrationPipeline(baselines_dir=Path(tmpdir) / "baselines")
            from models.calibration import CalibrationComparison, QuestionComparison
            from models.enums import AlignmentStatus, RecommendationType

            comparison = CalibrationComparison(
                id="comp-test",
                baseline_id="baseline-001",
                overall_overlap=50.0,
                alignment_status=AlignmentStatus.DIVERGENT,
                question_comparisons=[
                    QuestionComparison(
                        question_id="q1",
                        overlap_percentage=40.0,
                        synthetic_mean=3.0,
                        baseline_mean=6.0,
                        mean_difference=-3.0,
                        divergence_detected=True,
                    ),
                ],
                synthetic_sample_size=20,
                baseline_sample_size=50,
            )
            recs = pipeline.generate_recommendations(comparison)
            decrease_recs = [
                r for r in recs if r.recommendation_type == RecommendationType.DECREASE
            ]
            assert len(decrease_recs) >= 1

    def test_no_recommendations_when_aligned(self):
        """No recommendations generated when all questions are aligned."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pipeline = CalibrationPipeline(baselines_dir=Path(tmpdir) / "baselines")
            from models.calibration import CalibrationComparison, QuestionComparison
            from models.enums import AlignmentStatus

            comparison = CalibrationComparison(
                id="comp-test",
                baseline_id="baseline-001",
                overall_overlap=85.0,
                alignment_status=AlignmentStatus.ALIGNED,
                question_comparisons=[
                    QuestionComparison(
                        question_id="q1",
                        overlap_percentage=85.0,
                        divergence_detected=False,
                    ),
                ],
                synthetic_sample_size=20,
                baseline_sample_size=50,
            )
            recs = pipeline.generate_recommendations(comparison)
            assert len(recs) == 0


# ---------------------------------------------------------------------------
# T075: save_baseline / load_baseline
# ---------------------------------------------------------------------------


class TestBaselinePersistence:
    """Tests for save_baseline and load_baseline YAML persistence (T075)."""

    def test_save_baseline_creates_file(self):
        """save_baseline writes a YAML file to baselines_dir."""
        with tempfile.TemporaryDirectory() as tmpdir:
            baselines_dir = Path(tmpdir) / "baselines"
            pipeline = CalibrationPipeline(baselines_dir=baselines_dir)

            csv_path = Path(tmpdir) / "data.csv"
            _write_csv(csv_path, _rating_csv_rows("q1", 20))
            baseline = pipeline.import_csv(csv_path, name="Persistence Test")

            saved_path = pipeline.save_baseline(baseline)
            assert saved_path.exists()
            assert saved_path.suffix == ".yaml"

    def test_load_baseline_round_trip(self):
        """save then load returns equivalent baseline."""
        with tempfile.TemporaryDirectory() as tmpdir:
            baselines_dir = Path(tmpdir) / "baselines"
            pipeline = CalibrationPipeline(baselines_dir=baselines_dir)

            csv_path = Path(tmpdir) / "data.csv"
            _write_csv(csv_path, _rating_csv_rows("q1", 20))
            baseline = pipeline.import_csv(csv_path, name="Round Trip")

            pipeline.save_baseline(baseline)
            loaded = pipeline.load_baseline(baseline.id)
            assert loaded.id == baseline.id
            assert loaded.name == baseline.name
            assert loaded.sample_size == baseline.sample_size
            assert len(loaded.distributions) == len(baseline.distributions)

    def test_list_baselines(self):
        """list_baselines returns all saved baselines."""
        with tempfile.TemporaryDirectory() as tmpdir:
            baselines_dir = Path(tmpdir) / "baselines"
            pipeline = CalibrationPipeline(baselines_dir=baselines_dir)

            csv_path = Path(tmpdir) / "data.csv"
            _write_csv(csv_path, _rating_csv_rows("q1", 20))
            b1 = pipeline.import_csv(csv_path, name="Baseline 1", tags=["tag_a"])
            b2 = pipeline.import_csv(csv_path, name="Baseline 2", tags=["tag_b"])
            pipeline.save_baseline(b1)
            pipeline.save_baseline(b2)

            all_baselines = pipeline.list_baselines()
            assert len(all_baselines) == 2

    def test_list_baselines_filter_by_tags(self):
        """list_baselines filters by tags when provided."""
        with tempfile.TemporaryDirectory() as tmpdir:
            baselines_dir = Path(tmpdir) / "baselines"
            pipeline = CalibrationPipeline(baselines_dir=baselines_dir)

            csv_path = Path(tmpdir) / "data.csv"
            _write_csv(csv_path, _rating_csv_rows("q1", 20))
            b1 = pipeline.import_csv(csv_path, name="Baseline A", tags=["alpha"])
            b2 = pipeline.import_csv(csv_path, name="Baseline B", tags=["beta"])
            pipeline.save_baseline(b1)
            pipeline.save_baseline(b2)

            filtered = pipeline.list_baselines(tags=["alpha"])
            assert len(filtered) == 1
            assert filtered[0].name == "Baseline A"

    def test_delete_baseline(self):
        """delete_baseline removes the YAML file and returns True."""
        with tempfile.TemporaryDirectory() as tmpdir:
            baselines_dir = Path(tmpdir) / "baselines"
            pipeline = CalibrationPipeline(baselines_dir=baselines_dir)

            csv_path = Path(tmpdir) / "data.csv"
            _write_csv(csv_path, _rating_csv_rows("q1", 20))
            baseline = pipeline.import_csv(csv_path, name="To Delete")
            pipeline.save_baseline(baseline)

            result = pipeline.delete_baseline(baseline.id)
            assert result is True
            assert len(pipeline.list_baselines()) == 0

    def test_delete_baseline_nonexistent(self):
        """delete_baseline returns False for non-existent baseline."""
        with tempfile.TemporaryDirectory() as tmpdir:
            baselines_dir = Path(tmpdir) / "baselines"
            pipeline = CalibrationPipeline(baselines_dir=baselines_dir)
            result = pipeline.delete_baseline("nonexistent-id")
            assert result is False
