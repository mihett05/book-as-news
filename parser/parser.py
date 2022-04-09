import requests
from typing import List, Dict
from urllib.parse import urlparse, urlunparse
from bs4 import BeautifulSoup
from bs4.element import Tag

from .element import Element, ElementType
from .paragraph import Paragraph


class Parser:
    root_url: str

    def __init__(self, table_of_contents_url: str):
        self.root_url = self._clear_root_url(table_of_contents_url)

    @classmethod
    def _clear_root_url(cls, url: str) -> str:
        scheme, host, path, _, _, _ = urlparse(url)
        if path.split("/")[-1].endswith(".html"):
            path = "/".join(path.split("/")[:-1])
        return urlunparse([scheme, host, path, "", "", ""])

    @classmethod
    def _scrap(cls, url: str) -> BeautifulSoup:
        return BeautifulSoup(requests.get(url).text, 'html.parser')

    def parse_table_of_content(self) -> List[Element]:
        soup = self._scrap(self.root_url)
        size_to_type = {
            "l0": ElementType.chapter
        }

        contents = []
        table = soup.select_one("table")
        rows = table.select("tr")
        if len(rows) >= 3:
            same_sum = sum([row.get("onclick") == rows[0].get("onclick") for row in rows[1:3]])
            if same_sum == 2:
                size_to_type = {
                    "l0": ElementType.volume,
                    "l1": ElementType.part,
                    "l2": ElementType.chapter
                }
            elif same_sum == 1:
                size_to_type = {
                    "l0": ElementType.part,
                    "l1": ElementType.chapter
                }

        for row in rows:
            div = row.select_one("td > div")
            link = div.select_one("div > p > a")

            name = link.get_text().strip()
            url = link.get("href")
            element_type = size_to_type[div.get("class")[0]]

            contents.append(Element(
                name=name,
                url=urlparse(self.root_url).scheme + "://" + urlparse(self.root_url).netloc + url,
                element_type=element_type
            ))

        return contents

    def parse_chapter(self, url: str, part: str = "", volume: str = "") -> List[Paragraph]:
        soup = self._scrap(url)
        notes = self._parse_notes(soup.select_one("#text > .fns"))
        paragraphs = []

        chapter = soup.select_one("#text > h3").get_text()

        for paragraph in soup.select("#text > span.p"):
            refs = []
            for ref in paragraph.select("span.fnref"):
                a = ref.select_one("sup").select_one("a")
                refs.append(int(a.text.strip()))
                a.string = f"*{a.text}*"

            notes_text = ""

            for ref in refs:
                notes_text += f"{ref}. {notes[ref]}\n"

            paragraphs.append(Paragraph(
                volume=volume,
                part=part,
                chapter=chapter,
                content=paragraph.get_text(),
                notes=notes_text
            ))
        return paragraphs

    @staticmethod
    def _parse_notes(fns: Tag) -> Dict[int, str]:
        notes = dict()
        number = 0
        found = False
        if fns:
            for i, el in enumerate(fns.children):
                if el.name == "div":
                    try:
                        number = int(el.select_one("span").select_one("sup").select_one("a").text.strip())
                        found = True
                    except AttributeError:
                        pass
                elif el.name == "span" and el.get("class")[0] == "p" and found:
                    notes[number] = el.text
                    found = False
        return notes
