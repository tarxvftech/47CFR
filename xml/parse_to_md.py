import sys
import xml.etree.ElementTree as ET

def getdivlevel(et):
    assert( et.tag.startswith("DIV") )
    divlevel = int(et.tag[3:])
    return divlevel


def xmlet2markdown(et,level=0,prefixlevel=0):
    markdown = ""
    indent = "\t"*level
    if et.text and not et.text.isspace():
        markdown += f"{indent} {et.tag}:{et.text}"
    level += 1
    for child in et:
        if child.tag in ["HEAD"]:
            mydivlevel = getdivlevel(et)
            headerlevel = mydivlevel - prefixlevel
            header = "#"*(headerlevel)
            header = "\n\n" + header
            markdown += f"{header} {child.text}\n\n"
            level = 0
        elif child.tag in ["AUTH","SOURCE","EDNOTE"]:
            markdown += f"{indent} {child.tag} {child.text}\n"
        elif child.tag in ["P"]:
            t = ''.join(child.itertext())
            markdown += f"{indent} {t}\n\n"
        elif child.tag in ["TABLE"]:
            ...
            #add a link to the table in ecfr or render as markdown table
        else:
            markdown += f"{child.tag}\n"
            markdown += xmlet2markdown(child,level=level,prefixlevel=prefixlevel)
    return markdown

def xml_to_markdown(xml_string):
    root = ET.fromstring(xml_string)
    prefixlevel = getdivlevel(root)
    markdown = xmlet2markdown(root, level=0, prefixlevel=prefixlevel)
    return markdown


if __name__ == "__main__":
    with open(sys.argv[1],"r") as fd:
        md = xml_to_markdown(fd.read())
        print(md)
