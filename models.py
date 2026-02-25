from dataclasses import dataclass, asdict


@dataclass
class Book:
    no: str
    title: str
    genre: str
    author: str
    price: float
    year: int

    def to_dict(self) -> dict:
        d = asdict(self)
        d["price"] = float(self.price)
        d["year"] = int(self.year)
        return d

    @staticmethod
    def from_dict(d: dict) -> "Book":
        return Book(
            no=str(d.get("no", "")),
            title=str(d.get("title", "")),
            genre=str(d.get("genre", "")),
            author=str(d.get("author", "")),
            price=float(d.get("price", 0)),
            year=int(d.get("year", 0)),
        )