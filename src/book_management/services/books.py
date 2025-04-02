import csv
import json
from io import StringIO
from typing import Any, Protocol


class FileParser(Protocol):
    def parse(self, content: str) -> list[dict[str, Any]]:
        pass


class JSONFileParser:
    def parse(self, content: str) -> list[dict[str, Any]]:
        data = json.loads(content)
        if not isinstance(data, list):
            raise ValueError("JSON content must be an array of books")
        return data


class CSVFileParser:
    def parse(self, content: str) -> list[dict[str, Any]]:
        books = []
        csv_file = StringIO(content)
        reader = csv.DictReader(csv_file)

        required_headers = {"title", "author_name", "genre", "published_year"}
        if not required_headers.issubset(set(reader.fieldnames)):
            raise ValueError("CSV must contain title, author_name, genre, and published_year columns")

        for row in reader:
            row["published_year"] = int(row["published_year"])
            books.append(row)
        return books


class FileParserFactory:
    _parsers = {".json": JSONFileParser, ".csv": CSVFileParser}

    @classmethod
    def get_parser(cls, filename: str) -> FileParser:
        for ext, parser_class in cls._parsers.items():
            if filename.endswith(ext):
                return parser_class()
        raise ValueError("Unsupported file format. Use JSON or CSV")
