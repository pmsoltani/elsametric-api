from elsametric.models.paper import Paper
from elsametric.models.associations import Paper_Author
from elsametric.models.author import Author

from ..helpers import paper_formatter


def get_author_papers(session, id_backend: int):
    # returns a list of all papers for author 'id_backend'
    response = None

    try:
        papers = session \
            .query(Paper) \
            .join((Paper_Author, Paper.authors)) \
            .join((Author, Paper_Author.author)) \
            .filter(Author.id == id_backend) \
            .all()  # empty list if not found
        # possible TypeError
        response = tuple(paper_formatter(paper) for paper in papers)
    except TypeError:
        pass

    return response
