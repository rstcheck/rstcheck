import os
from pathlib import Path

def test_path_resolve_works_on_windows(tmp_path: Path):
    p = tmp_path / "a" / "b.rst"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("title\n=====\n", encoding="utf-8")
    assert p.resolve().exists()
    # avoid assumptions that break on Windows drive letters
    assert os.path.isabs(str(p.resolve()))
