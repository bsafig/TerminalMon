"""End-to-end tests driving the CLI against an isolated data directory."""
import json
import os

import pytest

from terminalmon import cli, storage


@pytest.fixture(autouse=True)
def isolated_home(tmp_path, monkeypatch):
    """Point TERMINALMON_HOME at a throwaway dir for every test."""
    monkeypatch.setenv("TERMINALMON_HOME", str(tmp_path))
    return tmp_path


def run(*argv):
    return cli.main(list(argv))


def test_new_sets_first_mon_as_buddy(capsys):
    assert run("new", "pikachu") == 0
    assert storage.get_buddy_name() == "pikachu"
    assert "set as your buddy" in capsys.readouterr().out


def test_new_duplicate_rejected():
    run("new", "pikachu")
    assert run("new", "pikachu") == 1


def test_xp_levels_up(capsys):
    run("new", "pikachu")
    capsys.readouterr()
    assert run("xp", "25") == 0
    out = capsys.readouterr().out
    assert "leveled up to level 2" in out
    data = storage.load_mon("pikachu")
    assert data["level"] == 2 and data["xp"] == 15


def test_learn_creates_move_script_and_forget_removes_it():
    run("new", "pikachu")
    run("learn", "thunder")
    assert storage.move_path("thunder").exists()
    assert "thunder" in storage.load_mon("pikachu")["moves"]
    run("forget", "thunder")
    assert not storage.move_path("thunder").exists()
    assert "thunder" not in storage.load_mon("pikachu")["moves"]


def test_forget_shared_move_keeps_script():
    run("new", "pikachu")
    run("learn", "thunder")
    run("new", "raichu")
    run("buddy", "raichu")
    run("learn", "thunder")
    run("forget", "thunder")  # raichu forgets, but pikachu still knows it
    assert storage.move_path("thunder").exists()


def test_rename_updates_buddy_pointer_and_name():
    run("new", "charmander")
    assert run("rename", "charmander", "charizard") == 0
    assert not storage.mon_exists("charmander")
    assert storage.get_buddy_name() == "charizard"
    assert storage.load_mon("charizard")["name"] == "charizard"


def test_release_refuses_buddy():
    run("new", "pikachu")
    assert run("release", "pikachu") == 1
    assert storage.mon_exists("pikachu")


def test_release_non_buddy():
    run("new", "pikachu")
    run("new", "eevee")
    assert run("release", "eevee") == 0
    assert not storage.mon_exists("eevee")


def test_use_unknown_move_fails():
    run("new", "pikachu")
    assert run("use", "surf") == 1


def test_hook_print_emits_snippet(capsys):
    assert run("hook", "print", "--shell", "bash") == 0
    assert "terminalmon_xp_tracker" in capsys.readouterr().out


def test_colors_suppressed_when_not_a_tty(capsys):
    # capsys stdout is not a tty, so no ANSI escapes should leak.
    run("new", "pikachu")
    run("stats")
    assert "\033[" not in capsys.readouterr().out


def test_data_file_is_valid_json():
    run("new", "pikachu")
    raw = (storage.mon_path("pikachu")).read_text(encoding="utf-8")
    data = json.loads(raw)
    assert data["name"] == "pikachu"
    assert data["moves"] == []


@pytest.mark.skipif(os.name == "nt", reason="POSIX shebang execution (Unix-only tool)")
def test_learned_move_script_executes(capfd):
    """A learned move's script actually runs (via its shebang) and produces output."""
    run("new", "pikachu")
    run("learn", "thunder")
    # Rewrite the script with a deterministic marker, then use the move.
    storage.move_path("thunder").write_text(
        "#!/bin/bash\necho MOVE_RAN_OK\n", encoding="utf-8", newline="\n"
    )
    assert run("use", "thunder") == 0
    assert "MOVE_RAN_OK" in capfd.readouterr().out
