# Grid level catalog and scaling

The shipped catalog is every `.led` and `.ledb` archive below
`games/source`. As validated on 2026-07-22, it contains 109 archives:

- `-/`: 10
- `--/`: 15
- `---/`: 72, including the nested legacy collection
- `----/`: 12

Those archives contain 110 main gameplay boards. `-/010.led` is the one
multi-board archive: canonical board `0000122` (`跳跃15`) plus
`0000122/平行03` (`平行03`). The active 1P marathon selector uses 37 `.led`
files directly inside `-`, `--`, and `---`; those files contain 38 boards
because of `-/010.led`. The catalog validator is deliberately recursive so
dormant or legacy shipped archives cannot hide malformed data.

## Archive semantics

Each archive is a ZIP containing one or more Python `shelve` databases.
Every shelf whose `para_key_game.play_order` is false is a main gameplay
board. Board identity is its normalized subfolder path inside the archive.
Boards are ordered by that identity. The production raw loader selects the
first main board in this deterministic order (falling back to the first
readable auxiliary board only when an archive has no main board). A board
supplies:

- `para_key_game`: authored dimensions and the half-open active zone
  `[row_from,row_to) × [col_from,col_to)`.
- `dict_group`: `floor_light`, `wall_light`, and `screen_light` groups.
- `start_member`: `(row, col)` floor cells for `floor_light`; linear hardware
  indexes for true wall/screen groups.
- `activity_area`: half-open movement bounds.
- `start_time_sec` and `end_time_sec`: the group's active interval.
- `scale`: one of `both`, `row`, `col`, `none`, or the legacy alias
  `none2edge`.

`start_area` is not a hardware type. In particular, a `floor_light` with
`start_area=0` remains a floor group and must not be discarded as wall
hardware.

The headless defaults disable true `wall_light` and `screen_light` groups.
Floor groups are retained regardless of `start_area`.

## Production scaling

Before every attempt, the runtime reloads the raw archive and calls
`prepare_level_for_platform`. The configured default target is 16 rows × 26
columns.

- `both` scales row and column cell boundaries proportionally.
- `row` scales rows; columns retain authored size and are anchored/recentered.
- `col` scales columns; rows retain authored size and are anchored/recentered.
- `none` and `none2edge` retain authored cell size while anchoring/recentering
  both axes.
- Decimal `ROUND_HALF_UP` is used for boundaries. A non-empty source cell or
  range that would collapse during downscaling is kept non-empty.
- The game zone and every group activity range are transformed with the same
  boundary scaling. Prepared floor cells must be integer coordinates inside
  the target board.
- Preparation deep-copies the board and groups; raw archive objects are not
  mutated. Reloading and preparing the same archive must produce the same
  digest.

The valid portion of the current catalog includes authored boards sized
12×24, 15×26, 16×26, and 16×28. Encountered scale modes are `both`, `row`,
`col`, and `none`.

## Headless scoring semantics

The current Grid runtime recognizes blue `(0, 0, 254)` as P1 scoreable and
orange `(254, 128, 0)` as P2 scoreable. A prepared board containing both is
multiplayer. Plain red is a score/life hazard; deduct red consumes a tile and
deducts score without reducing life. Other floor colors are non-scoreable
decoration or safety indicators. Final score is not divided by players or
elapsed time.

## Catalog validation

Run:

```bash
python scripts/validate_level_catalog.py
python scripts/validate_level_catalog.py --strict
python scripts/validate_level_catalog.py --verbose
python scripts/validate_level_catalog.py --json
```

The default output is a summary plus detailed failures and known exclusions;
`--verbose` adds one metadata line per valid board, and JSON contains the
complete archive-plus-board report. `--rows` and `--cols` validate another
target size. Every main board is reloaded and prepared twice through production
code. The selected production board is also checked against the first
deterministic board identity.

The command exits nonzero for unexplained load errors, malformed or
out-of-bounds geometry, invalid group time ranges, invalid transformed zones,
empty retained floor geometry, absent production score colors on an expected
playable board, or nondeterministic output. Default mode reports the three
exact known nested-legacy exclusions below but exits zero if there are no
unexplained failures. `--strict` counts them as failures and exits nonzero.

The known-exclusion key is exact archive path + board identity + reason. A
renamed board or changed error cannot match:

- `---/---/JZDS002.led#JZDS0022` (`JZDS04`): no scoreable floor members. Its
  floor colors include `(88,88,211)`, yellow, magenta, and light gray, but no
  production blue/orange.
- `---/---/YC16.led#YC162` (`隐藏游戏16`): floor group `蓝色(1)` has reversed
  authored column activity bounds `(89,24)`.
- `---/---/ZZDK01.ledb#ZZ032` (`PD04`): floor group `绿色14(81)` has reversed
  activity times `(569.6,560.4)`.

All three archives live in nested `---/---` legacy content and are absent from
the production 37-file 1P sequence. The 2026-07-22 full 16×26 default run
processed 109 archives / 110 boards: 107 valid, 0 unexplained failures, and 3
known exclusions. The production sequence itself has 37 archives / 38 boards
and zero failures.
