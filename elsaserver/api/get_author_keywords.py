from typing import Tuple

from .. import Author, Session


def get_author_keywords(db: Session, id_backend: int,
                        keywords_threshold: int) -> Tuple[dict]:
    author = db.query(Author).get(id_backend)  # None if not found

    # possible AttributeError
    keywords = author.get_keywords(threshold=keywords_threshold)
    return tuple({'keyword': k, 'value': v} for k, v in keywords.items())
