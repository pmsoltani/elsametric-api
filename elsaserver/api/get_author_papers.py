from typing import Tuple

from .. import Author, Paper, Paper_Author, Session
from ..helpers import paper_formatter


def get_author_papers(db: Session, id_backend: int) -> Tuple[dict]:
    # returns a list of all papers for author 'id_backend'

    papers = db \
        .query(Paper) \
        .join((Paper_Author, Paper.authors)) \
        .join((Author, Paper_Author.author)) \
        .filter(Author.id == id_backend) \
        .all()  # empty list if not found
    # possible TypeError
    return tuple(paper_formatter(paper) for paper in papers)
