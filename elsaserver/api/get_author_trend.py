from .. import Author, Session


def get_author_trend(db: Session, id_backend: int) -> tuple:
    author = db.query(Author).get(id_backend)  # None if not found
    papers_trend = author.get_papers_trend()  # possible AttributeError
    citations_trend = author.get_citations_trend()

    trend = []
    for year in papers_trend:
        trend.append({
            'year': year,
            'papers': papers_trend[year],
            'citations': citations_trend[year]
        })
    return tuple(trend)
