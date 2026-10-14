"""
Страховка от утечки: ни один файл под git не должен содержать сессию Telethon,
api_hash или заполненные секреты. Запускается в `make test` и в pre-commit.
"""

import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]

PATTERNS = {
    "строка сессии Telethon": re.compile(r"\b1[A-Za-z0-9_-]{300,}={0,2}"),
    # [ \t] вместо \s: пустое значение не должно склеиваться со следующей строкой
    "заполненный секрет в env": re.compile(r"^[ \t]*TG_(API_HASH|SESSION)[ \t]*=[ \t]*[^\s#]", re.MULTILINE),
    "api_hash в коде": re.compile(r"(?i)api_hash\s*[=:]\s*['\"][0-9a-f]{32}['\"]"),
    "номер телефона": re.compile(r"\+7\d{10}\b"),
}
# Файлы, где шаблоны встречаются намеренно: сам этот тест и тесты-примеры
ALLOWED = {
    "tests/unit/test_no_secrets.py",
    "tests/unit/settings/test_settings.py",
    "tests/unit/core/bots/test_service.py",
}


def tracked_files() -> list[str]:
    try:
        result = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        pytest.skip("не git-репозиторий")
    return [name for name in result.stdout.decode().split("\0") if name]


def test_secrets_file_is_ignored_by_git():
    result = subprocess.run(["git", "check-ignore", "-q", ".env.local"], cwd=ROOT, check=False)
    assert result.returncode == 0, ".env.local должен быть в .gitignore"


def test_tracked_files_contain_no_secrets():
    leaks = []
    for name in tracked_files():
        if name in ALLOWED:
            continue
        try:
            text = (ROOT / name).read_text(encoding="utf-8")
        except (UnicodeDecodeError, FileNotFoundError):
            continue
        leaks += [f"{name}: {kind}" for kind, pattern in PATTERNS.items() if pattern.search(text)]
    assert not leaks, f"похоже на секреты в файлах под git: {leaks}"


@pytest.mark.parametrize(
    ("text", "leaks"),
    [
        ("TG_API_HASH=\n# комментарий\nTG_SESSION=\n", False),
        ("TG_API_HASH=   # пусто\n", False),
        ("TG_API_HASH=0123456789abcdef0123456789abcdef\n", True),
        ("  TG_SESSION=1AbC\n", True),
    ],
)
def test_env_secret_pattern(text, leaks):
    assert bool(PATTERNS["заполненный секрет в env"].search(text)) is leaks
