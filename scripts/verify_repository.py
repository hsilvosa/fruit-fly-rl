"""Check repository documentation, package discovery, and CLI help without training."""
from pathlib import Path
import importlib.util
import json
import re
import subprocess
import sys


def verify(root):
    errors = []
    markdown = [root / name for name in ("README.md", "ROADMAP.md", "CONTRIBUTING.md")]
    markdown.extend(sorted((root / "docs").rglob("*.md")))
    checked_links = 0
    for path in markdown:
        if not path.is_file():
            errors.append(f"Missing document: {path.relative_to(root)}")
            continue
        for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
            target = target.strip().strip("<>").split("#", 1)[0]
            if not target or "://" in target or target.startswith("mailto:"):
                continue
            checked_links += 1
            if not (path.parent / target).exists():
                errors.append(f"Broken link in {path.relative_to(root)}: {target}")
    modules = [
        "fly_rl.navigation.observed_map", "fly_rl.navigation.goal_margin",
        "fly_rl.navigation.cruise", "fly_rl.navigation.free_margin",
        "fly_rl.navigation.speed_margin", "fly_rl.navigation.adaptive_margin",
        "fly_rl.navigation.registry", "fly_rl.navigation.distance_stable",
        "fly_rl.navigation.persistent_route", "fly_rl.navigation.ray_consistent",
        "fly_rl.connectome.distance_readout", "fly_rl.connectome.dual_readout",
        "fly_rl.navigation.momentum_guard", "fly_rl.navigation.dual_safety", "fly_rl.atomic_io",
        "fly_rl.training.mastery_curriculum",
        "fly_rl.simulation.map_profiles", "fly_rl.training.geometry_curriculum", "fly_rl.training.geometry_comparison", "fly_rl.visualization.map_report",
        "fly_rl.training.collision_diagnostics", "fly_rl.training.risk_shaping", "fly_rl.training.risk_comparison", "fly_rl.cli", "fly_rl.connectome.brain", "fly_rl.connectome.data",
        "fly_rl.connectome.anatomy", "fly_rl.simulation.world", "fly_rl.simulation.sensors",
        "fly_rl.simulation.flight", "fly_rl.training.learning", "fly_rl.training.evaluation",
        "fly_rl.training.iteration", "fly_rl.training.dense_training", "fly_rl.training.suites",
        "fly_rl.training.selection", "fly_rl.training.generalization", "fly_rl.visualization.viewer",
        "fly_rl.visualization.camera", "fly_rl.visualization.brain_map", "fly_rl.visualization.neural_view",
        "fly_rl.visualization.neural_trace", "fly_rl.visualization.playback", "fly_rl.visualization.plotting",
        "fly_rl.visualization.dense_report", "fly_rl.recordings.recording", "fly_rl.recordings.archive",
        "fly_rl.recordings.replay", "fly_rl.recordings.shutdown", "fly_rl.simulation.planner",
        "fly_rl.visualization.generalization_report", "fly_rl.training.diagnostics", "fly_rl.training.experiment_selection", "fly_rl.training.test_access", "fly_rl.training.sensor_migration", "fly_rl.training.sensor_comparison", "fly_rl.training.approach_curriculum", "fly_rl.training.approach_comparison", "fly_rl.training.validation_trace", "fly_rl.visualization.validation_trace", "fly_rl.training.fresh_sensor_comparison", "fly_rl.visualization.validation_failures",
    ]
    for module in modules:
        spec = importlib.util.find_spec(module)
        if spec is None or spec.origin is None:
            errors.append(f"Undiscoverable module: {module}")
        elif not Path(spec.origin).resolve().is_relative_to(root.resolve()):
            errors.append(f"Module resolves outside this repository: {module}")
    commands = [
        "map-report", "prepare-geometry-comparison", "run-geometry-comparison",
        "diagnose-collisions", "prepare-risk-comparison", "run-risk-comparison", "prepare-data", "benchmark", "demo", "inspect", "recover", "compare", "replay",
        "train", "smoke-test", "evaluate", "select-policy", "plot-training", "prepare-suite",
        "train-dense", "plot-dense", "final-test", "iterate", "diagnose-validation", "select-experiment", "plot-generalization", "migrate-sensors", "compare-sensors", "prepare-approach-comparison", "run-approach-comparison", "trace-validation", "plot-validation-trace", "plot-validation-failures", "prepare-fresh-comparison", "run-fresh-comparison",
    ]
    for command in commands:
        result = subprocess.run(
            [sys.executable, "-s", "-m", "fly_rl", command, "--help"],
            cwd=root, capture_output=True, text=True, timeout=30,
        )
        if result.returncode or "usage:" not in result.stdout:
            errors.append(f"CLI help failed for {command}: {result.stderr.strip()}")
    return {
        "status": "passed" if not errors else "failed",
        "documents": len(markdown), "local_links": checked_links,
        "modules": len(modules), "subcommand_help": len(commands),
        "training_invoked": False, "evaluation_invoked": False, "errors": errors,
    }


if __name__ == "__main__":
    report = verify(Path(__file__).resolve().parents[1])
    print(json.dumps(report, indent=2))
    raise SystemExit(bool(report["errors"]))
