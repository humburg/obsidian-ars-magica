"""Basic smoke test to ensure environment and package are correctly configured."""

import obsidian_ars_magica


def test_package_version():
    assert obsidian_ars_magica.__version__ == "0.1.0"

