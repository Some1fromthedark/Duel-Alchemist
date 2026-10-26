# Proposed patch: no tributes for normal summon/set (Junior Trials)

## Intent

Make the duel engine treat monsters as **not requiring advance tributes** for normal summon/set (level 5+ defaults), by forcing **`GetAdvanceSummonTributeCount`** to behave as if the card is in **tier 1** (no tribute requirement).

## Recommended approach (Duel-Alchemist compatible)

Replace each **5-byte** `CALL GetAdvanceSummonTributeCount` with **`mov eax, 1`**:

| Ghidra VA | Function context | Original bytes |
|-----------|------------------|----------------|
| `0x1800c3cca` | `CanIDoPutMonster` | `E8 51 01 00 00` |
| `0x18025b9b3` | `CheckNormalSummonWithoutTributePath` | `E8 68 84 E6 FF` |
| `0x180861feb` | `FUN_180861e60` | `E8 30 1E 86 FF` |

**Payload** (same as existing `payloads/payload_mov_1.txt`):

```text
B8 01 00 00 00
```

Duel-Alchemist will NOP-pad to the 5-byte instruction length (exact fit).

### Why this instead of patching `CanIDoPutMonster` everywhere?

- Only **3 sites**, low blast radius.
- Avoids the broad “always yes” behavior of the infinite-summon mod.
- Keeps **`CanIDoPutMonster`** honest for zone/lock/other restrictions while fixing tribute tier input.

### Alternative (not chosen initially)

- **NOP the `JGE`** at `0x18025b9ba` / `0x180861ff2` — still runs real tribute count logic elsewhere; prefer forcing `eax = 1` at the source.
- **Patch `GetAdvanceSummonTributeCount` body** to `mov eax,1; ret` — breaks stack frame prologue (`push rdi`; `sub rsp,0x20`); needs a longer rewrite.

## How to apply

From repo root (with `duel_.dll` backup in place per main README):

```bash
python duel_alchemist.py -c junior-trials/configs/config_no_tributes_normal_summon.json
```

## Config layout

See `junior-trials/configs/config_no_tributes_normal_summon.json` and `junior-trials/inputs/GetAdvanceSummonTributeCount_call_sites.tsv`.

## Test plan

1. Restore vanilla `duel_.dll` → patch → launch Master Duel offline / solo.
2. Deck with **level 5–8** normal monsters **without** tribute effects.
3. Confirm **Normal Summon** and **Set** appear and complete **without** tribute selection.
4. Regression: level 4 still works; locked zones / summon count / “cannot normal summon” cards still blocked.
5. If tribute prompt still appears **after** confirming summon, note the phase — we may need a second hook in summon **execution** (future doc).

## Risk

Game updates will move these VAs. Re-run xref collection on **`GetAdvanceSummonTributeCount`** (`0x1800c3e20`) after each `duel.dll` update.
