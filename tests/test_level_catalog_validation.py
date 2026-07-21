"""Focused tests for the shipped level-catalog validator."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts import validate_level_catalog as validator


def _game(**overrides):
    values = {
        "name": "fixture",
        "row": 4,
        "col": 5,
        "zone_row_from": 0,
        "zone_row_to": 4,
        "zone_col_from": 0,
        "zone_col_to": 5,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def _group(**overrides):
    values = {
        "name": "blue",
        "type": "floor_light",
        "start_member": {(0, 0), (3, 4)},
        "activity_area": [(0, 4), (0, 5)],
        "start_time_sec": 0,
        "end_time_sec": 10,
        "scale": "both",
        "start_area": 0,
        "color": [(0, 0, 0), (0, 0, 254), (0, 0, 0)],
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def test_discovery_is_recursive_filtered_and_deterministic(tmp_path):
    source = tmp_path / "games" / "source"
    (source / "b").mkdir(parents=True)
    (source / "a").mkdir()
    for relative in ("b/2.ledb", "a/1.led", "a/ignore.txt"):
        path = source / relative
        path.write_bytes(b"fixture")

    assert validator.discover_level_archives(source) == [
        source / "a/1.led",
        source / "b/2.ledb",
    ]


def test_archive_is_reloaded_prepared_twice_and_reports_required_metadata(monkeypatch):
    calls = []

    def load(path):
        calls.append(Path(path))
        return {
            "blue": _group(),
            "wall": _group(
                name="wall",
                type="wall_light",
                start_member=[0],
                start_area=1,
                color=[(0, 0, 0)] * 3,
            ),
            "screen": _group(
                name="screen",
                type="screen_light",
                start_member=[0],
                start_area=2,
                color=[(0, 0, 0)] * 3,
            ),
        }, _game()

    def prepare(groups, game, **options):
        assert options == {
            "target_rows": 16,
            "target_cols": 26,
            "enable_wall_light": False,
            "enable_screen_light": False,
        }
        return {"blue": groups["blue"]}, _game(
            row=16,
            col=26,
            zone_row_to=16,
            zone_col_to=26,
        )

    monkeypatch.setattr(validator, "_load_level_file", load)
    monkeypatch.setattr(validator, "prepare_level_for_platform", prepare)

    report = validator.validate_archive(Path("fixture.led"))

    assert calls == [Path("fixture.led"), Path("fixture.led")]
    assert report["authored_dimensions"] == [4, 5]
    assert report["scale_modes"] == ["both"]
    assert report["transformed_bounds"] == {
        "row_min": 0,
        "row_max": 3,
        "col_min": 0,
        "col_max": 4,
    }
    assert report["retained_floor_groups"] == 1
    assert report["retained_floor_members"] == 2
    assert report["ignored_wall_groups"] == 1
    assert report["ignored_screen_groups"] == 1
    assert report["scoreable_groups"] == 1
    assert report["scoreable_members"] == 2
    assert report["p1_colors"] == [[0, 0, 254]]
    assert report["p2_colors"] == []
    assert report["multiplayer"] is False
    assert report["zone"] == [0, 16, 0, 26]
    assert len(report["digest"]) == 64


def test_start_area_zero_floor_group_is_not_counted_as_wall(monkeypatch):
    groups = {"floor": _group(start_area=0)}
    monkeypatch.setattr(validator, "_load_level_file", lambda path: (groups, _game()))
    monkeypatch.setattr(
        validator,
        "prepare_level_for_platform",
        lambda groups, game, **options: (groups, game),
    )

    report = validator.validate_archive(Path("floor.led"))

    assert report["retained_floor_groups"] == 1
    assert report["ignored_wall_groups"] == 0


def test_catalog_collects_detailed_failures_and_continues(monkeypatch, tmp_path):
    good = tmp_path / "good.led"
    bad = tmp_path / "bad.ledb"
    good.touch()
    bad.touch()
    monkeypatch.setattr(
        validator,
        "discover_level_archives",
        lambda source: [bad, good],
    )

    def validate(path, **options):
        if path == bad:
            return {
                "reports": [],
                "failures": [{
                    "path": str(path),
                    "board": "board-a",
                    "board_name": "broken",
                    "error": "non-integer floor member in group 'broken'",
                }],
                "board_count": 1,
            }
        return {
            "reports": [{"path": str(path), "board": "board-b", "digest": "a" * 64}],
            "failures": [],
            "board_count": 1,
        }

    monkeypatch.setattr(validator, "validate_archive_boards", validate)

    result = validator.validate_catalog(tmp_path)

    assert result["processed"] == 2
    assert result["valid"] == 1
    assert result["failed"] == 1
    assert result["failures"][0]["path"] == str(bad)
    assert result["failures"][0]["board"] == "board-a"
    assert result["failures"][0]["error"] == (
        "non-integer floor member in group 'broken'"
    )


def test_rejects_nondeterministic_prepared_output(monkeypatch):
    count = 0

    monkeypatch.setattr(
        validator, "_load_level_file", lambda path: ({"blue": _group()}, _game())
    )

    def prepare(groups, game, **options):
        nonlocal count
        count += 1
        groups["blue"].start_member = {(count, 0)}
        return groups, game

    monkeypatch.setattr(validator, "prepare_level_for_platform", prepare)

    try:
        validator.validate_archive(Path("unstable.led"))
    except validator.CatalogValidationError as error:
        assert "nondeterministic" in str(error)
    else:
        raise AssertionError("nondeterministic output was accepted")


def test_rejects_invalid_time_range_before_preparation(monkeypatch):
    groups = {"bad": _group(start_time_sec=11, end_time_sec=10)}
    monkeypatch.setattr(validator, "_load_level_file", lambda path: (groups, _game()))

    try:
        validator.validate_archive(Path("bad-time.led"))
    except validator.CatalogValidationError as error:
        assert "activity time range" in str(error)
        assert "blue" in str(error)
    else:
        raise AssertionError("invalid activity time range was accepted")


def test_default_cli_is_concise_but_verbose_mode_prints_per_file(
    monkeypatch, capsys, tmp_path
):
    result = {
        "processed": 1,
        "valid": 1,
        "failed": 0,
        "reports": [
            {
                "path": "games/source/-/001.led",
                "authored_dimensions": [16, 26],
                "retained_floor_groups": 2,
                "retained_floor_members": 20,
                "scoreable_groups": 1,
                "scoreable_members": 10,
                "digest": "a" * 64,
            }
        ],
        "failures": [],
    }
    monkeypatch.setattr(validator, "validate_catalog", lambda *args, **kwargs: result)

    assert validator.main(["--source", str(tmp_path)]) == 0
    concise = capsys.readouterr()
    assert (
        "Validated 1 archive(s), 1 board(s): "
        "1 valid, 0 failed, 0 known legacy exclusion(s)."
    ) in concise.out
    assert "games/source/-/001.led" not in concise.out

    assert validator.main(["--source", str(tmp_path), "--verbose"]) == 0
    verbose = capsys.readouterr()
    assert "OK games/source/-/001.led" in verbose.out


def test_level_010_discovers_both_main_boards_in_stable_order():
    boards = validator.discover_main_gameplay_boards(
        validator.ROOT / "games/source/-/010.led"
    )

    assert [(board.identity, board.game.name) for board in boards] == [
        ("0000122", "跳跃15"),
        ("0000122/平行03", "平行03"),
    ]


def test_level_010_reports_both_board_identities():
    result = validator.validate_archive_boards(
        validator.ROOT / "games/source/-/010.led"
    )

    assert result["failures"] == []
    assert [
        (report["board"], report["board_name"]) for report in result["reports"]
    ] == [
        ("0000122", "跳跃15"),
        ("0000122/平行03", "平行03"),
    ]


def test_malformed_archive_is_an_unexplained_failure(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "broken.led").write_bytes(b"not a zip archive")

    result = validator.validate_catalog(source)

    assert result["processed_archives"] == 1
    assert result["processed_boards"] == 0
    assert result["failed"] == 1
    assert result["known_excluded"] == 0
    assert "main gameplay board" in result["failures"][0]["error"]


@pytest.mark.parametrize(
    ("groups", "message"),
    (
        ({}, "empty group mapping"),
        ({"wall": _group(type="wall_light", start_member=[0])}, "no retained floor groups"),
        ({"decor": _group(color=[(0, 0, 0)] * 3)}, "no scoreable floor members"),
    ),
)
def test_rejects_empty_no_floor_and_no_scoreable_boards(
    monkeypatch, groups, message
):
    monkeypatch.setattr(
        validator,
        "_load_level_file",
        lambda path: (groups, _game()),
    )

    with pytest.raises(validator.CatalogValidationError, match=message):
        validator.validate_archive(Path("invalid.led"))


def test_rejects_reversed_activity_geometry(monkeypatch):
    groups = {"bad": _group(activity_area=[(0, 4), (4, 2)])}
    monkeypatch.setattr(validator, "_load_level_file", lambda path: (groups, _game()))

    with pytest.raises(validator.CatalogValidationError, match=r"activity_area.*ordered"):
        validator.validate_archive(Path("bad-geometry.led"))


def test_known_legacy_exclusion_is_visible_and_strict_controls_exit(monkeypatch, capsys):
    result = {
        "processed_archives": 1,
        "processed_boards": 1,
        "valid": 0,
        "failed": 0,
        "known_excluded": 1,
        "reports": [],
        "failures": [],
        "known_exclusions": [
            {
                "path": "games/source/---/---/YC16.led",
                "board": "YC162",
                "error": "exact malformed geometry",
            }
        ],
    }
    monkeypatch.setattr(validator, "validate_catalog", lambda *args, **kwargs: result)

    assert validator.main([]) == 0
    default = capsys.readouterr()
    assert "1 known legacy exclusion" in default.out
    assert "YC162" in default.err

    assert validator.main(["--strict"]) == 1
    strict = capsys.readouterr()
    assert "YC162" in strict.err


def test_cli_returns_nonzero_for_unexplained_failure(monkeypatch, capsys):
    result = {
        "processed_archives": 1,
        "processed_boards": 1,
        "valid": 0,
        "failed": 1,
        "known_excluded": 0,
        "reports": [],
        "known_exclusions": [],
        "failures": [
            {
                "path": "games/source/-/bad.led",
                "board": "main",
                "error": "malformed geometry",
            }
        ],
    }
    monkeypatch.setattr(validator, "validate_catalog", lambda *args, **kwargs: result)

    assert validator.main([]) == 1
    output = capsys.readouterr()
    assert "games/source/-/bad.led#main: malformed geometry" in output.err
