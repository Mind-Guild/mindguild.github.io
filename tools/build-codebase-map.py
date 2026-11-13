#!/usr/bin/env python3
"""Build the public code-map metadata from a pinned Mind_Guild checkout.

No source bodies, credentials, machine settings, or meeting data are exported.
Usage: python tools/build-codebase-map.py /path/to/Mind_Guild
       --output research/codebase/map-data.js
For a verified source export, also pass --manifest and --revision.
"""

import argparse
import ast
import hashlib
import json
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


GROUPS = [
    ("entry", "Benchmark runners", "Run, compare and visualize", "benchmark", "run.py and visualize.py select agents and environments, execute training/evaluation episodes, and render comparisons. The experiments/ directory also retains standalone experiment entry points.", ["run.py", "visualize.py", "experiments/visualize.py"]),
    ("agents", "Agent strategies", "Reactive · GNW · RPT · SF", "benchmark", "Adapters implement the BaseAgent interface for reactive, global-workspace, recurrent-processing, successor-feature and object-permanence strategies. Object-permanence agents also include DQN variants.", ["agents/gnw_broadcast.py", "agents/rpt_recurrent.py", "agents/sf_consciousness.py", "agents/op_dqn_agents.py"]),
    ("envs", "Task environments", "Grid · occlusion · MiniHack", "benchmark", "Gymnasium-style wrappers expose the consciousness grid, object permanence, two-step compositional transfer and optional MiniHack tasks through BaseEnv. MiniHack requires its separate optional dependencies.", ["wrappers/consciousness_grid.py", "wrappers/object_permanence.py", "wrappers/two_step_compositional.py", "wrappers/s3q_minihack.py"]),
    ("benchmarks", "Experiment kernels", "Tabular models and sweeps", "benchmark", "The original consciousness-grid agents and environments live in mind_guild_experiment.py. SR_Experiment supplies two-step tabular and model-based successor-feature implementations through explicit file loaders. The MiniHack lab is a separate experiment path.", ["mind_guild_experiment.py", "experiments/SR_Experiment", "experiments/s3q_minihack_lab.py"]),
    ("contracts", "Benchmark interfaces", "Agent and environment APIs", "benchmark", "BaseAgent and BaseEnv define the common interfaces used by the benchmark runner, strategy wrappers and task wrappers. These interfaces are separate from the newer Layer 1 tensor and serving contracts.", ["base_agent.py", "base_env.py"]),
    ("l1experiments", "Layer 1 experiments", "Train · calibrate · evaluate", "layer1", "Offline runners train perception models, calibrate policies, evaluate acceptance, verify ingestion and reproduce a frozen recipe. They assemble the reference runtime and retain configuration, model state and evidence.", ["src/mind_guild/layer1/experiments/training.py", "src/mind_guild/layer1/experiments/acceptance.py", "src/mind_guild/layer1/experiments/reproduction.py"]),
    ("l1runtime", "Layer 1 runtime", "Schedule, state and statistics", "layer1", "Layer1Runtime assembles timestamped ingress, multirate scheduling, model inference, double-buffered slots/liveness, bounded history, SFA, InfoNCE and leased outputs. Checkpoint restoration preserves a reproducible continuation.", ["src/mind_guild/layer1/runtime/engine.py", "src/mind_guild/layer1/runtime/state.py", "src/mind_guild/layer1/runtime/statistics.py", "src/mind_guild/layer1/runtime/scheduler.py"]),
    ("l1model", "Perception model", "Encode, predict and bind slots", "layer1", "The trainable PyTorch model encodes modality-specific observations, projects tokens to a shared width, predicts prior slots and applies a fixed number of competitive attention/refinement iterations. It is used by the reference runtime and training code.", ["src/mind_guild/layer1/models/perception.py"]),
    ("l1contracts", "Layer 1 contracts", "Configuration, payloads, checks", "layer1", "Immutable configuration and reference policy define build inputs. NumPy and tensor contracts enforce sensor, token, slot, liveness and held-output boundaries. Versioned checkpoint utilities serialize model and runtime state.", ["src/mind_guild/layer1/config.py", "src/mind_guild/layer1/policy.py", "src/mind_guild/layer1/interfaces/contracts.py", "src/mind_guild/layer1/interfaces/payloads.py"]),
    ("successor", "Successor features", "Policy features and GPI", "support", "The packaged successor module provides exact policy features, a tabular successor-feature learner and generalized policy improvement. This is a distinct implementation from the legacy benchmark SF wrappers.", ["src/mind_guild/successor.py", "docs/SUCCESSOR_REPRESENTATION.md"]),
    ("verification", "Tests and evidence", "Contracts, replay and acceptance", "support", "Tests cover wrappers, Layer 1 contracts, model boundaries, scheduling, state, checkpoint restoration and successor features. Evidence checkers retain dated reports. File counts describe the snapshot; this map does not execute the tests.", ["tests/test_wrappers.py", "tests/layer1/test_runtime_restore.py", "tests/layer1/test_perception.py", "docs/layer1/VERIFICATION.md"]),
    ("ops", "Meeting operations", "Recording → transcript → summary", "support", "The maintained meeting-operations entry point discovers recordings, transcribes segmented audio, and writes transcripts, summaries and metadata to Drive. A compatibility V2 entry point delegates to it. This is separate from the scientific runtime.", ["mind_guild_ops/transcribe_mind_guild.py", "mind_guild_ops/transcribe_mind_guild_v2.py", "mind_guild_ops/README.md"]),
    ("planning", "Planning and CI", "Tickets, decisions and workflows", "support", "Planning metadata and GitHub workflows support issue tracking, quality checks, strict acceptance and meeting operations. Architecture decisions and coverage records make implementation boundaries explicit.", ["planning/s3q-layer1/BACKLOG.md", ".github/workflows/layer1-quality.yml", ".github/workflows/layer1-acceptance.yml"]),
    ("docs", "Documentation and recipes", "Specifications and frozen inputs", "support", "Documentation, immutable experiment configurations and retained results provide scientific and engineering context for the code. Dated reports are evidence for their recorded environment and source.", ["README.md", "docs/layer1/README.md", "docs/layer1/TRACEABILITY.md", "configs/layer1-reproduction-v1.json"]),
    ("archive", "Scratch experiments", "Historical working material", "archive", "Tracked scratch files retain exploratory versions of experiments and notes. They are inventoried separately from the maintained reference package.", ["scratch/README.md"]),
]


