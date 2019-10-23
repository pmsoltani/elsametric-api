from sqlalchemy import extract

from elsametric.models.paper import Paper
from elsametric.models.associations import Paper_Author
from elsametric.models.author import Author

from ..helpers import paper_formatter


def get_author_papers_year(session, id_backend: int,
                           year: int, year_range: tuple) -> tuple:
    # returns a list of papers published in 'year' for author 'id_backend'

    if not isinstance(year, int):
        raise TypeError
    if not (year_range[0] <= year <= year_range[1]):
        raise ValueError

    papers = session \
        .query(Paper) \
        .join((Paper_Author, Paper.authors)) \
        .join((Author, Paper_Author.author)) \
        .filter(
            Author.id == id_backend,
            extract('year', Paper.date) == year) \
        .all()  # empty list if not found
    # possible TypeError
    return tuple(paper_formatter(paper) for paper in papers)
