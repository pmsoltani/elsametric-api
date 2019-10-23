from elsametric.models.paper import Paper
from elsametric.models.associations import Paper_Author
from elsametric.models.author import Author
from elsametric.models.keyword_ import Keyword

from ..helpers import paper_formatter


def get_author_papers_keyword(session, id_backend: int,
                              keyword: str, keywords_threshold: int) -> tuple:
    # returns a list of papers containing 'keyword' for author 'id_backend'

    if not isinstance(keyword, str):
        raise TypeError

    author = session.query(Author).get(id_backend)  # None if not found

    # checking if the requested keyword is genuine
    # possible AttributeError
    keywords_list = list(
        author.get_keywords(threshold=keywords_threshold).keys())
    if not(keywords_list) or (keyword not in keywords_list):
        raise ValueError

    papers = session \
        .query(Paper) \
        .join((Paper_Author, Paper.authors)) \
        .join((Author, Paper_Author.author)) \
        .join((Keyword, Paper.keywords)) \
        .filter(Author.id == id_backend, Keyword.keyword == keyword) \
        .all()  # empty list if not found
    # possible TypeError
    return tuple(paper_formatter(paper) for paper in papers)
