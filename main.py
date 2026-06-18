import re


"""
self todo:
add banners
add acls
add hostnames
add switch dns config
"""
"""

in my test config I noticed that port ranges do not cross multi-digit boundaries
so "ethe 1/1/45 to 1/2/4" will always be "ethe 1/1/45 to 1/1/48 ethe 1/2/1 to 1/2/4"
if you have a config that does, this function will break
"""
def x_to_y_converter(input_string):
	int_list = input_string.split()
	new_list = []
	to_check = False
	last_item = ""
	for item in int_list:
		if item == "to":
			to_check = True
			pass
		elif to_check:
			starting_int = last_item.split("/")[2]
			stopping_int = item.split("/")[2]
			prefix = "/".join(item.split("/")[:-1])
			for digit in range(int(starting_int)+1, int(stopping_int)+1):
				new_list.append("ethe")
				new_list.append(f"{prefix}/{str(digit)}")
			last_item = item
			to_check = False
		else:
			new_list.append(item)
			last_item = item
	return " ".join(new_list)


def main(brocade_config_path):
	physical_interface_sections = []
	physical_interface_dict = {}
	lag_sections = []
	lag_list = []
	l2_vlan_sections = []
	l2_vlan_dict = {}
	l3_vlan_sections = []
	interface_vlan_dict= {}

	with open(brocade_config_path, "r") as file:
		file_content = file.read()
	sections = file_content.split("!")

	for section in sections:
		if section.split()[0] == "trunk":
			lag_sections.append(section)
		elif section.split()[0] == "vlan":
			l2_vlan_sections.append(section)
		elif section.split()[0] == "interface":
			if section.split()[1] == "ethe":
				physical_interface_sections.append(section)
			elif section.split()[1] == "ve":
				l3_vlan_sections.append(section)
	
	for section in physical_interface_sections:
		port_number = section.split()[2]
		port_desc = ""
		shutdown = False
		section_list = section.split("\n")
		for line in section_list:
			if line.split()[0] == "port-name":
				port_desc = line.split()[1:]
			elif line.split(0) == "disable":
				shutdown = True
		physical_interface_dict[port_number] = {"description":port_desc, "trunk":False, "native":"1", "vlans":[], "lag":"", "shutdown":shutdown}

	for section in l2_vlan_sections:
		vlan_num = section.split()[1]
		vlan_desc = ""
		if section.split()[2] == "name":
			vlan_desc = "".join(section.split("\n")[0].split()[3:-2])
		l2_vlan_dict[vlan_num] = vlan_desc
		section_break = section.split("tagged")
		tagged_string = x_to_y_converter(section_break[1])
		section_break[2] = " ".join(section_break[2].split()[1:])
		untagged_string = x_to_y_converter(section_break[2])
		tagged_list = tagged_string.split()
		untagged_list = untagged_string.split()
		for interface in tagged_list:
			if interface != "ethe":
				physical_interface_dict[interface]["vlans"].append(vlan_num)
				physical_interface_dict[interface]["trunk"] = True
		for interface in untagged_list:
			if interface != "ethe":
				physical_interface_dict[interface]["native"] = vlan_num

	for section in lag_sections:
		section_num = 1
		lag_list.append(section_num)
		section = x_to_y_converter(section)
		interface_list = section.split()
		for interface in interface_list:
			if interface != "trunk" and interface != "ethe":
				physical_interface_dict[interface]["lag"] = str(section_num)
		section_num += 1

	for section in l3_vlan_sections:
		vlan_num = section.split()[3]
		ip_address = ""
		helper_list = []
		desc = ""
		config_list = section.split("\n")
		for line in config_list:
			if line.split[0] == "ip" and line.split[1] == "address":
				ip_address = line
			elif line.split[0] == "ip" and line.split[1] == "helper-address":
				helper_list.append(line)
			elif line.split[0] == "port-name":
				desc = line.split()[1:]
		interface_vlan_dict[vlan_num] = {"description":desc, "address":ip_address, "helpers":helper_list}
	
