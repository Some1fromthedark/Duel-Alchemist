import argparse
import json
import os
import struct

from capstone import Cs, CS_ARCH_X86, CS_MODE_64

def parse_x86_64_instruction(byte_string, offset):
    """
    Parse a single x86_64 instruction from a byte string starting at a given offset.
    
    Args:
        byte_string (bytes): The input byte string containing machine code.
        offset (int): The offset to start parsing from.
    
    Returns:
        tuple: A tuple containing the instruction bytes and the disassembled instruction text.
    """
    # Initialize the Capstone disassembler for x86_64
    md = Cs(CS_ARCH_X86, CS_MODE_64)
    
    # Slice the byte string starting from the offset
    code_slice = byte_string[offset:]
    
    # Disassemble one instruction
    for instr in md.disasm(code_slice, offset):
        return (instr.bytes, instr.mnemonic + " " + instr.op_str)
    
    # If no instruction could be parsed, return None
    return None

base_config_path = "configs/config_base.json"

def load_config(config_path, defaults_map=None):
    if defaults_map is None:
        # Configure Defaults
        defaults_map = {
            "input_dll": "duel_.dll",
            "output": "duel.dll",
            "start_index": 0,
            "count": -1,
            "blacklist_file": None,
            "blacklist": [],
            "magic_offset": -6442454016,
            "config": base_config_path,
        }
    config_map = {
        "default_values": defaults_map
    }
    if os.path.exists(config_path):
        with open(config_path) as f:
            json_obj = json.load(f)
        if "default_values" not in json_obj:
            json_obj["default_values"] = defaults_map
        else:
            config_defaults = json_obj["default_values"]
            for default in defaults_map:
                if default not in config_defaults:
                    config_defaults[default] = defaults_map[default]
        config_map = json_obj
    return config_map

