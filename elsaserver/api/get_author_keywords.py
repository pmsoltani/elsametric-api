from elsametric.models.author import Author


def get_author_keywords(session,
                        id_backend: int, keywords_threshold: int) -> tuple:
    author = session.query(Author).get(id_backend)  # None if not found

    # possible AttributeError
    keywords = author.get_keywords(threshold=keywords_threshold)
    return tuple({'keyword': k, 'value': v} for k, v in keywords.items())
