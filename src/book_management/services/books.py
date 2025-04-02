import csv
import json
from io import StringIO
from typing import Any, Protocol

# Prefer Single Responsibility Principle (keep 2 classes) over DRY in this approach (2 methods in 1 class)

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


class FileExporter(Protocol):
    def export(self, data: list[dict]) -> str:
        pass

class JSONExporter(FileExporter):
    def export(self, books_data: list[dict]) -> str:
        return json.dumps(books_data, indent=2)

class CSVExporter(FileExporter):
    def export(self, data: list[dict]) -> str:
        output = StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=["id", "title", "author_name", "genre", "published_year"],
        )
        writer.writeheader()
        writer.writerows(data)
        return output.getvalue()

class FileExporterFactory:
    _exporters = {
        "json": JSONExporter(),
        "csv": CSVExporter()
    }

    @classmethod
    def get_exporter(cls, format: str) -> FileExporter:
        exporter = cls._exporters.get(format.lower())
        if not exporter:
            raise ValueError("Unsupported format. Use JSON or CSV")
        return exporter