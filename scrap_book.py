from parser.parser import Parser


if __name__ == '__main__':
    p = Parser("https://ilibrary.ru/text/11/index.html")
    contents = p.parse_table_of_content()
    print(p.parse_chapter(contents[0].url))

