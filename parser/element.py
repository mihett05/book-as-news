from enum import Enum
from pydantic import BaseModel, HttpUrl


class ElementType(str, Enum):
    chapter = 'chapter'
    part = 'part'
    volume = 'volume'


class Element(BaseModel):
    name: str
    element_type: ElementType = ElementType.chapter
    url: HttpUrl
