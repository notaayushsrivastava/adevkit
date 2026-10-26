import pytest
from adevkit.ui import BANNER_VARIATIONS, BANNER_ART, get_random_banner, print_banner

def test_banner_variations_exist():
    assert len(BANNER_VARIATIONS) == 5
    for banner in BANNER_VARIATIONS:
        assert isinstance(banner, str)
        assert len(banner.strip()) > 0
    # Check backwards compatibility
    assert BANNER_ART == BANNER_VARIATIONS[0]

def test_get_random_banner_explicit():
    for i in range(len(BANNER_VARIATIONS)):
        assert get_random_banner(i) == BANNER_VARIATIONS[i]

def test_get_random_banner_dynamic():
    banner = get_random_banner()
    assert banner in BANNER_VARIATIONS

def test_print_banner_runs(capsys):
    print_banner(variation=0)
    # Ensure it prints without throwing exceptions
