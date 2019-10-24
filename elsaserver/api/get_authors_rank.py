from .. import \
    Author, authors_backend, home_institution, home_country, \
    Session


def get_authors_rank(db: Session) -> dict:
    stats = {
        'h_index_gsc': [],
        'i10_index_gsc': [],
        'total_papers': [],
        'total_citations': [],
        'this_year_papers': [],
        'this_year_citations': [],
        'intl_collaborations': [],
    }

    for id_backend in authors_backend.values():
        try:
            author = db.query(Author).get(id_backend)  # None if not found

            # possible AttributeError
            stats['h_index_gsc'].append(author.h_index_gsc)
            stats['i10_index_gsc'].append(author.i10_index_gsc)

            # possible TypeError
            papers_trend = author.get_papers_trend()
            citations_trend = author.get_citations_trend()
            stats['total_papers'].append(sum(papers_trend.values()))
            stats['total_citations'].append(sum(citations_trend.values()))

            this_year = max(papers_trend.keys())
            stats['this_year_papers'].append(papers_trend[this_year])
            stats['this_year_citations'].append(citations_trend[this_year])

            intl_collaborations = 0
            papers = [paper_author.paper for paper_author in author.papers]
            for paper in papers:
                co_authors = [
                    paper_author.author for paper_author in paper.authors]
                for co_author in co_authors:
                    if co_author == author:
                        continue
                    countries = co_author.get_countries()
                    if countries and home_country not in countries:
                        intl_collaborations += 1
                        break
            stats['intl_collaborations'].append(intl_collaborations)
        except (AttributeError, TypeError) as e:
            print(e)
            pass

    return stats
