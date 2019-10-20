from elsametric.models.author import Author

from ..helpers import author_formatter


def get_author_info(session, home_institution, id_backend: int):
    response = None
    author = session.query(Author).get(id_backend)  # None if not found
    if author:
        response = author_formatter(
            author, department=True, profile=True, institution=True,
            home_institution=home_institution)

    return response
