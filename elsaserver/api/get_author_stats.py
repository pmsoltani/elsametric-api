from datetime import datetime

from elsametric.models.author import Author
from elsametric.models.country import Country

# from .. import home_country


def get_author_stats(session, id_backend: int):
    response = None
    stats = {
        'hIndex': None,
        'i10Index': None,
        'totalPapers': None,
        'totalCitationss': None,
        'thisYearPapers': None,
        'thisYearCitationss': None,
        'intl_collaborations': None,
    }

    home_country = session \
        .query(Country) \
        .filter(Country.domain == 'IR') \
        .first()

    try:
        author = session.query(Author).get(id_backend)  # None if not found

        stats['hIndex'] = {
            'value': author.h_index_gsc,  # possible AttributeError
            'retrievalTime': author.retrieval_time_gsc,
        }
        stats['i10Index'] = {
            'value': author.i10_index_gsc,
            'retrievalTime': author.retrieval_time_gsc,
        }

        papers_trend = author.get_papers()
        citations_trend = author.get_citations()
        this_year = datetime.now().year

        stats['totalPapers'] = {'value': sum(papers_trend.values())}
        stats['totalCitationss'] = {'value': sum(citations_trend.values())}
        if this_year in papers_trend.keys():
            stats['thisYearPapers'] = {'value': papers_trend[this_year]}
            stats['thisYearCitationss'] = {'value': citations_trend[this_year]}

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
        stats['intl_collaborations'] = intl_collaborations

        response = stats
    except AttributeError:
        pass

    return response
