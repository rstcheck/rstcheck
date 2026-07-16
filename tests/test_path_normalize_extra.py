import os
from pathlib import Path

def test_path_join_is_stable():
    p = Path("a") / "b" / "c.rst"
    s = str(p)
    assert "c.rst" in s
    assert os.path.normpath(s)
