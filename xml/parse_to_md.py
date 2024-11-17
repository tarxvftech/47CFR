import sys
import re
import xml.etree.ElementTree as ET

def getdivlevel(et):
    assert( et.tag.startswith("DIV") )
    divlevel = int(et.tag[3:])
    return divlevel

def anchor_name(section):
    return section.replace('§','').strip().replace('(', '').replace(')', '') #.replace('.', '_')

def add_links(md,part=97,base_url=""):
    """
    Find references like 97.3(a)(11)(iii) and make them hyperlinks
    """
    # simple = r'(\d+\.\d+(\s*\(\s*\w+\s*\))*)' 
    simple = r'(%s.\d+(\s*\(\s*\w+\s*\))*)'%(part)
    #first process for references to multiple sections simultaneously,
    #e.g. "§§ 97.305(c) and 97.307(f) of the part, an amateur station may transmit ...
    def replacement2(match):
        anchor = anchor_name(match.group())
        name = match.group()
        s = f"[{name}](#{anchor})"
        return s

    multiple = '§§' 
    start = 0
    while True:
        start = md.find(multiple, start)
        if start == -1:
            break
        newline = md.index('\n', start)
        end = md.find('§', start+2, newline)
        if end == -1:
            end = newline
        so = md[start:end]
        sn = re.sub(simple, replacement2, so)
        # print(so)
        # print(sn)
        md = md[:start] + sn + md[end:]
        start = start + len(sn)

    #then for single references
    single = r'(?<!§)(?<=§ )\s*' + simple
    def replacement(match):
        anchor = anchor_name(match.group())
        name = match.group()
        s = f"[{name}](#{anchor})"
        return s
    result = re.sub(single, replacement, md)

    return result

def add_anchors(text,part='97'):
    """
    Track sections throughout a document, nested like 
    97.3(a)(11)(iii) and give them anchors for future linking purposes
    """
    section_pattern = re.compile(
            r'^\#*\s*§?\s*(?P<part>%s\.\d+)'%(part)
            + r'|^\s*(?P<alpha>\([a-z]+\))' 
            + r'|^\s*(?P<number>\(\d+\))' 
            + r'|^\s*(?P<ALPHA>\([A-Z]+\))' 
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
                elif match.group('ALPHA'):
                    while len(current_section) > 4:
                        current_section.pop()
                    current_section.append(match.group('ALPHA'))
                # elif match.group('roman'):
                    # while len(current_section) > 2:
                        # current_section.pop()
                    # current_section.append(match.group('roman'))

            section_label = ''.join(current_section)
            section_label = anchor_name(section_label)
            link = f"{section_label}"
            name = ''.join(current_section)
            anchor = link
            # nl = f"[{name}]({link})\n"
            # processed_lines.append(nl)
            anchor_html=f'<a name="{anchor}"></a>'
            # processed_lines.append(f'<span id="{anchor}">\n')
            # processed_lines.append('</span>')
            indent = "  "*(len(current_section)-2) if len(current_section)>1 else ""
            indent += "- " if len(current_section)>1 else ""
            # processed_lines.append(anchor_html)
            processed_lines.append(indent+ line.lstrip() + "\t\t" + anchor_html)
        else:
            processed_lines.append(line)

    return '\n'.join(processed_lines)



def xmlet2markdown(et,prefixlevel=0):
    markdown = ""
    for child in et:
        if child.tag in ["HEAD"]:
            mydivlevel = getdivlevel(et)
            headerlevel = mydivlevel - prefixlevel +1
            header = "#"*(headerlevel)
            header = "\n\n" + header
            markdown += f"{header} {child.text}\n\n"
        elif child.tag in ["AUTH","SOURCE","EDNOTE"]:
            markdown += f"{child.tag} {child.text}\n"
        elif child.tag in ["TABLE"]:
            ...
            #add a link to the table in ecfr or render as markdown table
        else:
            if child.text:
                markdown += f"{child.text}"
            if list(child):
                markdown += xmlet2markdown(child,prefixlevel=prefixlevel)
            if child.tail:
                markdown += f"{child.tail}"
    return markdown

def xml_to_markdown(xml_string):
    root = ET.fromstring(xml_string)
    prefixlevel = getdivlevel(root)
    markdown = xmlet2markdown(root, prefixlevel=prefixlevel)
    part=root.get('N')
    markdown = add_anchors(markdown, part=part)
    markdown = add_links(markdown, part=part, base_url="")
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
