# from xmlParser import XMLParser
from lxml import etree
from io import StringIO, BytesIO
import sys

textStyle = 'padding: 0px; margin: 0px;'
tableStyle = 'border-collapse: collapse; border: 1px solid black;'
tableItemStyle = 'border: 1px solid black; padding: 3px;'

STYLE = '''

div, h2, p {
  margin: 0;
  padding: 0;
  font-family: Arial, "Helvetica Neue", Helvetica, sans-serif;
}

th, td, p {
  font-size: 0.8em;
}

.elementName {
  font-size: 1.2em;
  padding: 0;
  margin: 0;
}

.attributeContainer {
  padding: 10px;
}

.elementContainer {
  # box-shadow: 1px 1px 10px grey;
  # padding: 10px; 
  # border: 1px solid black;
  margin-left: 10px;
  margin-bottom: 10px;
  margin-top: 10px;
  background-color: rgba(0,0,0,0.05);
}
.elementContainer table {
  padding-left: 20px;
}

.bold {
  font-weight: bold
}

input[type='checkbox'] {
  display: none;
}

.collapsible-content {
  max-height: 0px;
  overflow: hidden;

  transition: max-height .25s ease-in-out;
}

.lbl-toggle {
  font-weight: bold;
}
.lbl-toggle::before {
  content: ' ';
  display: inline-block;

  border-top: 5px solid transparent;
  border-bottom: 5px solid transparent;
  border-left: 5px solid currentColor;

  vertical-align: middle;
  margin-right: .7rem;
  transform: translateY(-2px);

  transition: transform .2s ease-out;
}

.toggle:checked + .lbl-toggle::before {
  transform: rotate(90deg) translateX(-3px);
}

.toggle:checked + .lbl-toggle {
  border-bottom-right-radius: 0;
  border-bottom-left-radius: 0;
}

.toggle:checked + .lbl-toggle + .collapsible-content {
  max-height: none
}

'''

# def renderElementTable

def addAttributes(source, elementDict):
  # if len(source.keys()) > 0:
    # attributes = etree.SubElement(container, 'table')
    # attributes.attrib['class'] = 'attributeContainer'
    for key in source.keys():
      elementDict[resolveName(key, source.nsmap)] = source.get(key)
      # a = etree.fromstring('''
      #   <tr>
      #     <th style="text-align: left;">{attribute}:</th>
      #     <td>{content}</td>
      #   </tr>
      # '''.format(attribute = resolveName(key, source.nsmap), content=source.get(key)))
      # attributes.append(a)
    return elementDict

def resolveTagName(source):

  tag = etree.QName(source.tag)
  if (tag.namespace):
    for key in source.nsmap:
      if source.nsmap[key] == tag.namespace:
        if key:
          return key + ':' + tag.localname

  return tag.localname

def resolveName(name, nsmap):
  tag = etree.QName(name)
  if (tag.namespace):
    for key in nsmap:
      if nsmap[key] == tag.namespace:
        if key:
          return key + ':' + tag.localname

  return tag.localname

