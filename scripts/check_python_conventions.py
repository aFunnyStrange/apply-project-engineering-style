#!/usr/bin/env python3
"""Check Python files for the user's deterministic source conventions."""

from __future__ import annotations

import ast
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Set, Union


EXCLUDED_DIRECTORY_NAMES = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
    "target",
    "venv",
}
PYDANTIC_V1_DECORATORS = {"root_validator", "validator"}


@dataclass(frozen=True)
class Violation:
    """Describe one convention violation."""

    path: Path
    line: int
    code: str
    message: str

    def render(self) -> str:
        """Render the violation in a tool-friendly format.

        Returns:
            A path, line, code, and message string.
        """
        return f"{self.path}:{self.line}: {self.code} {self.message}"


def _contains_pep604_union(annotation: ast.AST) -> bool:
    """Return whether an annotation contains PEP 604 union syntax.

    Args:
        annotation: Annotation syntax tree.

    Returns:
        True when the annotation contains a bitwise-or union expression.
    """
    return any(
        isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr)
        for node in ast.walk(annotation)
    )


def _iter_annotations(tree: ast.AST) -> Iterable[ast.AST]:
    """Yield annotation nodes from a Python syntax tree.

    Args:
        tree: Parsed Python syntax tree.

    Yields:
        Function, variable, and argument annotation nodes.
    """
    for node in ast.walk(tree):
        if isinstance(node, ast.arg) and node.annotation is not None:
            yield node.annotation
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.returns is not None:
                yield node.returns
        elif isinstance(node, ast.AnnAssign):
            yield node.annotation


