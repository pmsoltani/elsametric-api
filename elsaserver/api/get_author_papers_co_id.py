from typing import Tuple

from .. import Author, Keyword, Paper, Paper_Author, Session
from ..helpers import get_joint_papers


def get_author_papers_co_id(db: Session,
                            id_backend: int, co_id: str) -> Tuple[dict]:
    # returns joint papers between author 'id_backend' and co_author 'co_id'

    if not isinstance(co_id, str):
        raise TypeError

    author = db.query(Author).get(id_backend)  # None if not found
    if co_id == author.id_frontend:
        raise ValueError
    if len(co_id) != len(author.id_frontend):  # possible TypeError
        raise ValueError

    co_author = db \
        .query(Author) \
        .filter(Author.id_frontend == co_id) \
        .first()  # None if not found
    if not co_author:
        raise ValueError

    papers = db \
        .query(Paper) \
        .join((Paper_Author, Paper.authors)) \
        .join((Author, Paper_Author.author)) \
        .filter(Author.id == id_backend) \
        .all()  # empty list if not found

    return tuple(get_joint_papers(papers, co_author, format_results=True))
