# Tribute requirement investigation (`duel.dll`)

Analysis date: current `duel.dll` from Master Duel (Steam path loaded in Ghidra).

## Goal

Find where the engine decides that a **normal summon or set** requires **tributes** for high-level monsters, so Junior Trials can disable that requirement without breaking unrelated logic.

## Executive summary

Tribute need for normal summon/set is **not** a single `if (level >= 5)` check in one place. The engine:

1. Computes a **tribute tier** (values **1**, **2**, or **3**) per card via **`GetAdvanceSummonTributeCount`** (`0x1800c3e20`), using card/effect script tables (effect IDs such as `0x4862`, `0x1c33`, `0x1d20`, `0x40b1`), not a raw level compare in this function.
2. Gates normal summon validation in **`CheckNormalSummonWithoutTributePath`** (`0x18025b970`): if required tier **`>= 2`**, it **skips** the “no-tribute” fast path and returns failure to the orchestrator unless another path succeeds.
3. Exposes placement eligibility through **`CanIDoPutMonster`** (`0x1800c3cb0`, export **`DLL_DuelCanIDoPutMonster`** → `JMP 0x1800c3cb0`), which also calls **`GetAdvanceSummonTributeCount`** and folds the result into its return value.

The practical hook for “treat high-level monsters like level 4 for tribute purposes” is to **stop callers from seeing tribute tiers ≥ 2**—either by patching the **`CALL GetAdvanceSummonTributeCount`** sites to **`mov eax, 1`**, or by inverting the **`JGE`** branches that reject the no-tribute path.

## Key functions

| VA | Name (renamed in Ghidra) | Role |
|----|--------------------------|------|
| `0x180ea9eb0` | `DLL_DuelCanIDoPutMonster` | Export thunk → `CanIDoPutMonster` |
| `0x1800c3cb0` | `CanIDoPutMonster` | “Can this monster be normal summoned/set here?” (~206 call sites in this build) |
| `0x1800c3e20` | `GetAdvanceSummonTributeCount` | Returns tribute **tier** in `EAX` (1 = no advance tribute required, 2+ = needs tribute flow) |
| `0x18025b970` | `CheckNormalSummonWithoutTributePath` | Compares tier to threshold; either runs **`0x1800c7250`** (core summon check) or fails early |
| `0x1800c7250` | (wrapper) | Calls **`0x1800c7270`** — main summon permission logic |
| `0x1806d0f80` | `ValidateMonsterSummonAction` | C++-style validation chain; invokes tribute gate via vtable slot `@ 0x18025b970` |
| `0x180861e60` | `FUN_180861e60` | Second consumer of tribute tier (`CALL` + **`JGE`**) |

### `GetAdvanceSummonTributeCount` (`0x1800c3e20`)

- **Only three direct callers** in this binary (good for a minimal patch):
  - `0x1800c3cca` — inside `CanIDoPutMonster`
  - `0x18025b9b3` — inside `CheckNormalSummonWithoutTributePath`
  - `0x180861feb` — inside `FUN_180861e60`
- Walks duel work memory + per-card effect records to determine tribute tier.
- Early exit returns **`0x32`** in special duel states (do not break this without testing).

### `CheckNormalSummonWithoutTributePath` (`0x18025b970`)

Critical sequence:

```text
18025b9b3  CALL  GetAdvanceSummonTributeCount   ; EAX = tier
18025b9b8  CMP   EAX, EBX                       ; EBX is 2, or 3 for some card text IDs
18025b9ba  JGE   fail_path                      ; tier >= 2 → do not use no-tribute path
18025b9bf  MOV   EDX, 1
18025b9c6  CALL  0x1800c7250                    ; try normal summon permission
```

Interpretation: for tier **1**, the engine attempts normal summon through the standard checker; for tier **≥ 2**, it **bails out** (`EAX = 0`) so the UI/rules demand tributes.

### `ValidateMonsterSummonAction` (`0x1806d0f80`)

Uses **`0x180240720`** as a dispatcher (vtable / callback list). Relevant handlers registered at:

- `0x18024f780` — check with `R8 = 2`
- `0x18024f7c0` — check with `R8 = 1`
- **`0x18025b970`** — tribute path gate (calls **`CheckNormalSummonWithoutTributePath`** at `0x1806d106d`)
- `0x1802745c0` — follow-on check

Flow fragment:

```text
1806d106d  CALL  CheckNormalSummonWithoutTributePath
1806d1072  TEST  EAX, EAX
1806d1074  JZ    overall_fail
```

So the tribute gate must return **non-zero** for high-level normal summons to proceed in this chain.

### `CanIDoPutMonster` vs infinite-summon example mod

The shipped **infinite normal summons** mod patches **many** `CanIDoPutMonster` call sites to **`mov eax, 1`**. That forces “yes” everywhere and is broader than Junior Trials needs.

For **no tributes only**, prefer patching **`GetAdvanceSummonTributeCount` call sites** (3 locations) so tier stays **1** while other `CanIDoPutMonster` semantics remain.

## Strings / exports

- String **`TRIBUTESUMMONED`** @ `0x1811a9608` — referenced from `FUN_180593cc0` (summon state / logging, not the main tier calculator).
- No exported symbol named “Tribute”; **`DLL_DuelCanIDoPutMonster`** and **`DLL_DuelCanIDoSummonMonster`** (`0x1800c9d90` → `JMP 0x1800c7250`) are the public-adjacent entry points closest to this logic.

## Repo staleness

`inputs/CanIDoPutMonster_Usage_tsv.txt` lists VAs such as `0x1804a7b03`. In the **current** DLL, that address is **`mov ecx, 0x53`**, not a `CALL` to `CanIDoPutMonster`. Any mod based on that file must **refresh xrefs** from Ghidra (`get_xrefs_to` on `0x1800c3cb0` or export `0x180ea9eb0`).

## Open questions (in-game validation)

1. **Tribute release UI** — forcing tier **1** may still leave separate code that prompts to select monsters to tribute during the summon **resolution** step; test with level 7 normal monsters.
2. **`FUN_180861e60`** — confirm context (likely related summon/set dialog); patched together with the other two call sites.
3. **Cards with explicit “Cannot be Normal Summoned…”** — effect-driven; this patch does not remove those text rules.

## Next steps (other Junior Trials rules)

Separate investigations: hand size cap, spell/trap activation limits, set limits, effect special summon count — likely different functions (`GetPossibleMonsterActions`, phase/action bitmasks, etc.).
