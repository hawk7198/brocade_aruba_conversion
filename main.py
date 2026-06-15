def main(brocade_config_path):
	phy_sections = []
	phy_list = []
	lag_sections = []
	lag_list = []
	vlan_sections = []
	vlan_list = []

	with open(brocade_config_path, "r") as file:
		file_content = file.read()
	sections = file_content.split("!")

	for section in sections:
		if section.split()[0] == "trunk":
			lag_sections.append(section)
		elif section.split()[0] == "vlan":
			vlan_sections.append(section)
		elif section.split()[0] == "interface":
			if section.split()[1] == "ethe":
				phy_sections.append(section)
			elif section.split()[1] == "ve":
				vlan_sections.append(section)
	
