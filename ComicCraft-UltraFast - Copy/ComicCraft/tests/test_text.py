from app.utils.text import safe_filename, normalize_text

def test_safe_filename():
    name = safe_filename("Panel 1: Into the woods")
    assert name.endswith(".png")
    assert " " not in name
    assert ":" not in name

def test_normalize_text():
    assert normalize_text(" hello   world ") == "hello world"
