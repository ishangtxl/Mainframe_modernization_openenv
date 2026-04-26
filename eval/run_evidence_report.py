"""Generate score summary and plot artifacts for the submission."""

from __future__ import annotations

import json
from pathlib import Path

from legacy_cobol_env.eval.evidence_report import build_score_summary, load_json, write_score_plot
from legacy_cobol_env.server.task_bank import all_tasks


ENV_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ENV_ROOT / "outputs" / "evals"
TRAINING_DIR = ENV_ROOT / "outputs" / "training"
HISTORICAL_OUTPUT_DIR = OUTPUT_DIR / "historical"
PLOT_DIR = ENV_ROOT / "plots"


def main() -> None:
    baseline = load_json(OUTPUT_DIR / "baseline_results.json")
    evidence_notes = []
    oracle_model = _load_current_rollout(OUTPUT_DIR / "oracle_model_rollouts.json", evidence_notes)
    base_qwen3 = _load_current_rollout(OUTPUT_DIR / "base_qwen3_14b_all_tasks.json", evidence_notes)
    zeroshot = _load_current_rollout(OUTPUT_DIR / "azure_gpt54mini_zeroshot_rollouts.json", evidence_notes)
    repair = _load_current_rollout(OUTPUT_DIR / "azure_gpt54mini_repair1_rollouts.json", evidence_notes)
    trained_summary = _load_training_summary(TRAINING_DIR / "sft_run_metadata.json", evidence_notes)
    _record_historical_artifacts(evidence_notes)
    summary = build_score_summary(
        baseline,
        zeroshot=zeroshot,
        repair=repair,
        oracle_model=oracle_model,
        base_model=base_qwen3,
        trained_summary=trained_summary,
        evidence_notes=evidence_notes,
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PLOT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "score_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_score_plot(summary, PLOT_DIR / "model_scores.svg")
    print(json.dumps(summary["policies"], indent=2))


def _load_current_rollout(path: Path, evidence_notes: list[str]) -> dict | None:
    if not path.exists():
        evidence_notes.append(f"missing rollout artifact: {_display_path(path)}")
        return None
    artifact = load_json(path)
    if _matches_current_task_artifacts(artifact):
        return artifact
    evidence_notes.append(f"stale rollout artifact skipped after task hardening: {_display_path(path)}")
    return None


def _load_training_summary(path: Path, evidence_notes: list[str]) -> dict | None:
    if not path.exists():
        evidence_notes.append(f"missing training metadata: {_display_path(path)}")
        return None
    metadata = load_json(path)
    if metadata.get("status") != "completed":
        evidence_notes.append(f"non-completed training metadata skipped: {_display_path(path)}")
        return None
    return metadata


def _record_historical_artifacts(evidence_notes: list[str]) -> None:
    if not HISTORICAL_OUTPUT_DIR.exists():
        return
    for path in sorted(HISTORICAL_OUTPUT_DIR.glob("azure_gpt54mini_*.json")):
        evidence_notes.append(f"historical artifact retained outside current score summary: {_display_path(path)}")


def _display_path(path: Path) -> str:
    try:
        return path.relative_to(ENV_ROOT).as_posix()
    except ValueError:
        return path.name


def _matches_current_task_artifacts(artifact: dict) -> bool:
    current = {
        task.task_id: {
            "files": sorted(task.cobol_files),
            "copybooks": sorted(task.copybooks),
        }
        for task in all_tasks()
    }
    trajectories = artifact.get("trajectories", [])
    if len(trajectories) != len(current):
        return False
    for trajectory in trajectories:
        task_id = trajectory.get("task_id")
        ticket = trajectory.get("ticket") or {}
        expected = current.get(task_id)
        if expected is None:
            return False
        if sorted(ticket.get("available_files", [])) != expected["files"]:
            return False
        if sorted(ticket.get("available_copybooks", [])) != expected["copybooks"]:
            return False
    return True


if __name__ == "__main__":
    main()