def main():
    config = load_config(base_config_path)
    defaults = config["default_values"]
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', default=defaults["config"])
    
    config_args, remaining_args = parser.parse_known_args()
    
    if config_args.config != base_config_path:
        config = load_config(config_args.config, defaults)
        defaults = config["default_values"]
    
    parser = argparse.ArgumentParser()
    if "usage_file" not in config:
        parser.add_argument('usage_file')
    if "payload_file" not in config:
        parser.add_argument('payload_file')
    parser.add_argument('-i', '--input_dll', default=defaults["input_dll"])
    parser.add_argument('-o', '--output', default=defaults["output"])
    parser.add_argument('-s', '--start_index', type=int, default=defaults["start_index"])
    parser.add_argument('-n', '--count', type=int, default=defaults["count"])
    parser.add_argument('-b', '--blacklist_file', default=defaults["blacklist_file"])
    parser.add_argument('-B', '--blacklist', type=int, nargs="+", default=defaults["blacklist"])
    parser.add_argument('-m', '--magic_offset', type=int, default=defaults["magic_offset"])
    
    args = parser.parse_args(remaining_args)

    # Files Info
    if "usage_file" in config:
        usage_fn = config["usage_file"]
    else:
        usage_fn = args.usage_file
    if "payload_file" in config:
        payload_fn = config["payload_file"]
    else:
        payload_fn = args.payload_file
    if "input_dll" in config:
        input_fn = config["input_dll"]
    else:
        input_fn = args.input_dll
    if "output" in config:
        output_fn = config["output"]
    else:
        output_fn = args.output    
    # Converts Ghidra address to duel.dll offset
    if "magic_offset" in config:
        magic_offset = config["magic_offset"]
    else:
        magic_offset = args.magic_offset
    
    # Parse the usage file
    with open(usage_fn, 'r') as f:
        usage_contents = f.read()
    usage_lines = [[field.strip() for field in line.split('\t')] for line in usage_contents.split('\n')]
    offsets = [int(line[0], 16) for line in usage_lines]
    
    with open(input_fn, 'rb') as f:
        dll_data = f.read()
    
    if "start_index" in config:
        start_index = config["start_index"]
    else:
        start_index = args.start_index
    if "count" in config:
        count = config["count"]
    else:
        count = args.count
    if count < 0:
        count = len(offsets)
    
    # Print Stage Info
    print("Start Index: {}, End Index: {}, Count: {}".format(start_index, start_index + count - 1, count))
    
    if "blacklist_file" in config:
        blacklist_fn = config["blacklist_file"]
    else:
        blacklist_fn = args.blacklist_file
    if blacklist_fn is not None:
        with open(blacklist_fn, 'r') as f:
            blacklist_content = f.read().strip()
        if len(blacklist_content) > 0:
            blacklisted_indices = [int(value) for value in blacklist_content.split(' ')]
        else:
            blacklisted_indices = []
    else:
        blacklisted_indices = []
        
    if "blacklist" in config:
        blacklist = config["blacklist"]
    else:
        blacklist = args.blacklist
    
    if len(blacklist) > 0 and len(blacklisted_indices) > 0:
        for ind in args.blacklist:
            if ind not in blacklisted_indices:
                blacklisted_indices.append(ind)
        blacklisted_indices.sort()
    elif len(blacklist) > 0:
        blacklisted_indices = blacklist
    
    # Print Black List Info
    print("Blacklisted Indices:\t{}".format(blacklisted_indices))
    
    # Determine the length of the minimum instruction we will be replacing with our payload
    min_instruction_len = -1
    for i in range(count):
        index = start_index + i
        if index in blacklisted_indices:
            continue
        
        offset = offsets[index]
        adjusted_offset = offset + magic_offset
        
        instr_info = parse_x86_64_instruction(dll_data, adjusted_offset)
        instr_values = struct.unpack("B"*len(instr_info[0]), instr_info[0])
        #print(" ".join([hex(value) for value in instr_values]))
        
        instruction_len = len(instr_values)
        if instruction_len < min_instruction_len or min_instruction_len == -1:
            min_instruction_len = instruction_len
            
    print("Min Instruction Length: {} bytes".format(min_instruction_len))
    
    # Load Payload Bytes
    with open(payload_fn, 'r') as f:
        payload_content = f.read().strip()
    if len(payload_content) > 0:
        payload_values = [int(value, 16) for value in payload_content.split(' ')]
    else:
        payload_values = []
    # TO-DO: Allow for larger payload lengths by adjusting dll metadata?
    if len(payload_values) > min_instruction_len:
        print("Error: The payload length must be less than or equal to {}".format(min_instruction_len))
        assert False
    payload_bytes = struct.pack("B"*len(payload_values), *payload_values)
    
    print("Payload Values: {}".format(" ".join([hex(value) for value in payload_values])))
    
    for i in range(count):
        index = start_index + i
        if index in blacklisted_indices:
            print("Skipping index {} due to blacklist".format(index))
            continue
        offset = offsets[index]
        adjusted_offset = offset + magic_offset
        instr_info = parse_x86_64_instruction(dll_data, adjusted_offset)
        instr_values = struct.unpack("B"*len(instr_info[0]), instr_info[0])
        instr_len = len(instr_values)
        #instr_bytes = dll_data[adjusted_offset:adjusted_offset+instr_len]
        #unpacked_instr_bytes = [hex(value) for value in struct.unpack('BBBBB', instr_bytes)]
        #print("{}:\t{}:\t{}:\t{}".format(index, hex(offset), hex(adjusted_offset), " ".join(unpacked_instr_bytes)))
        # Pad the payload to the length of the instruction
        instr_payload = payload_bytes + b'\x90'*(instr_len - len(payload_bytes))
        #print("{}:\t{}:\t{}".format(index, hex(adjusted_offset), instr_payload))
        dll_data = dll_data[0:adjusted_offset] + instr_payload + dll_data[adjusted_offset+instr_len:]
    
    with open(output_fn, 'wb') as f:
        f.write(dll_data)

if __name__ == '__main__':
    main()