def resolveChildren(source, currentContainer, isListItem = False):
  # if len(source) == 0:
  #   textNode = etree.SubElement(currentContainer, 'p')
  #   textNode.text = source.text
  #   return

  names = {}
  for child in source:
    tag = child.tag
    if tag in names:
      names[tag] += 1
    else:
      names[tag] = 1

  # reslove text elements
  # for key in names:
  #   if names[key] == 1:
  #     # an element or container is found
  #     for child in source:
  #       if child.tag == key:
  #         # print(len(child))
  #         # the element is found, filter out only textnodes first
  #         if len(child) == 0:
  #           resolveElement(child, currentContainer)
  
  # reslove subcontainers
  for key in names:
    if names[key] == 1:
      # an element or container is found
      for child in source:
        if child.tag == key:
          # print(len(child))
          # the element is found, filter out only textnodes first
          if len(child) != 0:
            resolveElement(child, currentContainer)

  # resolve lists
  for key in names:
    if names[key] > 1:

      # find all columns in an array, to be used for a table
      columns = set()
      attributes = set()
      for child in source:
        if child.tag == key:
          for c in child:
            columns.add(c.tag)
          for a in child.attrib:
            attributes.add(a)

      if len(columns) + len(attributes) > 5:
        if names[key] > 5:
          # handle large arrays
          collapsable = etree.SubElement(currentContainer, 'div')
          checkbox = etree.SubElement(collapsable, 'input')
          checkbox.attrib['id'] = key
          checkbox.attrib['class'] = 'toggle'
          checkbox.attrib['type'] = 'checkbox'
          label = etree.SubElement(collapsable, 'label')
          label.attrib['for'] = key
          label.text = "expand"
          label.attrib['class'] = 'lbl-toggle'
          cont = etree.SubElement(collapsable, 'div')
          cont.attrib['class'] = 'collapsible-content'
          for child in source:
            if child.tag == key:
              resolveElement(child, cont)
          pass
        else:
          for child in source:
            if child.tag == key:
              resolveElement(child, currentContainer)
        return


      listContainer = etree.SubElement(currentContainer, 'div')
      # listContainer.attrib['style'] = containerStyle
      listContainer.attrib['class'] = 'elementContainer'
      title = etree.SubElement(listContainer, 'h2')
      title.attrib['style'] = textStyle
      title.text = resolveName(key, child.nsmap) + ' - list'

      # addAttributes(source, listContainer)

      listItem = etree.SubElement(listContainer, 'table')
      listItem.attrib['style'] = tableStyle

      tableHeaderRow = etree.SubElement(listItem, 'tr')
      tableHeaderRow.attrib['style'] = tableItemStyle
      for column in columns:
        if isinstance(column, basestring):
          tableItem = etree.SubElement(tableHeaderRow, 'th')
          tableItem.attrib['style'] = tableItemStyle
          tableItem.text = column
          for child in source:
            if child.tag == key:
              for c in child:
                if c.tag == column:
                  tableItem.text = resolveTagName(c).replace(child.tag, "")

      # add attributes as columns
      for attrib in attributes:
        tableItem = etree.SubElement(tableHeaderRow, 'th')
        tableItem.attrib['style'] = tableItemStyle
        tableItem.text = attrib

      for child in source:
        if child.tag == key:
          tableRow = etree.SubElement(listItem, 'tr')
          tableRow.attrib['style'] = tableItemStyle
          resolveListElement(child, tableRow, columns, attributes)
          

def resolveListElement(source, container, columns, attributes):

  if len(source) == 0 and len(source.keys()) == 0:
    textNode = etree.SubElement(container, 'p')
    textNode.text = source.text
  
  names = {}
  for child in source:
    tag = child.tag
    if tag in names:
      names[tag] += 1
    else:
      names[tag] = 1

  for col in columns:
    if col in names and names[col] > 1:
      # a list is found, render as list:
      cont = etree.SubElement(container, 'td')
      cont.attrib['style'] = tableItemStyle

      listItem = etree.SubElement(cont, 'table')
      listItem.attrib['style'] = tableStyle

      tableHeaderRow = etree.SubElement(listItem, 'tr')
      tableHeaderRow.attrib['style'] = tableItemStyle

      cols = set()
      attbs = set()
      for child in source:
        if child.tag == col:
          for c in child:
            cols.add(c.tag)
          for a in child.attrib:
            attbs.add(a)


      for column in cols:
        tableItem = etree.SubElement(tableHeaderRow, 'th')
        tableItem.attrib['style'] = tableItemStyle
        for child in source:
          if child.tag == column:
            tableItem.text = resolveTagName(child)

      for attrib in attbs:
        tableItem = etree.SubElement(tableHeaderRow, 'th')
        tableItem.attrib['style'] = tableItemStyle
        tableItem.text = attrib

      for child in source:
        # print(child.tag)
        if child.tag == col:
          tableRow = etree.SubElement(listItem, 'tr')
          tableRow.attrib['style'] = tableItemStyle
          resolveListElement(child, tableRow, cols, attbs)
      # pass
    else:
      found = False
      for child in source:
        if child.tag == col:
          tableItem = etree.SubElement(container, 'td')
          tableItem.attrib['style'] = tableItemStyle
          resolveElement(child, tableItem, True)
          found = True
      if not found:
        tableItem = etree.SubElement(container, 'td')
        tableItem.attrib['style'] = tableItemStyle
        tableItem.text = "EMPTY"

  for attrib in attributes:
    tableItem = etree.SubElement(container, 'td')
    tableItem.attrib['style'] = tableItemStyle
    if attrib in source.attrib:
      tableItem.text = source.attrib[attrib]
    else:
      tableItem.text = "EMPTY"
      

