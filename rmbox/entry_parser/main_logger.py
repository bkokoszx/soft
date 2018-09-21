import subprocess
import os
import sys
import tools
import section
import io
import argparse

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

DMA_DIRECTORY = None
ELF_DIRECTORY = None
OUTPUT_DIRECTORY = None

IN_PIPE_HANDLE = 0			# handling input pipe flag
OUT_PIPE_HANDLE = 0			# handling output pipe flag

parser = argparse.ArgumentParser()
parser.add_argument("dirs", nargs="*",
	help='[dma_dump_dir, elf_dir, out_dir]')
parser.add_argument("--dma_dir")
parser.add_argument("--elf_dir")
parser.add_argument("--out_dir")
args = parser.parse_args()
argv = args.dirs

if not os.isatty(0):
	IN_PIPE_HANDLE = 1
	if args.dma_dir != None:
		sys.exit("Using pipe with --dma_dir flag is forbidded")

if not IN_PIPE_HANDLE:
	DMA_DIRECTORY, argv = tools.get_arg_directory(args.dma_dir, 
							argv, DMA_DIRECTORY)
		
ELF_DIRECTORY, argv = tools.get_arg_directory(args.elf_dir, 
						argv, ELF_DIRECTORY)

OUTPUT_DIRECTORY, argv = tools.get_arg_directory(args.out_dir,
							argv, OUTPUT_DIRECTORY)
if OUTPUT_DIRECTORY == None:
	OUT_PIPE_HANDLE = 1

if IN_PIPE_HANDLE:
	# intercepting binary trace input
	dma_trace_input = sys.stdin.buffer.read()
	
	# making hexadecimal dump
	xxd_cmd = subprocess.Popen(['xxd', '-e', '-g', '4'],
				stdin=subprocess.PIPE, stdout=subprocess.PIPE)
	xxd_cmd.stdin.write(dma_trace_input)
	xxd_cmd.stdin.close()
else:
	# making hexadecimal dump
	xxd_cmd = subprocess.Popen(['xxd', '-e', '-g', '4', 
				DMA_DIRECTORY], stdout=subprocess.PIPE)

# reset output file
	if not OUT_PIPE_HANDLE:
		f = open(OUTPUT_DIRECTORY, 'w+')
		f.close()

# removing unnecessary colums
dma_trace_content = subprocess.check_output(['awk',
						"{print $2 \" \" $3 \" \" $4 \" \" $5}"],
						stdin=xxd_cmd.stdout)
dma_trace_content = dma_trace_content.split()
dma_trace_content = list(map(tools.decode_bytes, dma_trace_content))

# init elf sections
section.init_sections(ELF_DIRECTORY)

out = tools.format_output_header()
if OUT_PIPE_HANDLE:
		sys.stdout.write(out)
else:
	with open(OUTPUT_DIRECTORY, 'a+') as f:
		f.write(out)

# fetching dma_trace_content
while len(dma_trace_content):
	# fetching core_id
	try:
		core_id = tools.string_hex_to_int(dma_trace_content.pop(0))
	except ValueError:
		break
	if not len(dma_trace_content):
		break
		
	# fetching timestamp
	try:
		t_1 = tools.string_hex_to_int(dma_trace_content.pop(0))
	except ValueError:
		break
	if not len(dma_trace_content):
		break
		
	try:
		t_2 = tools.string_hex_to_int(dma_trace_content.pop(0))
	except:
		break
	if not len(dma_trace_content):
		break
		
	timestamp = (t_2 << 32) | t_1
	
	# fetching entry address
	e_addr = tools.string_hex_to_int(dma_trace_content.pop(0))
	
	# searching entry in elf sections
	for sec in section.SECTIONS:
		entry = sec.get_entry(e_addr)
		if (entry != None):
			break
			
	if (entry != None):
		if (len(dma_trace_content) < entry.param_count):
			break
		
		# fetching entry parameters
		e_params = []
		for i in range(entry.param_count):
			e_params += \
				[tools.string_hex_to_int(dma_trace_content.pop(0))]
				
		out = tools.format_output(tools.LOG_FORMAT,
								  core_id,
								  timestamp,
								  entry.level,
								  entry.component_id,
								  entry.line_idx,
								  entry.file_name,
								  entry.text,
								  e_params)
		if OUT_PIPE_HANDLE:
			sys.stdout.write(out)
		else:
			with open(OUTPUT_DIRECTORY, 'a+') as f:
				f.write(out)

