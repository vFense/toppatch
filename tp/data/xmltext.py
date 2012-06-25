
from lxml import etree as ET

xmlfile = "/home/radioact1ve/Desktop/topPatch/custom.xml"


def main():

	tree = ET.parse(xmlfile)
	root = tree.getroot()

	print "root: " + str(root)

	for subelement in root:
		print subelement.tag
		print subelement.attrib

if __name__ == "__main__":
	main()
