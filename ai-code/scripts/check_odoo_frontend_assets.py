#!/usr/bin/env python3
"""Lightweight validator for Odoo frontend action asset wiring.

Checks the chain:
ir.actions.client tag -> JS action registry -> action class -> static template
-> XML t-name -> manifest web.assets_backend declaration.
"""

from __future__ import annotations

import argparse
import ast
import glob
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
import xml.etree.ElementTree as ET


ACTION_DIR = Path("static/src/js/actions")
TEMPLATE_DIR = Path("static/src/xml")


@dataclass
class ClientActionTag:
    tag: str
    file: Path
    record_id: str | None = None


@dataclass
class RegistryRegistration:
    key: str
    component: str
    file: Path


@dataclass
class ClassTemplate:
    class_name: str
    template_name: str | None
    file: Path


@dataclass
class ValidationIssue:
    level: str
    message: str


def normalize_slashes(value: str) -> str:
    return value.replace("\\", "/")


def make_module_relative(module_root: Path, path: Path) -> str:
    return normalize_slashes(str(path.resolve().relative_to(module_root.resolve())))


def parse_manifest(module_root: Path) -> dict:
    manifest_path = module_root / "__manifest__.py"
    try:
        content = manifest_path.read_text(encoding="utf-8")
        manifest = ast.literal_eval(content)
    except Exception as exc:  # pragma: no cover - surfaced to caller
        raise ValueError(f"failed to parse manifest {manifest_path}: {exc}") from exc
    if not isinstance(manifest, dict):
        raise ValueError(f"manifest {manifest_path} did not evaluate to a dict")
    return manifest


def resolve_asset_entry(module_root: Path, entry: str) -> list[Path]:
    module_name = module_root.name
    normalized = normalize_slashes(entry).strip()
    if normalized.startswith(f"{module_name}/"):
        normalized = normalized[len(module_name) + 1 :]
    pattern = module_root / normalized
    has_glob = any(char in normalized for char in "*?[")
    if has_glob:
        return [Path(item).resolve() for item in glob.glob(str(pattern), recursive=True)]
    if pattern.exists():
        return [pattern.resolve()]
    return []


def collect_manifest_assets(module_root: Path, bundle_name: str) -> tuple[list[str], set[str], list[str]]:
    manifest = parse_manifest(module_root)
    assets = manifest.get("assets", {})
    bundle_entries = assets.get(bundle_name, [])
    if not isinstance(bundle_entries, list):
        raise ValueError(f"bundle {bundle_name} is not a list in {module_root / '__manifest__.py'}")

    resolved_files: set[str] = set()
    missing_entries: list[str] = []
    raw_entries: list[str] = []

    for entry in bundle_entries:
        if not isinstance(entry, str):
            continue
        raw_entries.append(entry)
        files = resolve_asset_entry(module_root, entry)
        if files:
            resolved_files.update(make_module_relative(module_root, file) for file in files if file.is_file())
        else:
            missing_entries.append(entry)

    return raw_entries, resolved_files, missing_entries


def safe_xml_parse(xml_path: Path) -> ET.Element | None:
    try:
        return ET.parse(xml_path).getroot()
    except ET.ParseError:
        return None


def collect_client_action_tags(module_root: Path) -> list[ClientActionTag]:
    tags: list[ClientActionTag] = []
    for xml_path in sorted((module_root / "views").glob("*.xml")):
        root = safe_xml_parse(xml_path)
        if root is None:
            continue
        for record in root.findall(".//record[@model='ir.actions.client']"):
            tag_field = record.find("./field[@name='tag']")
            if tag_field is None or not (tag_field.text or "").strip():
                continue
            tags.append(
                ClientActionTag(
                    tag=(tag_field.text or "").strip(),
                    file=xml_path,
                    record_id=record.attrib.get("id"),
                )
            )
    return tags


def find_matching_brace(source: str, open_index: int) -> int:
    depth = 0
    in_single = False
    in_double = False
    in_template = False
    in_line_comment = False
    in_block_comment = False
    escape = False

    for index in range(open_index, len(source)):
        char = source[index]
        next_char = source[index + 1] if index + 1 < len(source) else ""

        if in_line_comment:
            if char == "\n":
                in_line_comment = False
            continue
        if in_block_comment:
            if char == "*" and next_char == "/":
                in_block_comment = False
            continue
        if in_single:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == "'":
                in_single = False
            continue
        if in_double:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_double = False
            continue
        if in_template:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == "`":
                in_template = False
            continue

        if char == "/" and next_char == "/":
            in_line_comment = True
            continue
        if char == "/" and next_char == "*":
            in_block_comment = True
            continue
        if char == "'":
            in_single = True
            continue
        if char == '"':
            in_double = True
            continue
        if char == "`":
            in_template = True
            continue
        if char == "{":
            depth += 1
            continue
        if char == "}":
            depth -= 1
            if depth == 0:
                return index

    return -1


