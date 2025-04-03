from exceptions import InvalidSortParameterError


class BookQueryValidator:
    _valid_fields = ["title", "published_year", "author"]
    _valid_directions = ["asc", "desc"]

    @staticmethod
    def parse_sort_by(sort_by: str) -> tuple[str, str]:
        try:
            field, direction = sort_by.split(":")
            if field not in BookQueryValidator._valid_fields:
                raise InvalidSortParameterError(field="sort_by", message=f"Invalid field '{field}'")
            if direction not in BookQueryValidator._valid_directions:
                raise InvalidSortParameterError(field="sort_by", message=f"Invalid direction '{direction}'")

            return field, direction
        except ValueError:
            raise InvalidSortParameterError()
