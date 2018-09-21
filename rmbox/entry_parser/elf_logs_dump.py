import section
import sys
import os
import entry

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

ELF_DIRECTORY = sys.argv[1]
OUT_DIR = sys.argv[2]

# init elf sections
section.init_sections(ELF_DIRECTORY)
section.dump_sections(OUT_DIR)

'''
local_entries = []

with open(out_dir, "r") as f:
	content = f.readlines()

# removing newlines
content = list(map(lambda s: s[:len(s)-1], content))

for c in content:
	e = entry.Entry()
	e.load_raw_params(c)
	local_entries += [e]
	# e.print_params()
'''