def collect_js_metadata(
    module_root: Path,
    allowed_asset_files: set[str] | None = None,
) -> tuple[dict[str, list[RegistryRegistration]], dict[str, ClassTemplate]]:
    registry_map: dict[str, list[RegistryRegistration]] = defaultdict(list)
    class_map: dict[str, ClassTemplate] = {}

    class_pattern = re.compile(r"(?:export\s+)?class\s+([A-Za-z_$][\w$]*)[^{]*\{", re.MULTILINE)
    direct_add_pattern = re.compile(
        r"""registry\.category\(\s*["']actions["']\s*\)\.add\(\s*["']([^"']+)["']\s*,\s*([A-Za-z_$][\w$]*)""",
        re.MULTILINE,
    )
    alias_pattern = re.compile(
        r"""(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*registry\.category\(\s*["']actions["']\s*\)""",
        re.MULTILINE,
    )
    template_pattern = re.compile(r"""static\s+template\s*=\s*["']([^"']+)["']""", re.MULTILINE)

    for js_path in sorted((module_root / ACTION_DIR).glob("*.js")):
        rel_path = Path(make_module_relative(module_root, js_path))
        rel_path_text = normalize_slashes(str(rel_path))
        if allowed_asset_files is not None and rel_path_text not in allowed_asset_files:
            continue

        source = js_path.read_text(encoding="utf-8")

        aliases = set(alias_pattern.findall(source))
        for key, component in direct_add_pattern.findall(source):
            registry_map[key].append(RegistryRegistration(key=key, component=component, file=rel_path))
        for alias in aliases:
            alias_add_pattern = re.compile(
                rf"""\b{re.escape(alias)}\.add\(\s*["']([^"']+)["']\s*,\s*([A-Za-z_$][\w$]*)""",
                re.MULTILINE,
            )
            for key, component in alias_add_pattern.findall(source):
                registry_map[key].append(RegistryRegistration(key=key, component=component, file=rel_path))

        for match in class_pattern.finditer(source):
            class_name = match.group(1)
            brace_index = source.find("{", match.start())
            close_index = find_matching_brace(source, brace_index)
            body = source[brace_index + 1 : close_index] if close_index != -1 else source[brace_index + 1 :]
            template_match = template_pattern.search(body)
            class_map[class_name] = ClassTemplate(
                class_name=class_name,
                template_name=template_match.group(1) if template_match else None,
                file=rel_path,
            )

    return registry_map, class_map


def collect_xml_templates(module_root: Path) -> dict[str, list[Path]]:
    template_map: dict[str, list[Path]] = defaultdict(list)
    for xml_path in sorted((module_root / TEMPLATE_DIR).glob("*.xml")):
        root = safe_xml_parse(xml_path)
        if root is None:
            continue
        for element in root.iter():
            template_name = element.attrib.get("t-name")
            if template_name:
                template_map[template_name].append(Path(make_module_relative(module_root, xml_path)))
    return template_map


def format_path_list(paths: Iterable[Path | str]) -> str:
    values = [normalize_slashes(str(path)) for path in paths]
    return ", ".join(sorted(values))


