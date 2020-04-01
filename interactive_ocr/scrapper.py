import html5lib
import glob
import pandas

from PyQt5.QtWidgets import QApplication
from interactive_ocr.form import getInputOutput

PRE = '{http://www.w3.org/1999/xhtml}'


def parse_person(person):
    name = ''
    address = ''
    tel = ''

    for elem in person.iter():
        class_names = elem.attrib.get('class')

        if class_names and class_names.startswith('adresse'):
            address = elem.text

        if class_names and class_names.startswith('denomination-links'):
            name = elem.text

        if class_names and class_names.startswith('num') and elem.tag.endswith('strong'):
            tel = elem.text

    return {
       'name': name.strip(),
       'address': address.strip(),
       'telephone': tel.strip()
    }


def read_htmls(input, output):
    data = []

    for file_name in glob.glob(f'{input}/*.html')[:]:
        with open(file_name, 'br') as file:
            document = html5lib.parse(file)

        elems = list(document.findall(f".//*{PRE}div[@class]"))
        people = []

        for child in elems:
            class_attr = child.attrib.get('class')
            if class_attr and class_attr.startswith('zone-bi'):
                people.append(child)

        print(f'Found {len(people)} in `{file_name}`')
        for person in people:
            parsed = parse_person(person)
            data.append(parsed)

    df = pandas.DataFrame(data)
    df.to_excel(output)


def main():
    import sys
    app = QApplication(sys.argv)

    input, output = getInputOutput()
    read_htmls(input, output)

    app.closeAllWindows()
    sys.exit(0)

if __name__ == '__main__':
    main()
