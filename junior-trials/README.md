# Junior Trials mod research

Working notes for a **Yu-Gi-Oh! Master Duel** rules mod (Junior Trials format) built with [Duel-Alchemist](../README.md).

## Scope (current)

Focus: **normal summon / set of level 5+ monsters without tributing**, while keeping other rules intact for later work (spell/trap limits, special summon cap, hand size, etc.).

## Contents

| Document | Purpose |
|----------|---------|
| [01-tribute-investigation.md](01-tribute-investigation.md) | Ghidra findings in `duel.dll` (current build) |
| [02-proposed-patch-no-tributes.md](02-proposed-patch-no-tributes.md) | Patch strategy and Duel-Alchemist config |
| [inputs/GetAdvanceSummonTributeCount_call_sites.tsv](inputs/GetAdvanceSummonTributeCount_call_sites.tsv) | Patch addresses (Ghidra VAs) |

## Binary reference

- **Program:** `duel.dll` (Ghidra project **Masterduel**)
- **Image base:** `0x180000000`
- **Magic offset** (VA → file offset in Duel-Alchemist): `-6442454016` (`-0x180000000`)

## Note on shipped examples

Repo usage files such as `inputs/CanIDoPutMonster_Usage_tsv.txt` target **old** call-site VAs. At `1804a7b03` the bytes are no longer a `CALL` to `CanIDoPutMonster` in the current DLL—regenerate xref lists from Ghidra before reusing those mods.
