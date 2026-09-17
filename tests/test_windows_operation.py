from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_windows_entry_point_is_portable_and_loopback_only() -> None:
    script = (ROOT / "scripts" / "start-local.ps1").read_text(encoding="utf-8")

    assert "$PSScriptRoot" in script
    assert ".venv\\Scripts\\python.exe" in script
    assert '"3.13.15"' in script
    assert "127.0.0.1:$Port" in script
    assert "0.0.0.0" not in script
    assert "--noreload" in script
    assert "manage.py migrate" not in script
    assert "backup_sqlite" not in script


def test_explorer_wrapper_uses_local_execution_policy_only() -> None:
    wrapper = (ROOT / "scripts" / "start-local.cmd").read_text(encoding="utf-8")

    assert "%~dp0" in wrapper
    assert "-NoProfile -ExecutionPolicy Bypass -File" in wrapper
    assert "start-local.ps1" in wrapper


def test_windows_guide_preserves_s5_s6_and_update_boundaries() -> None:
    guide = (ROOT / "docs" / "V0.4_S7_Operacao_Windows.md").read_text(encoding="utf-8")

    assert "exit `0` saudável, `2` findings impeditivos e `3` falha" in guide
    assert "destino novo e isolado" in guide
    assert "nunca substitui o banco principal" in guide
    assert "git reset --hard" in guide
