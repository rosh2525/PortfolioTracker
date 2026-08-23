import json
from pathlib import Path

from apps.insights.scoring import calculate_signal


def test_offline_evaluation_fixtures_land_in_expected_bands():
    fixture_path = Path(__file__).parent / "fixtures" / "evaluations.json"
    evaluations = json.loads(fixture_path.read_text())
    for evaluation in evaluations:
        factors = {
            name: {"score": score, "available": True, "explanation": f"Fixture evidence for {name}"}
            for name, score in evaluation["factors"].items()
        }
        signal, rating, coverage = calculate_signal(factors)
        assert signal is not None
        assert evaluation["expected"][0] <= signal <= evaluation["expected"][1]
        assert rating is not None
        assert coverage == 100
