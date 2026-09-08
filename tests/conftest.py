"""Offline contract-pin suite for everything outside RussianTranslation/ (H4353).

Ground rules enforced HERE, not per test:

* **No network.** ``socket`` connections and ``urllib.request.urlopen`` are
  replaced at collection time with functions that raise. A test that reaches
  the network fails loudly instead of silently passing on a warm cache.
* **No external mirrors.** Every environment variable the modules under test
  read for an outside data root (``CSL_ORIG_V02``, ``PWG_INPUT_DIR``,
  ``DCS_LEMMA_SUMMARY``, ``SSC_DIR``, ...) is pointed at a directory that
  does not exist, so a module that "helpfully" falls back to the sibling
  checkout reads nothing. Fixtures live under ``tests/fixtures`` only.
* **No history walks.** The clone is shallow (grafted 06-08-2026); nothing in
  this suite runs ``git log``.

Module loading helpers:

* :func:`load_module` imports a script by path under a unique module name
  (sibling imports such as ``import huet_coverage as huet`` keep working
  because the script's own directory is put on ``sys.path``).
* :func:`load_defs` is for scripts that execute their whole analysis at
  module level (``Catalan-Pujol/accent_compare.py`` and friends): it keeps
  only imports, constant assignments and ``def``/``class`` blocks, so the
  pure functions can be pinned without running the analysis.
"""
from __future__ import annotations

import ast
import importlib
import importlib.util
import os
import socket
import sys
import types
import urllib.request
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
FIXTURES = Path(__file__).resolve().parent / "fixtures"
NOWHERE = str(Path(__file__).resolve().parent / "_nonexistent_external_root")

# ---------------------------------------------------------------- environment
# Every external root the modules under test can read. Each is pointed at a
# path that does not exist BEFORE any of them is imported.
_EXTERNAL_ENV = (
    "CSL_ORIG_V02", "PWG_INPUT_DIR", "DCS_LEMMA_SUMMARY", "SSC_DIR", "KOSHA_FREQ",
    "HERITAGE_MIRROR_DATA", "DCS_FULL_SQLITE", "CORPUS_LEXICON_JSONL",
    "ACC_TXT", "NCC_TXT", "PD_TXT", "PWG_DATA_ROOT",
)
for _var in _EXTERNAL_ENV:
    os.environ[_var] = NOWHERE


def _resolve_sanskrit_util() -> None:
    """Make ``sanskrit_util`` importable: pip-installed first, sibling checkout second."""
    try:
        importlib.import_module("sanskrit_util")
        return
    except ImportError:
        pass
    candidates = [os.environ.get("SANSKRIT_UTIL_PY"),
                  str(REPO.parent / "sanskrit-util" / "py")]
    for cand in candidates:
        if cand and Path(cand, "sanskrit_util").is_dir():
            sys.path.insert(0, cand)
            os.environ["SANSKRIT_UTIL_PY"] = cand
            importlib.import_module("sanskrit_util")
            return
    pytest.exit("sanskrit_util is not importable: pip install "
                "'sanskrit-util @ git+https://github.com/sanskrit-lexicon/sanskrit-util"
                "#subdirectory=py' or set SANSKRIT_UTIL_PY", returncode=3)


_resolve_sanskrit_util()
# The scripts insert os.environ["SANSKRIT_UTIL_PY"] (default: a Windows path)
# into sys.path; make that a real, harmless value.
os.environ.setdefault("SANSKRIT_UTIL_PY", NOWHERE)


# -------------------------------------------------------------------- network
class NetworkDisabled(RuntimeError):
    """Raised by any attempt to open a socket or URL while the suite runs."""


def _no_network(*_a, **_k):
    raise NetworkDisabled("offline suite: network access is disabled (H4353)")


socket.socket.connect = _no_network          # type: ignore[assignment]
socket.socket.connect_ex = _no_network       # type: ignore[assignment]
socket.create_connection = _no_network       # type: ignore[assignment]
urllib.request.urlopen = _no_network         # type: ignore[assignment]
urllib.request.urlretrieve = _no_network     # type: ignore[assignment]


# ------------------------------------------------------------- module loading
_LOADED: dict[str, types.ModuleType] = {}


