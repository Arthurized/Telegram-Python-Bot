import re
from unittest.mock import patch
import pytest
from bot import services


@patch("bot.services.wikipedia.summary")
@patch("bot.services.wikipedia.page")
def test_search_wikipedia_success(mock_page, mock_summary):
    mock_page.return_value.title = "Python (programming language)"
    mock_summary.return_value = "Python is a programming language."
    result = services.search_wikipedia("Python")
    assert result is not None
    assert "Python" in result


def test_get_ny_time_format():
    time_str = services.get_ny_time()
    assert re.match(r"\d{2}:\d{2}:\d{2}", time_str)


def test_get_current_date_format():
    date_str = services.get_current_date()
    assert re.match(r"\d{2}-\d{2}-\d{4}", date_str)


def test_random_fallback_sticker():
    stickers = ["a", "b", "c"]
    result = services.random_fallback_sticker(stickers)
    assert result in stickers
