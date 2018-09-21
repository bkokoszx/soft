import sys
import os
import tools
import subprocess

class Entry:
	LENGTH_OBJDUMP_INDEX = 4
	HEX_IN_DWORD = 8 	# Number of hex tokens in one dword
	
	start_address = 0	# Memory entry address
	length = 0			# Length in memory
	section_name = ""	# The name of section in which the 
						# entry is stored
	binary_offset = 0 	# Offset in binary file
	hex_content = []	# Entry content in hex
	
	print_list = [		# list for debug
		"start_address",
		"level",
		"component_id",
		"param_count",
		"line_idx",
		"file_name_len",
		"file_name",
		"text_len",
		"text"
	]
	
	def __init__(self, start_address=None):
		self.start_address = start_address
		
	def set_length_and_offset(self,
							  length,
							  section_address,
							  section_offset):
		self.length = length
		self.binary_offset = section_offset + \
			(self.start_address - section_address)
		
	def fetch_content(self, content):
		self.hex_content = content
		
		ci = 0 					# content index
		ct = self.hex_content	# content
		
		get_dword = lambda _ci : (tools.dword_value(ct[_ci : _ci + self.HEX_IN_DWORD]), _ci + self.HEX_IN_DWORD)
		get_text = lambda _ci, bytecount : (tools.fetch_text(ct[_ci:(_ci + bytecount * 2)], bytecount - 1), _ci + tools.get_text_dword_len(self.file_name_len) * self.HEX_IN_DWORD)
			
		# parse level 
		self.level, ci = get_dword(ci)
		
		# parse component_id
		self.component_id, ci = get_dword(ci) 
		
		# parse param_count
		self.param_count, ci = get_dword(ci)  
		
		# parse line_idx
		self.line_idx, ci = get_dword(ci)
		
		# parse file_name_len
		self.file_name_len, ci = get_dword(ci)
		
		# parse file name
		self.file_name, ci = get_text(ci, self.file_name_len)
		
		# parse text len
		self.text_len, ci = get_dword(ci)
		
		# parse text
		self.text, ci = get_text(ci, self.text_len)
		
	def print_params(self):
		for item in self.print_list:
			print(item + ": " + str(eval("self." + item)))

		
	def save_params(self, filename):
		with open(filename, "a+") as f:
			for item in self.print_list:
				f.write(item + ": " + str(eval("self." + item)) + "\n")
	
	def save_raw_params(self, filename):
		out = ""
		for item in self.print_list:
			out += str(eval("self." + item)) + " "
		out += "\n"
		
		with open(filename, "a+") as f:
			f.write(out)
			
	def load_raw_params(self, content):
		SPACE_SPLIT_INDEX = 8
		space_i = 0
		char_i = 0

		for char in content:
			if char == " ":
				space_i += 1
			if space_i == SPACE_SPLIT_INDEX:
				break		
			char_i += 1
		params = content[:char_i].split()
		msg = content[(char_i + 1):]
		
		self.start_address = int(params[0])
		self.level = int(params[1])
		self.component_id = int(params[2])
		self.param_count = int(params[3])
		self.line_idx = int(params[4])
		self.file_name_len = int(params[5])
		self.file_name = params[6]
		self.text_len = int(params[7])
		self.text = msg

