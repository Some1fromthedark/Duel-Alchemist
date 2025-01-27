# Configuration Guide

This document provides a detailed explanation of the structure and usage of configuration files for **Duel-Alchemist**.

## Overview
Configuration files are JSON files that allow users to set default values for the script's arguments. These configurations streamline the process of modifying `duel.dll` by predefining paths and parameters. There are two levels of configuration:

1. **Base Configuration** (`config/config_base.json`): Loaded first and defines the global default values for the script.
2. **Secondary Configuration**: Specified using the `-c` argument when running the script. Overrides the defaults set in the base configuration.

---

## Base Configuration: `config/config_base.json`
The base configuration file contains a single key, `default_values`, which is a dictionary of default arguments. Any other elements in the file are ignored.

### Example `config/config_base.json`:
```json
{
	"default_values": {
		"input_dll": "../masterduel_Data/Plugins/x86_64/duel_.dll",
		"output": "../masterduel_Data/Plugins/x86_64/duel.dll"
	}
}
```

### Keys in `default_values`
The `default_values` dictionary can include any of the following key-value pairs:

- **`config`**: *(str)* The default path to load the configuration JSON file from.
- **`usage_file`**: *(str)* The default path to load the usage text file from.
- **`payload_file`**: *(str)* The default path to load the payload text file from.
- **`input_dll`**: *(str)* The default path to load the input DLL file from.
- **`output`**: *(str)* The default path to save the modified DLL to.
- **`start_index`**: *(int)* The default starting index for offsets from the usage file.
- **`count`**: *(int)* The default number of offsets to process from the usage file, starting from `start_index`.
- **`blacklist_file`**: *(str)* The default path to the blacklist file.
- **`blacklist`**: *(list)* The default list of blacklisted indices.
- **`magic_offset`**: *(int)* The default magic offset for converting usage file offsets to input DLL offsets.

### Behavior:
- If a key-value pair exists in `config/config_base.json`, it overrides the corresponding hardcoded default value in the script.
- Missing keys in `config/config_base.json` are populated with the hardcoded defaults.

---

## Secondary Configuration
When the user specifies a secondary configuration file using the `-c` argument, the script:
1. Loads `config/config_base.json` first to get the global defaults.
2. Loads the specified secondary configuration file, inheriting the defaults from `config/config_base.json`.
3. Overrides any values in the base configuration with those provided in the secondary configuration.

### Example Secondary Configuration:
```json
{
	"usage_file": "inputs/CanIDoPutMonster_Usage_tsv.txt",
	"payload_file": "payloads/payload_mov_1.txt",
	"start_index": 3,
	"count": 5,
	"blacklist_file": "blacklists/blacklist_infinite_normal_summons.txt"
}
```

### Explanation:
- **`usage_file`**: Specifies the path to the usage text file (`inputs/CanIDoPutMonster_Usage_tsv.txt`).
- **`payload_file`**: Specifies the path to the payload file (`payloads/payload_mov_1.txt`).
- **`start_index`**: Overrides the starting index with `3`.
- **`count`**: Limits the number of offsets to `5`.
- **`blacklist_file`**: Specifies the path to the blacklist file.

Keys not included in this file (e.g., `input_dll`, `output`, etc.) will inherit their values from `config/config_base.json`.

---

## Key Points to Remember:
- The `default_values` dictionary in `config/config_base.json` is the foundation for all configurations.
- Secondary configuration files build on the base configuration but can override specific values.
- Any unspecified keys in the secondary configuration will fall back to the values in `config/config_base.json`.

By leveraging these configuration files, you can easily customize and manage the behavior of **Duel-Alchemist** without having to specify arguments manually every time you run the script.
