from pydantic import BaseModel


class Paragraph(BaseModel):
    volume: str = ""
    part: str = ""
    chapter: str

    content: str
    notes: str
