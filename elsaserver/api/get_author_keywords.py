from elsametric.models.author import Author


def get_author_keywords(session, id_backend: int, keywords_threshold: int):
    response = None

    try:
        author = session.query(Author).get(id_backend)  # None if not found

        # possible AttributeError
        keywords = author.get_keywords(threshold=keywords_threshold)
        response = tuple({'keyword': k, 'value': v}
                         for k, v in keywords.items())
    except AttributeError:
        pass

    return response
