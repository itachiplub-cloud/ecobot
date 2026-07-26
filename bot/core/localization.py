from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


class Localization:
    def __init__(self, locale_dir: str = None):
        if locale_dir is None:
            locale_dir = str(Path(__file__).resolve().parent.parent.parent / "locales")
        self.locale_dir = Path(locale_dir)
        self._cache: dict[str, dict] = {}

    def _load(self, lang: str) -> dict:
        if lang in self._cache:
            return self._cache[lang]
        path = self.locale_dir / f"{lang}.yml"
        if not path.exists():
            if lang != "en":
                return self._load("en")
            return {}
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        self._cache[lang] = data
        return data

    def t(self, key: str, lang: str = "en", **kwargs) -> str:
        data = self._load(lang)
        keys = key.split(".")
        value = data
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                value = None
                break
        if value is None:
            if lang != "en":
                return self.t(key, "en", **kwargs)
            return key
        if isinstance(value, str) and kwargs:
            try:
                return value.format(**kwargs)
            except (KeyError, IndexError):
                return value
        return str(value)

    def reload(self) -> None:
        self._cache.clear()
