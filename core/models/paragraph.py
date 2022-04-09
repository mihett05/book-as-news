from sqlalchemy import Column, Integer, Text
from core.database import Base


class Paragraph(Base):
    __tablename__ = 'paragraphs'

    id = Column(Integer, primary_key=True, index=True)  # в будущем можно добавить book_id

    # нумерация
    volume = Column(Integer)
    part = Column(Integer)
    chapter = Column(Integer)
    paragraph = Column(Integer)

    content = Column(Text)
    notes = Column(Text)

