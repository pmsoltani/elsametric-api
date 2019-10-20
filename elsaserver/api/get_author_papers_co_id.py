from elsametric.models.paper import Paper
from elsametric.models.associations import Paper_Author
from elsametric.models.author import Author
from elsametric.models.keyword_ import Keyword

from ..helpers import get_joint_papers


def get_author_papers_co_id(session, id_backend: int, co_id: str):
    # returns joint papers between author 'id_backend' and co_author 'co_id'
    response = None

    if not isinstance(co_id, str):
        return response

    try:
        author = session.query(Author).get(id_backend)  # None if not found
        if co_id == author.id_frontend:
            raise ValueError
        if len(co_id) != len(author.id_frontend):  # possible TypeError
            raise ValueError

        co_author = session \
            .query(Author) \
            .filter(Author.id_frontend == co_id) \
            .first()  # None if not found
        if not co_author:
            raise ValueError

        papers = session \
            .query(Paper) \
            .join((Paper_Author, Paper.authors)) \
            .join((Author, Paper_Author.author)) \
            .filter(Author.id == id_backend) \
            .all()  # empty list if not found

        response = tuple(
            get_joint_papers(papers, co_author, format_results=True))
    except (ValueError, TypeError, AttributeError):
        pass

    return response
