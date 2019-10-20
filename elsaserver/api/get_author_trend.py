from elsametric.models.author import Author


def get_author_trend(session, id_backend: int):
    response = None
    try:
        author = session.query(Author).get(id_backend)  # None if not found
        papers_trend = author.get_papers()  # possible AttributeError
        citations_trend = author.get_citations()

        trend = []
        for year in papers_trend:
            trend.append({
                'year': year,
                'papers': papers_trend[year],
                'citations': citations_trend[year]
            })
        response = tuple(trend)
    except AttributeError:
        pass

    return response
