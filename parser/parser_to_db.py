from sqlalchemy.orm import Session

from core.models import Paragraph
from core.database import create_db

from .element import ElementType
from .parser import Parser


def parse_and_add_to_db(root_url: str):
    p = Parser(root_url)
    table = p.parse_table_of_content()
    current_volume = ""
    current_part = ""

    db = create_db()

    for element in table:
        if element.element_type == ElementType.volume:
            current_volume = element.name
        elif element.element_type == ElementType.part:
            current_part = element.name
        else:
            paragraphs = p.parse_chapter(element.url, current_part, current_volume)
            for i, paragraph in enumerate(paragraphs):
                db.add(
                    Paragraph(**{
                        **paragraph.dict(),
                        "paragraph": i + 1
                    })
                )
                db.commit()
