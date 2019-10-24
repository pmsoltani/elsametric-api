from .. import Author, Institution, Session
from ..helpers import author_formatter


def get_author_info(db: Session,
                    home_institution: Institution, id_backend: int) -> dict:
    author = db.query(Author).get(id_backend)  # None if not found
    # possible TypeError
    return author_formatter(
        author, department=True, profile=True, institution=True,
        home_institution=home_institution)