def group(path):
    if path.startswith("scratch/"):
        return "archive"
    if path.startswith("mind_guild_ops/"):
        return "ops"
    if path.startswith(("planning/", ".github/")):
        return "planning"
    if path.startswith(("tests/", "evidence/")):
        return "verification"
    if path in ("run.py", "visualize.py", "experiments/visualize.py"):
        return "entry"
    if path in ("base_agent.py", "base_env.py"):
        return "contracts"
    for prefix, name in [("agents/", "agents"), ("wrappers/", "envs"), ("experiments/", "benchmarks"), ("src/mind_guild/layer1/runtime/", "l1runtime"), ("src/mind_guild/layer1/models/", "l1model"), ("src/mind_guild/layer1/experiments/", "l1experiments")]:
        if path.startswith(prefix):
            return name
    if path == "mind_guild_experiment.py":
        return "benchmarks"
    if path == "src/mind_guild/successor.py":
        return "successor"
    if path.startswith("src/"):
        return "l1contracts"
    return "docs"


def python_file(path):
    return path.endswith(".py") or path in ("experiments/SR_Experiment", "scratch/SR_Experiment")


def module_name(path):
    name = path.removeprefix("src/").removesuffix(".py").replace("/", ".")
    return name.removesuffix(".__init__")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--revision")
    parser.add_argument("--output", type=Path, default=Path("research/codebase/map-data.js"))
    args = parser.parse_args()
    root = args.source.resolve()
    if args.manifest:
        manifest = json.loads(args.manifest.read_text())
        if args.revision and args.revision != manifest["commit"]:
            raise ValueError("Revision differs from verified source manifest")
        revision = manifest["commit"]
        committed = manifest["committed"]
        entries = {f["path"]: f for f in manifest["tree"] if f["type"] == "blob"}
    else:
        revision = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
        if args.revision and args.revision != revision:
            raise ValueError("Source checkout is not at the requested revision")
        if subprocess.check_output(["git", "-C", str(root), "status", "--porcelain"], text=True):
            raise ValueError("Source checkout must be clean")
        committed = subprocess.check_output(["git", "-C", str(root), "show", "-s", "--format=%cI", revision], text=True).strip()
        records = subprocess.check_output(["git", "-C", str(root), "ls-tree", "-r", "--full-tree", "HEAD"], text=True)
        entries = {line.split("\t", 1)[1]: {"sha": line.split()[2]} for line in records.splitlines()}
    paths = sorted(p for p in entries if not any(v in p.split("/") for v in ("__pycache__", ".idea", ".claude")) and p != ".gitignore")
    files = []
    trees = {}
    modules = {module_name(p): p for p in paths if python_file(p)}
    for path in paths:
        item = {"path": path, "group": group(path), "sha": entries[path]["sha"], "python": python_file(path)}
        local = root / path
        if item["python"]:
            raw = local.read_bytes()
            digest = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
            if digest != item["sha"]:
                raise ValueError(f"Source blob mismatch: {path}")
            text = raw.decode("utf-8-sig")
            tree = ast.parse(text, filename=path)
            trees[path] = tree
            item["lines"] = len(text.splitlines())
            item["symbols"] = [{"name": n.name, "line": n.lineno, "kind": "class" if isinstance(n, ast.ClassDef) else "function"} for n in tree.body if isinstance(n, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))]
        else:
            item["symbols"] = []
        files.append(item)
    edges = {}
    external = set()
    for path, tree in trees.items():
        package = module_name(path).split(".")
        if not path.endswith("__init__.py"):
            package = package[:-1]
        for node in ast.walk(tree):
            targets = []
            if isinstance(node, ast.Import):
                targets = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                prefix = package[:len(package) - node.level + 1] if node.level else []
                if node.module:
                    prefix += node.module.split(".")
                base = ".".join(prefix)
                for alias in node.names:
                    child = ".".join(prefix + [alias.name])
                    targets.append(child if child in modules else base)
            for target in targets:
                dest = modules.get(target)
                if dest and dest != path:
                    key = (path, dest)
                    if key not in edges:
                        edges[key] = {"from": path, "to": dest, "line": node.lineno, "kind": "import"}
                elif not dest and target and target.split(".")[0] not in ("__future__", "mind_guild", "tests"):
                    external.add(target.split(".")[0])
    # These three explicit loaders name the extensionless file in _SR_PATH.
    for path in ("agents/model_based_sf.py", "agents/tabular_q.py", "wrappers/two_step_compositional.py"):
        text = (root / path).read_text()
        line = next(i for i, line in enumerate(text.splitlines(), 1) if line.startswith("_SR_PATH ="))
        edges[(path, "experiments/SR_Experiment")] = {"from": path, "to": "experiments/SR_Experiment", "line": line, "kind": "loader"}
    counts = Counter(f["group"] for f in files)
    group_data = [{"id": v[0], "label": v[1], "subtitle": v[2], "track": v[3], "description": v[4], "featured": v[5], "count": counts[v[0]]} for v in GROUPS]
    result = {"repository": "Mind-Guild/Mind_Guild", "revision": revision, "committed": committed, "generated": datetime.now(timezone.utc).date().isoformat(), "method": "Python AST imports, three reviewed explicit SR_Experiment loaders, and source-reviewed module/pipeline annotations. Static imports include function-local, optional and type-checking branches; arbitrary dynamic imports and runtime calls are not inferred.", "groups": group_data, "files": files, "edges": sorted(edges.values(), key=lambda e: (e["from"], e["to"])), "stats": {"files": len(files), "python": len(trees), "imports": len(edges), "testFiles": sum(1 for p in trees if Path(p).name.startswith("test_")), "sourceLines": sum(f.get("lines", 0) for f in files)}, "externalModules": sorted(external)}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("/* Generated metadata only; see tools/build-codebase-map.py. */\nwindow.MIND_GUILD_MAP = " + json.dumps(result, ensure_ascii=False, separators=(",", ":")) + ";\n")
    print(json.dumps({"revision": revision, **result["stats"]}))


if __name__ == "__main__":
    main()
