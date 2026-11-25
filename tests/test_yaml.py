from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
HA = ROOT / "homeassistant"


class InputLoader(yaml.SafeLoader):
    pass


def _input(loader, node):
    if isinstance(node, yaml.ScalarNode):
        return f"!input {loader.construct_scalar(node)}"
    if isinstance(node, yaml.SequenceNode):
        return loader.construct_sequence(node)
    return loader.construct_mapping(node)


InputLoader.add_constructor("!input", _input)


def _yaml_files():
    return sorted(HA.rglob("*.yaml")) + sorted((ROOT / "prompts").glob("*.yaml"))


def test_home_assistant_yaml_parses():
    files = list(_yaml_files()) + [ROOT / "config.example.yaml"]
    assert files, "expected YAML files in the repo"
    for path in files:
        raw = path.read_text(encoding="utf-8")
        yaml.load(raw, Loader=InputLoader)


def test_package_has_no_private_identifiers():
    forbidden = (
        "byron",
        "east_alley",
        "west_alley",
        "east alley",
        "west alley",
        "01M7PM",
        "security_token",
        "simplelogin",
        "192.168.",
        "api.x.ai/v1/",  # ok in docs maybe; check package only
    )
    # Tight check on shipped Home Assistant YAML and the visits card.
    texts = [p.read_text(encoding="utf-8").lower() for p in HA.rglob("*") if p.is_file() and p.suffix in {".yaml", ".js", ".md"}]
    blob = "\n".join(texts)
    for item in ("byron", "east_alley", "west_alley", "east alley", "west alley", "01m7pm", "security_token="):
        assert item not in blob, f"private identifier leaked: {item}"
