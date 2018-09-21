import os
import sys
import tools
import entry
import subprocess
import math

class Section:
	LEN_OBJDUMP_INDEX = 2
	START_ADDRESS_OBJDUMP_INDEX = 4
	BIN_OFFSET_OBJDUMP_INDEX = 5
	
	name = ""
	start_address = 0
	bin_offset = 0
	length = 0
	
	content = ""			# section content
	entries = []			# entries existing in that section
	
	def __init__(self, name):
		self.name = name		# section name
	
	# Fetch length, offset and entries
	def load(self, elf_dir):
		# cmd
		xtobj_cmd = subprocess.Popen(['xt-objdump', '-h', elf_dir], stdout=subprocess.PIPE)
		os_ret = subprocess.check_output(['grep', self.name], stdin=xtobj_cmd.stdout)
		os_ret = os_ret.split()
		for i in range(len(os_ret)):
			os_ret[i] = os_ret[i].decode("utf-8")
				
		# fetching length
		self.length = tools.string_hex_to_int(os_ret[self.LEN_OBJDUMP_INDEX])
		
		# fetching address 
		self.start_address = tools.string_hex_to_int(os_ret[self.START_ADDRESS_OBJDUMP_INDEX])
		
		# fetching offset
		self.bin_offset = tools.string_hex_to_int(os_ret[self.BIN_OFFSET_OBJDUMP_INDEX])
		
		# fetching section context
		self.__fetch_content(elf_dir)
		
		# fetching entries
		self.fetch_entries(elf_dir)
		
	def __fetch_content(self, elf_dir):
		xxd_cmd = subprocess.Popen(['xxd', '-u', '-g', '4', '-s', hex(self.bin_offset), '-l', hex(self.length), elf_dir], stdout=subprocess.PIPE)
		self.content = subprocess.check_output(['awk', '{print $2 \" \" $3 \" \" $4 \" \" $5}'], stdin=xxd_cmd.stdout)
		self.content = self.content.split()
		self.content = list(map(tools.decode_bytes, self.content))
		pass
		
	def fetch_entries(self, elf_dir): # fetching amount of entries in existing in that section
		
		# new
		xtobj_cmd = subprocess.Popen(['xt-objdump', '-tj', self.name, elf_dir], stdout=subprocess.PIPE)
		g1_cmd = subprocess.Popen(['grep', '-v', '00000000'], stdin=xtobj_cmd.stdout, stdout=subprocess.PIPE)
		g2_cmd = subprocess.Popen(['grep', '-v', 'SYMBOL TABLE'], stdin=g1_cmd.stdout, stdout=subprocess.PIPE)
		g3_cmd = subprocess.Popen(['grep', '-v', '"^$"'], stdin=g2_cmd.stdout, stdout=subprocess.PIPE)
		g4_cmd = subprocess.Popen(['grep', '-v', 'file format'], stdin=g3_cmd.stdout, stdout=subprocess.PIPE)
		os_ret = subprocess.check_output(['awk', '{print $1 \" \" $5}'], stdin=g4_cmd.stdout)
		
		entry_info = {
			"address" : None,
			"length" : None
		}
		os_ret = os_ret.split()
		os_ret = list(map(tools.decode_bytes, os_ret))
		
		for i in range(int(len(os_ret)/len(entry_info))):
			entry_info["address"] = tools.string_hex_to_int(os_ret[i*len(entry_info)])
			entry_info["length"] = tools.string_hex_to_int(os_ret[i*len(entry_info) + 1])
			
			# New entry
			e = entry.Entry(entry_info["address"])
			
			# Fetching entry length and offset
			e.set_length_and_offset(entry_info["length"], self.start_address, self.bin_offset)
			
			# Fetching entry content
			b_i = int((e.binary_offset - self.bin_offset)/4)		# beg index
			e_i = b_i + int(math.ceil(entry_info["length"]/4.0))	# end index
			e.fetch_content(''.join(self.content[b_i:e_i+1]))
			
			self.entries += [e]
	
	def get_entry(self, entry_address):
		for e in self.entries:
			if (entry_address == e.start_address):
				return e
		return None

# ALL ENTRIES SECTIONS DEFINED IN .ELF FILE
SECTIONS = [
	Section(".static_log_entries")
]

def init_sections(in_file):
	for s in SECTIONS:
		s.load(in_file)

def dump_sections(out_file):
	# reset file
	f = open(out_file, 'w+')
	f.close()
	
	for s in SECTIONS:
		for e in s.entries:
			e.save_raw_params(out_file)
