import math
from functools import reduce

LOG_FORMAT = '%10s %12s %10s %15s %-15s \t %1s \n'
BYTES_IN_DWORD = 4

def string_hex_to_int(s):
	return int("0x" + s, 16)

def decode_bytes(byte):
	return byte.decode("utf-8")
	
def int_to_string_hex(val):
	return format(val, 'x')
	
def string_big_to_little_end(string_hex_dword):
	return string_hex_dword[6:8] + string_hex_dword[4:6] + \
		   string_hex_dword[2:4] + string_hex_dword[0:2]

def dword_value(string_dword):
	return string_hex_to_int(string_big_to_little_end(string_dword))

def fetch_text(content, text_byte_len):
	get_range = lambda i: (i*2, i*2+2)
	extract_content = lambda tuple: content[tuple[0]:tuple[1]]
	from_hex_to_char = lambda h: chr(string_hex_to_int(h))
	s_sum = lambda x, y: x + y
	
	return reduce(s_sum, map(from_hex_to_char, 
		map(extract_content ,map(get_range, range(text_byte_len)))))
	
def get_text_dword_len(text_byte_len):
	return int(math.ceil(float(text_byte_len)/BYTES_IN_DWORD))
					
def format_output(log_format,
				  core_id,
				  timestamp,
				  level,
				  component_id,
				  line_idx,
				  file_name,
				  text,
				  params):
					  
			out = log_format % (
					str(core_id),
					str(timestamp),
					str(level),
					str(component_id),
					str(file_name) + ":" + str(line_idx),
					(str(text) % tuple(params))
					)
					
			return out

def format_output_header():
	out = LOG_FORMAT % ("CORE_ID",
						"TIMESTAMP",
						"LEVEL",
						"COMPONENT_ID",
						"FILE_NAME",
						"CONTENT")
	return out
	
def get_arg_directory(in_arg, argv, arg_dir):
	if in_arg != None:
		arg_dir = in_arg
	else:
		if len(argv):
			arg_dir = argv.pop(0)
		else:
			arg_dir = None
	return [arg_dir, argv]
