import pytest
from pathlib import Path
import tempfile
import yaml


def test_load_locale():
    from bot.core.localization import Localization
    with tempfile.TemporaryDirectory() as tmpdir:
        locale_file = Path(tmpdir) / "en.yml"
        locale_file.write_text("test:\n  hello: 'Hello {name}'\n")
        loc = Localization(tmpdir)
        result = loc.t("test.hello", "en", name="World")
        assert result == "Hello World"


def test_missing_key():
    from bot.core.localization import Localization
    with tempfile.TemporaryDirectory() as tmpdir:
        locale_file = Path(tmpdir) / "en.yml"
        locale_file.write_text("test:\n  hello: 'Hello'\n")
        loc = Localization(tmpdir)
        result = loc.t("test.nonexistent", "en")
        assert result == "test.nonexistent"


def test_missing_language_fallback():
    from bot.core.localization import Localization
    with tempfile.TemporaryDirectory() as tmpdir:
        locale_file = Path(tmpdir) / "en.yml"
        locale_file.write_text("test:\n  hello: 'Hello'\n")
        loc = Localization(tmpdir)
        result = loc.t("test.hello", "fr")
        assert result == "Hello"
