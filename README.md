# Duel-Alchemist: A Tool for Modifying Yu-Gi-Oh! Master Duel's duel.dll

**Duel-Alchemist** is a powerful tool designed to modify the `duel.dll` file from **Yu-Gi-Oh! Master Duel**, the core file responsible for enforcing the game’s rules and logic. By injecting custom payloads into specific machine instructions, Duel-Alchemist allows users to transform gameplay mechanics, experiment with game states, or create custom game modes.

## Features:
- **Flexible Configuration**: Use JSON-based configuration files to set defaults, define offsets, and customize behavior.
- **Command-Line Interface**: Supports positional arguments and optional flags for precise control.
- **Blacklist Support**: Exclude specific offsets from modification for fine-tuned patching.
- **Instruction-Level Modding**: Disassemble and replace instructions with user-defined payloads.
- **Safety Checks**: Ensures payloads fit the length of the target instructions for reliable execution.

## Use Cases:
- **Custom Gameplay**: Modify how the game enforces rules or handles specific game states.
- **Debugging & Analysis**: Experiment with game logic to explore and test scenarios.
- **Automation**: Streamline patching workflows for development, experimentation, or modding.

Unleash your creativity and master the art of transforming *Yu-Gi-Oh! Master Duel* with Duel-Alchemist!

## Installation
1. Clone this repository into the "Yu-Gi-Oh! Master Duel" directory (the game's installation directory):
   ```bash
   git clone https://github.com/Some1fromthedark/Duel-Alchemist.git
   ```

2. Install the required dependencies using `pip` and the `requirements.txt` file:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a backup of the `duel.dll` file by renaming it to `duel_.dll` in the following directory:
   ```
   Yu-Gi-Oh! Master Duel/masterduel_Data/Plugins/x86_64/
   ```
   This ensures you have a fallback in case any issues arise, and the backup is used as the default input dll for the Duel-Alchemist script.

## Usage Examples

### Infinite Normal Summons Mod
This mod grants the player unlimited normal summons by replacing calls to `DuelCanIDoPutMonster` with `mov rax, 1`.

Run the script with the following command:
```bash
python script_name.py -c configs/config_infinite_normal_summons.json
```

### Enable Actions Mod
This mod ensures that when the player has a normal summon, they always have the `Special Summon`, `Activate`, `Normal Summon`, and `Set` actions available for all monsters in their hand. It achieves this by injecting `mov rax, 92` over all calls to a specific function.

Run the script with the following command:
```bash
python script_name.py -c configs/config_enable_actions.json
```