def resolveElement(source, container, isListItem=False, parentName=""):

  # if element has no children, render it as text
  if len(source) == 0: 
    if len(source.keys()) == 0:
      if isListItem:
        textNode = etree.SubElement(container, 'p')
        textNode.text = source.text
      else:
        if source.text:
          textNode = etree.SubElement(container, 'h2')
          textNode.text = resolveTagName(source) + ': ' + source.text
      return

  if len(source) == 1 and len(source.keys()) == 0 and not isListItem:
    resolveElement(source[0], container, False, source.tag)
    return
  # else, render as a container
  currentContainer = etree.SubElement(container, 'div')
  # currentContainer.attrib['style'] = containerStyle
  currentContainer.attrib['class'] = 'elementContainer'
  if not isListItem:
    title = etree.SubElement(currentContainer, 'h2')
    # title.attrib['style'] = textStyle
    title.attrib["class"] = "elementName"
    title.text = ""
    if parentName != "":
      title.text = parentName + " -> "
    title.text += resolveTagName(source)

  elementDict = {}

  if not source.text or source.text.strip() != "":
    # textNode = etree.SubElement(currentContainer, 'p')
    if source.text:
      elementDict['Value'] = source.text
      # textNode.text = "Value: " + source.text

  # for each attribute add it:
  elementDict = addAttributes(source, elementDict)

  for child in (child for child in source if len(child) == 0 and len(child.attrib) == 0):
    # print(child.tag)
    elementDict[resolveTagName(child).replace(source.tag, "")] = child.text

  # render attributes and values table
  if len(elementDict.keys()) > 0:
    # attributes = etree.SubElement(currentContainer, 'table')
    # attributes.attrib['class'] = 'attributeContainer'

    elements = []
    for key in elementDict:
      cont = ""
      if elementDict[key]:
        cont = elementDict[key]
      elements.append(u'''
          <th style="text-align: left;">{attribute}:</th>
          <td>{content}</td>
      '''.format(attribute = key, content=cont))
    
    res = u""
    for i,k in zip(elements[0::2], elements[1::2]):
      # print(i, k)
      res += u"<tr>" + i + k + u"</tr>"
      pass
    # print(u"<table>" + res + "</table>")
    currentContainer.append(etree.fromstring(u"<table>" + res + "</table>"))

  # identify lists:
  # if multiple children has the same tag, count as list.
  resolveChildren(source, currentContainer, isListItem)



# Main functionallity:
inputFile = "./example.xml"
outputFile = "./res.html"

if  len(sys.argv) >= 2:
  inputFile = sys.argv[1]
if  len(sys.argv) >= 3:
  outputFile = sys.argv[2]


myTree = etree.Element("html")
head = etree.SubElement(myTree, "head")
style = etree.SubElement(head, "style")
style.text = STYLE

body = etree.SubElement(myTree, "body")

tree = etree.parse(inputFile)
resolveElement(tree.getroot(), body)

body[0].attrib['style'] = "background-color: white;"

with open(outputFile, 'w') as f:
  f.write(etree.tostring(myTree, pretty_print=True))