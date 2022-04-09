from sqlalchemy import Column, Integer, String, Text
from core.database import Base


class Paragraph(Base):
    __tablename__ = 'paragraphs'

    id = Column(Integer, primary_key=True, index=True)  # в будущем можно добавить book_id

    # нумерация
    volume = Column(String)
    part = Column(String)
    chapter = Column(String)
    paragraph = Column(Integer)

    content = Column(Text)
    notes = Column(Text)