def _node_name(node: ast.AST) -> Optional[str]:
    """Return a simple or dotted name represented by an expression.

    Args:
        node: Expression syntax tree.

    Returns:
        Dotted name when recognized, otherwise None.
    """
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = _node_name(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    return None


def _pydantic_base_model_names(tree: ast.Module) -> Set[str]:
    """Return local names that definitely refer to Pydantic BaseModel."""
    names = {"BaseModel", "pydantic.BaseModel"}
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module == "pydantic":
            for alias in node.names:
                if alias.name == "BaseModel":
                    names.add(alias.asname or alias.name)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "pydantic":
                    names.add(f"{alias.asname or alias.name}.BaseModel")
    return names


def _is_base_model_class(node: ast.ClassDef, base_model_names: Set[str]) -> bool:
    """Return whether a class directly names Pydantic BaseModel as a base.

    Args:
        node: Class definition syntax tree.
        base_model_names: Local names proven to refer to Pydantic BaseModel.

    Returns:
        True when a direct base resolves to a known Pydantic BaseModel name.
    """
    return any((_node_name(base) or "") in base_model_names for base in node.bases)


def _check_docstrings(tree: ast.Module, path: Path) -> List[Violation]:
    """Check module, class, function, and method docstrings.

    Args:
        tree: Parsed module syntax tree.
        path: Source path used in diagnostics.

    Returns:
        Missing-docstring violations.
    """
    violations: List[Violation] = []
    if not ast.get_docstring(tree):
        violations.append(Violation(path, 1, "PCS001", "missing module docstring"))
    for node in ast.walk(tree):
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            if not ast.get_docstring(node):
                kind = "class" if isinstance(node, ast.ClassDef) else "function or method"
                violations.append(
                    Violation(path, node.lineno, "PCS001", f"missing {kind} docstring")
                )
    return violations


def _check_pydantic_v2(tree: ast.Module, path: Path) -> List[Violation]:
    """Check for definite Pydantic v1 model patterns.

    Args:
        tree: Parsed module syntax tree.
        path: Source path used in diagnostics.

    Returns:
        Pydantic v1 compatibility violations.
    """
    violations: List[Violation] = []
    base_model_names = _pydantic_base_model_names(tree)
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == "pydantic":
            for alias in node.names:
                if alias.name in PYDANTIC_V1_DECORATORS:
                    violations.append(
                        Violation(
                            path,
                            node.lineno,
                            "PCS003",
                            f"use a Pydantic v2 validator instead of {alias.name}",
                        )
                    )
        if isinstance(node, ast.ClassDef) and _is_base_model_class(
            node, base_model_names
        ):
            for child in node.body:
                if isinstance(child, ast.ClassDef) and child.name == "Config":
                    violations.append(
                        Violation(
                            path,
                            child.lineno,
                            "PCS003",
                            "use model_config = ConfigDict(...) instead of nested class Config",
                        )
                    )
    return violations


def check_source(
    source: str,
    path: Union[Path, str] = "<memory>",
) -> List[Violation]:
    """Check one Python source string.

    Args:
        source: Python source text.
        path: Diagnostic path.

    Returns:
        Sorted convention violations.
    """
    source_path = Path(path)
    violations: List[Violation] = []
    try:
        tree = ast.parse(source)
    except SyntaxError as error:
        violations.append(
            Violation(
                source_path,
                error.lineno or 1,
                "PCS000",
                f"syntax error: {error.msg}",
            )
        )
        return violations

    violations.extend(_check_docstrings(tree, source_path))
    for annotation in _iter_annotations(tree):
        if _contains_pep604_union(annotation):
            violations.append(
                Violation(
                    source_path,
                    getattr(annotation, "lineno", 1),
                    "PCS002",
                    "use Union[...] or Optional[...] instead of PEP 604 union syntax",
                )
            )
    violations.extend(_check_pydantic_v2(tree, source_path))
    return sorted(violations, key=lambda item: (str(item.path), item.line, item.code))


def _is_excluded(path: Path) -> bool:
    """Return whether a path is inside an excluded directory.

    Args:
        path: Candidate source path.

    Returns:
        True when any path component is excluded.
    """
    return any(part in EXCLUDED_DIRECTORY_NAMES for part in path.parts)


def iter_python_files(paths: Sequence[Union[Path, str]]) -> Iterable[Path]:
    """Yield unique Python files beneath input paths.

    Args:
        paths: Files or directories to scan.

    Yields:
        Sorted, unique Python source paths.
    """
    discovered: Set[Path] = set()
    for raw_path in paths:
        path = Path(raw_path)
        if path.is_file() and path.suffix == ".py" and not _is_excluded(path):
            discovered.add(path)
        elif path.is_dir():
            discovered.update(
                candidate
                for candidate in path.rglob("*.py")
                if candidate.is_file() and not _is_excluded(candidate)
            )
    yield from sorted(discovered)


def check_paths(
    paths: Sequence[Union[Path, str]],
) -> List[Violation]:
    """Check all Python files under the supplied paths.

    Args:
        paths: Files or directories to scan.

    Returns:
        All convention violations.
    """
    violations: List[Violation] = []
    for path in iter_python_files(paths):
        try:
            source = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            violations.append(
                Violation(path, 1, "PCS004", f"cannot read UTF-8 source: {error}")
            )
            continue
        violations.extend(check_source(source, path))
    return violations


def main(arguments: Optional[Sequence[str]] = None) -> int:
    """Run the convention checker.

    Args:
        arguments: Optional file and directory arguments.

    Returns:
        Zero when all files pass, one for violations, or two when no files are found.
    """
    selected_arguments = list(arguments if arguments is not None else sys.argv[1:])
    selected_paths: List[Union[Path, str]] = selected_arguments or [Path.cwd()]
    python_files = list(iter_python_files(selected_paths))
    if not python_files:
        print("No Python files found in the supplied paths.", file=sys.stderr)
        return 2
    violations = check_paths(python_files)
    for violation in violations:
        print(violation.render())
    if violations:
        print(f"Found {len(violations)} convention violation(s).", file=sys.stderr)
        return 1
    print(f"Checked {len(python_files)} Python file(s); no convention violations found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
