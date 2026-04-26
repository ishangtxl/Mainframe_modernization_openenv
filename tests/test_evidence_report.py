from pathlib import Path

from legacy_cobol_env.eval.evidence_report import build_score_summary, write_score_plot


def test_score_summary_identifies_visible_pass_hidden_failures():
    baseline = {
        "mean_public_score": {"identity": 0.15},
        "results": [{"task_id": "invoice_occurs_001", "policy": "identity", "public_score": 0.15}],
    }
    zeroshot = {
        "mean_public_score": 0.305,
        "accepted_count": 1,
        "task_count": 1,
        "trajectories": [{"task_id": "invoice_occurs_001", "final": {"public_score": 0.23, "accepted": False}}],
    }
    repair = {
        "mean_public_score": 0.92055,
        "accepted_count": 5,
        "task_count": 1,
        "trajectories": [
            {
                "task_id": "invoice_occurs_001",
                "visible": {"pass_rate": 1.0},
                "final": {
                    "public_score": 0.5233,
                    "accepted": False,
                    "components": {"hidden_correctness": 0.3333, "fresh_correctness": 0.5},
                },
            }
        ],
    }

    summary = build_score_summary(baseline, zeroshot, repair)

    assert summary["policies"]["gpt-5.4-mini + repair1"]["mean_public_score"] == 0.92055
    assert summary["task_scores"]["invoice_occurs_001"]["repair1"] == 0.5233
    assert summary["training_targets"][0]["task_id"] == "invoice_occurs_001"
    assert summary["training_targets"][0]["reason"] == "visible-pass-hidden-fresh-gap"


def test_score_summary_includes_real_sft_before_after_evidence():
    baseline = {
        "mean_public_score": {"identity": 0.15},
        "results": [{"task_id": "invoice_occurs_001", "policy": "identity", "public_score": 0.15}],
    }
    base_model = {
        "mean_public_score": 0.532,
        "accepted_count": 2,
        "task_count": 6,
        "trajectories": [
            {"task_id": "invoice_occurs_001", "final": {"public_score": 0.15}},
        ],
    }
    trained = {
        "model": "Qwen/Qwen3-14B",
        "method": "Hugging Face TRL LoRA SFT",
        "dataset_examples": 15,
        "loss_first": 1.135,
        "loss_last": 0.1924,
        "mean_token_accuracy_first": 0.7938,
        "mean_token_accuracy_last": 0.9483,
        "base_mean_public_score": 0.532,
        "trained_mean_public_score": 0.7971166666666667,
        "base_accepted_count": 2,
        "trained_accepted_count": 4,
        "task_count": 6,
    }

    summary = build_score_summary(baseline, base_model=base_model, trained_summary=trained)

    assert summary["policies"]["base Qwen3-14B"]["mean_public_score"] == 0.532
    assert summary["policies"]["trained Qwen3-14B LoRA SFT"]["accepted_count"] == 4
    assert summary["training_evidence"]["loss_last"] == 0.1924
    assert summary["task_scores"]["invoice_occurs_001"]["base_qwen3_14b"] == 0.15


def test_score_plot_writes_svg(tmp_path: Path):
    summary = {
        "policies": {
            "identity": {"mean_public_score": 0.15, "accepted_count": 0, "task_count": 6},
            "gpt-5.4-mini + repair1": {"mean_public_score": 0.92055, "accepted_count": 5, "task_count": 6},
        }
    }
    output = tmp_path / "scores.svg"

    write_score_plot(summary, output)

    assert output.read_text(encoding="utf-8").startswith("<svg")