def load_module(rel: str) -> types.ModuleType:
    """Import ``<repo>/<rel>`` as a fresh module under a collision-free name."""
    path = REPO / rel
    if rel in _LOADED:
        return _LOADED[rel]
    name = "h4353_" + rel.replace("/", "_").replace("-", "_").removesuffix(".py")
    here = str(path.parent)
    if here not in sys.path:
        sys.path.insert(0, here)
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    _LOADED[rel] = mod
    return mod


_SAFE_CALLS = {
    "re.compile", "set", "frozenset", "dict", "list", "tuple", "chr", "str", "int",
    "os.path.join", "os.path.dirname", "os.path.abspath", "os.path.normpath",
    "os.environ.get", "Path", "range", "sorted", "len", "zip", "enumerate",
    "defaultdict", "Counter", "unicodedata.lookup", "enumerate",
}


def _call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return _call_name(node.value) + "." + node.attr
    return "?"


def _is_constant_expr(node: ast.AST) -> bool:
    """True when evaluating ``node`` cannot read a file or run the analysis."""
    for sub in ast.walk(node):
        if isinstance(sub, ast.Call) and _call_name(sub.func) not in _SAFE_CALLS:
            if isinstance(sub.func, ast.Attribute) and isinstance(sub.func.value, ast.Constant):
                continue               # "literal".split() and friends
            return False
        if isinstance(sub, (ast.Await, ast.Yield, ast.YieldFrom)):
            return False
    return True


def load_defs(rel: str) -> types.ModuleType:
    """Load only the definitions of a module-level-executing script.

    Kept: ``import``/``from … import``, ``def``, ``class``, and assignments
    whose right-hand side is a constant expression (a literal, a
    ``re.compile``, an ``os.path.join`` …). Dropped: everything else — the
    ``for`` loops, ``print`` calls and ``open()`` reads that make up the
    script's analysis body.
    """
    path = REPO / rel
    key = rel + "::defs"
    if key in _LOADED:
        return _LOADED[key]
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    kept: list[ast.stmt] = []
    import builtins
    defined: set[str] = set(dir(builtins)) | {"__file__", "__name__", "__doc__"}
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module == "__future__":
            kept.append(node)          # must stay first and unwrapped
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            # Tolerate an absent optional dependency (nltk, rapidfuzz, git_ops):
            # the functions under test do not need it, only the analysis body did.
            for alias in node.names:
                defined.add((alias.asname or alias.name).split(".")[0])
            guarded = ast.Try(body=[node], handlers=[ast.ExceptHandler(
                type=ast.Name("ImportError", ast.Load()), name=None, body=[ast.Pass()])],
                orelse=[], finalbody=[])
            ast.copy_location(guarded, node)
            ast.fix_missing_locations(guarded)
            kept.append(guarded)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            defined.add(node.name)
            kept.append(node)
        elif isinstance(node, (ast.Assign, ast.AnnAssign)) and _is_constant_expr(node):
            value = node.value
            if value is None:
                continue
            loads = {n.id for n in ast.walk(value) if isinstance(n, ast.Name)
                     and isinstance(n.ctx, ast.Load)}
            if not loads <= defined:
                continue  # depends on a result of the dropped analysis body
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for t in targets:
                defined |= {n.id for n in ast.walk(t) if isinstance(n, ast.Name)}
            kept.append(node)
    tree.body = kept
    name = "h4353_defs_" + rel.replace("/", "_").replace("-", "_").removesuffix(".py")
    mod = types.ModuleType(name)
    mod.__file__ = str(path)
    here = str(path.parent)
    if here not in sys.path:
        sys.path.insert(0, here)
    sys.modules[name] = mod
    exec(compile(tree, str(path), "exec"), mod.__dict__)
    _LOADED[key] = mod
    return mod


def read_lines(rel: str) -> list[str]:
    """Committed list lines, BOM-tolerant, without the trailing empty element."""
    data = (REPO / rel).read_bytes()
    text = data.decode("utf-8-sig")
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    return lines


@pytest.fixture(scope="session")
def repo() -> Path:
    return REPO


@pytest.fixture(scope="session")
def fixtures() -> Path:
    return FIXTURES


@pytest.fixture(scope="session")
def su():
    import sanskrit_util
    return sanskrit_util
