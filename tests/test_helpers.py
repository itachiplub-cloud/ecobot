import pytest
from bot.utils.helpers import (
    format_number, progress_bar, seconds_to_human,
    calc_damage, clamp, percentage, xp_for_level,
    escape_html, rarity_emoji, generate_id,
)


def test_format_number():
    assert format_number(500) == "500"
    assert format_number(1500) == "1.5K"
    assert format_number(1500000) == "1.5M"
    assert format_number(1500000000) == "1.5B"


def test_progress_bar():
    bar = progress_bar(5, 10, 10)
    assert "█" in bar
    assert "░" in bar
    assert len(bar) == 10


def test_seconds_to_human():
    assert seconds_to_human(60) == "1m"
    assert seconds_to_human(3661) == "1h 1m 1s"
    assert seconds_to_human(86400) == "1d"


def test_clamp():
    assert clamp(5, 0, 10) == 5
    assert clamp(-5, 0, 10) == 0
    assert clamp(15, 0, 10) == 10


def test_percentage():
    assert percentage(50, 100) == 50.0
    assert percentage(0, 100) == 0.0
    assert percentage(1, 0) == 0.0


def test_xp_for_level():
    assert xp_for_level(1) == 100
    assert xp_for_level(2) == 150


def test_escape_html():
    assert escape_html("<b>") == "&lt;b&gt;"
    assert escape_html("a & b") == "a &amp; b"


def test_rarity_emoji():
    assert rarity_emoji("common") == "⚪"
    assert rarity_emoji("legendary") == "🟠"
    assert rarity_emoji("unknown") == "⚪"


def test_generate_id():
    id1 = generate_id()
    id2 = generate_id()
    assert len(id1) == 8
    assert id1 != id2