def validate_module(module_root: Path, bundle_name: str) -> tuple[list[ValidationIssue], dict]:
    raw_assets, asset_files, missing_entries = collect_manifest_assets(module_root, bundle_name)
    js_assets = {asset for asset in asset_files if asset.endswith(".js")}
    xml_assets = {asset for asset in asset_files if asset.endswith(".xml")}
    client_tags = collect_client_action_tags(module_root)
    registry_map, class_map = collect_js_metadata(module_root, js_assets)
    template_map = collect_xml_templates(module_root)

    issues: list[ValidationIssue] = []

    if missing_entries:
        for entry in missing_entries:
            issues.append(ValidationIssue("warning", f"manifest asset entry did not match any file: {entry}"))

    for client_action in client_tags:
        registrations = registry_map.get(client_action.tag, [])
        action_source = make_module_relative(module_root, client_action.file)
        if not registrations:
            issues.append(
                ValidationIssue(
                    "error",
                    f'action tag "{client_action.tag}" from {action_source} has no JS registry registration',
                )
            )
            continue

        for registration in registrations:
            class_info = class_map.get(registration.component)
            if not class_info:
                issues.append(
                    ValidationIssue(
                        "error",
                        f'action key "{registration.key}" references component "{registration.component}" in {registration.file}, but the class was not found in scanned action JS files',
                    )
                )
                continue

            if not class_info.template_name:
                issues.append(
                    ValidationIssue(
                        "error",
                        f'action component "{registration.component}" in {class_info.file} has no static template',
                    )
                )
                continue

            template_files = template_map.get(class_info.template_name, [])
            if not template_files:
                issues.append(
                    ValidationIssue(
                        "error",
                        f'template "{class_info.template_name}" used by {registration.component} in {class_info.file} has no matching t-name in static/src/xml',
                    )
                )
                continue

            declared_template_files = [
                path for path in template_files if normalize_slashes(str(path)) in xml_assets
            ]
            if not declared_template_files:
                issues.append(
                    ValidationIssue(
                        "error",
                        f'template "{class_info.template_name}" exists in {format_path_list(template_files)}, but none of those XML files are declared in {bundle_name}',
                    )
                )

    for class_info in class_map.values():
        js_file = normalize_slashes(str(class_info.file))
        if js_file not in js_assets or not class_info.template_name:
            continue
        template_files = template_map.get(class_info.template_name, [])
        if not template_files:
            issues.append(
                ValidationIssue(
                    "error",
                    f'asset JS class "{class_info.class_name}" in {class_info.file} points to missing template "{class_info.template_name}"',
                )
            )
            continue
        if not any(normalize_slashes(str(path)) in xml_assets for path in template_files):
            issues.append(
                ValidationIssue(
                    "error",
                    f'asset JS class "{class_info.class_name}" in {class_info.file} uses template "{class_info.template_name}", but its XML file is not declared in {bundle_name}',
                )
            )

    details = {
        "raw_assets": raw_assets,
        "asset_files": asset_files,
        "js_assets": js_assets,
        "xml_assets": xml_assets,
        "client_tags": client_tags,
        "registry_map": registry_map,
        "class_map": class_map,
        "template_map": template_map,
    }
    return issues, details


def print_report(module_root: Path, bundle_name: str, issues: list[ValidationIssue], details: dict) -> None:
    client_tags: list[ClientActionTag] = details["client_tags"]
    registry_map: dict[str, list[RegistryRegistration]] = details["registry_map"]
    class_map: dict[str, ClassTemplate] = details["class_map"]
    template_map: dict[str, list[Path]] = details["template_map"]
    js_assets: set[str] = details["js_assets"]
    xml_assets: set[str] = details["xml_assets"]

    print(f"Module: {module_root}")
    print(f"Bundle: {bundle_name}")
    print(f"Manifest JS assets: {len(js_assets)}")
    print(f"Manifest XML assets: {len(xml_assets)}")
    print(f"Client action tags: {len(client_tags)}")
    print(f"Registry keys found: {len(registry_map)}")
    print(f"Action classes found: {len(class_map)}")
    print(f"Template names found: {len(template_map)}")
    print()
    print("Action chain summary:")

    for client_action in client_tags:
        registrations = registry_map.get(client_action.tag, [])
        if not registrations:
            print(f'  [MISSING] {client_action.tag} -> no registry registration')
            continue

        for registration in registrations:
            class_info = class_map.get(registration.component)
            template_name = class_info.template_name if class_info else None
            template_ok = bool(template_name and template_map.get(template_name))
            status = "OK" if class_info and template_ok else "CHECK"
            print(
                f"  [{status}] {client_action.tag} -> {registration.component}"
                f" -> {template_name or 'no static template'}"
            )

    print()
    errors = [issue for issue in issues if issue.level == "error"]
    warnings = [issue for issue in issues if issue.level == "warning"]
    print(f"Errors: {len(errors)}")
    for issue in errors:
        print(f"  - {issue.message}")
    print(f"Warnings: {len(warnings)}")
    for issue in warnings:
        print(f"  - {issue.message}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate an Odoo module's frontend action registry/template asset chain."
    )
    parser.add_argument(
        "module_path",
        nargs="?",
        default="custom_addons/logistics_web",
        help="Path to the target Odoo module directory",
    )
    parser.add_argument(
        "--bundle",
        default="web.assets_backend",
        help="Asset bundle name to validate (default: web.assets_backend)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    module_root = Path(args.module_path).resolve()

    if not module_root.exists():
        parser.error(f"module path does not exist: {module_root}")
    if not (module_root / "__manifest__.py").exists():
        parser.error(f"module path does not look like an Odoo module: {module_root}")

    try:
        issues, details = validate_module(module_root, args.bundle)
    except ValueError as exc:
        print(f"Validation setup failed: {exc}", file=sys.stderr)
        return 2

    print_report(module_root, args.bundle, issues, details)
    return 1 if any(issue.level == "error" for issue in issues) else 0


if __name__ == "__main__":
    raise SystemExit(main())
