import xml.etree.ElementTree as ET

root = ET.parse("obituaries 2013 08.xml").getroot()

for child in root:
    if child.tag[-4:] == "body":
        body = child
        break

lineElements = []
for child in body:
    if child.tag[-1] == 'p':
        lineElements.append(child)

pages = []
page = ""
valKey = "{http://schemas.microsoft.com/office/word/2003/wordml}val"
for line in lineElements:
    for child in line:
        if child.tag[-3:] == "pPr":
            print child[0].attrib[valKey]
