from typing import Tuple

from .. import Author, Paper, Paper_Author, Session, extract
from ..helpers import paper_formatter


def get_author_papers_year(db: Session, id_backend: int,
                           year: int, year_range: tuple) -> Tuple[dict]:
    # returns a list of papers published in 'year' for author 'id_backend'

    if not isinstance(year, int):
        raise TypeError
    if not (year_range[0] <= year <= year_range[1]):
        raise ValueError

    papers = db \
        .query(Paper) \
        .join((Paper_Author, Paper.authors)) \
        .join((Author, Paper_Author.author)) \
        .filter(
            Author.id == id_backend,
            extract('year', Paper.date) == year) \
        .all()  # empty list if not found
    # possible TypeError
    return tuple(paper_formatter(paper) for paper in papers)
