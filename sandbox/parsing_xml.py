from lxml import etree
import io


def parse_example():
    with open('../data/xml/example.xml') as file_handler:
        xml = file_handler.read()

    xml_root = etree.fromstring(xml)

    books = []
    book_dict = {}

    for book in xml_root.getchildren():
        for elem in book.getchildren():
            if not elem.text:
                text = "None"
            else:
                text = elem.text
            print(elem.tag + " => " + text)
            book_dict[elem.tag] = text

        if book.tag == "book":
            books.append(book_dict)
            book_dict = {}

    print(books)
    print(book_dict)


def parse_book():
    xml_root = etree.parse('../data/books/fb2/Eisenhorn_Omnibus.fb2').getroot()

    print(xml_root.getchildren())


parse_book()
