import sys
import re
import xml.etree.ElementTree as ET

def getdivlevel(et):
    assert( et.tag.startswith("DIV") )
    divlevel = int(et.tag[3:])
    return divlevel

def add_links(md,part=97):
    pattern = r'\b(\d+\.\d+)\((\w+)\)'
    def replacement(match):
        section = match.group(1)
        subsection = match.group(2)
        return f"[#{section}{subsection}](#abcd)"
    result = re.sub(pattern, replacement, md)
    # md = result
    return md

def add_links_to_legal_text(text,part='97'):
    section_pattern = re.compile(
            r'^\#*\s*§?\s*(?P<part>%s\.\d+)'%(part)
            + r'|^\s*(?P<alpha>\([a-z]+\))' 
            + r'|^\s*(?P<number>\(\d+\))' 
            #r'(?P<part>§\s*\d+\.\d+)' 
            #roman numerals, handled by alpha regex
            # r'|(?P<roman>\([ivx]+\))'
            )
    current_section = []
    processed_lines = []

    for line in text.splitlines():
        if not line:
            processed_lines.append(line) #preserve empty newlines
            continue
        matches = list(section_pattern.finditer(line))

        # print(line)
        if matches:
            # print(current_section)
            # print(matches, current_section)
            for match in matches:
                # if match.group() == '(i)':
                    # import pdb; pdb.set_trace()
                if match.group('part'):
                    current_section = [match.group('part')]
                elif match.group('alpha'):
                    if len(current_section)>1 and (\
                        ('h' not in current_section[-1] and 'i' in match.group('alpha')) or \
                        ('w' not in current_section[-1] and 'x' in match.group('alpha')) or \
                        ('u' not in current_section[-1] and 'v' in match.group('alpha')) \
                                                   ):
                        #roman
                        while len(current_section) > 3:
                            current_section.pop()
                        current_section.append(match.group('alpha'))
                    else:
                        #letters, not roman numerals
                        while len(current_section) > 1:
                            current_section.pop()
                        current_section.append(match.group('alpha'))
                elif match.group('number'):
                    while len(current_section) > 2:
                        current_section.pop()
                    current_section.append(match.group('number'))
                # elif match.group('roman'):
                    # while len(current_section) > 2:
                        # current_section.pop()
                    # current_section.append(match.group('roman'))

            section_label = ''.join(current_section).replace('(', '').replace(')', '').replace('.', '_')
            link = f"#{section_label}"
            name = ''.join(current_section)
            anchor = link
            nl = f"[{name}]({link})\n"
            processed_lines.append(nl)
            processed_lines.append(line)
        else:
            processed_lines.append(line)

    return '\n'.join(processed_lines)

def add_anchors(md,part=97):
    header_pattern = r'^(### §\s+(\d+\.\d+))'
    subsection_pattern = r'^\((\w+)\)'

    lines = md.splitlines()
    result_lines = []
    current_section_number = None  # Keep track of the current section number
    for line in lines:
        header_match = re.match(header_pattern, line)
        a = False
        if header_match:
            current_section_number = header_match.group(2)
            # Create anchor tag for section
            anchor = f'<a name="{current_section_number}">'
            result_lines.append(anchor)
            a=True

        # Check if the line is a subsection
        subsection_match = re.match(subsection_pattern, line)
        if subsection_match and current_section_number:
            subsection_letter = subsection_match.group(1)
            # Create anchor tag for subsection
            anchor = f'<a name="{current_section_number}({subsection_letter})">'
            result_lines.append(anchor)
            a=True

        result_lines.append(line)
        if a:
            result_lines.append("</a>")

    return "\n".join(result_lines)


def xmlet2markdown(et,level=0,prefixlevel=0):
    markdown = ""
    indent = "\t"*level
    # if et.text and not et.text.isspace():
        # markdown += f"{indent} {et.tag}:{et.text}"
    level += 1
    for child in et:
        if child.tag in ["HEAD"]:
            mydivlevel = getdivlevel(et)
            headerlevel = mydivlevel - prefixlevel +1
            header = "#"*(headerlevel)
            header = "\n\n" + header
            markdown += f"{header} {child.text}\n\n"
            level = 0
        elif child.tag in ["AUTH","SOURCE","EDNOTE"]:
            markdown += f"{indent}{child.tag} {child.text}\n"
        # elif child.tag in ["P"]:
            # t = ''.join(child.itertext())
            # markdown += f"{indent} {t}\n\n"
            # markdown += f"{indent} {child.text}\n\n"
            # if child.text.strip() == "(50)":
                # import pdb; pdb.set_trace()
            # markdown += xmlet2markdown(child,level=level,prefixlevel=prefixlevel)
        elif child.tag in ["TABLE"]:
            ...
            #add a link to the table in ecfr or render as markdown table
        else:
            if child.text:
                markdown += f"{child.text}"
            if list(child):
                markdown += xmlet2markdown(child,level=level,prefixlevel=prefixlevel)
            if child.tail:
                markdown += f"{child.tail}\n"
    return markdown

def xml_to_markdown(xml_string):
    root = ET.fromstring(xml_string)
    prefixlevel = getdivlevel(root)
    markdown = xmlet2markdown(root, level=0, prefixlevel=prefixlevel)
    part=root.get('N')
    # markdown = add_anchors(markdown, part=part)
    # markdown = add_links(markdown, part=part)
    markdown = add_links_to_legal_text(markdown)
    return markdown


if __name__ == "__main__":
    with open(sys.argv[1],"r") as fd:
        md = xml_to_markdown(fd.read())
        print(md)

    """
97.3 Definitions
 (a) The definitions of terms used in part 97 are:
  (1) <I>Amateur Operator</I>. A person named in an amateur operator/primary ...
  ...
  (11) <I>Call sign system.</I> The method used to select a call sign ... The call sign systems are:
    (i) <I>Sequential Call Sign System</I> The call sign is selected by ...

    """
