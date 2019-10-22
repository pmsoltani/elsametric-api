from datetime import datetime

from elsametric.models.author import Author
from elsametric.models.country import Country

from .. import home_country, home_institution


paper_types_mapper = {
    'ar': 'article',
    'ip': 'article',
    'cp': 'conference',
    're': 'review',
    'bk': 'book',
    'ch': 'book',
    'tb': 'retracted',
    'le': 'other',
    'ed': 'other',
    'no': 'note',
    'er': 'other',
    'sh': 'other',
    'ab': 'other',
    'na': 'other'
}


def get_author_stats(session, id_backend: int):
    response = None
    stats = {
        'hIndex': None,
        'i10Index': None,
        'papers': {
            'totalPapers': None,
            'totalCitationss': None,
            'thisYearPapers': None,
            'thisYearCitationss': None
        },
        'paperTypes': {},
        'collaborations': {
            'singleAuthorship': None,
            'instCollaborations': None,
            'natCollaborations': None,
            'intlCollaborations': None
        }
    }
    total_citations = this_year_papers = this_year_citations = 0
    single_authorship = 0
    inst_collaborations = nat_collaborations = intl_collaborations = 0
    this_year = datetime.now().year

    try:
        author = session.query(Author).get(id_backend)  # None if not found

        # h-index & i10-index
        stats['hIndex'] = {
            'value': author.h_index_gsc,  # possible AttributeError
            'retrievalTime': author.retrieval_time_gsc,
        }
        stats['i10Index'] = {
            'value': author.i10_index_gsc,
            'retrievalTime': author.retrieval_time_gsc,
        }

        papers = [paper_author.paper for paper_author in author.papers]
        stats['papers']['totalPapers'] = len(papers)
        for paper in papers:
            # papers & citations count
            total_citations += paper.cited_cnt or 0  # citations might be None
            if paper.get_year() == this_year:
                this_year_papers += 1
                this_year_citations += paper.cited_cnt or 0

            # paper types
            paper_type = paper_types_mapper[paper.type]
            try:
                stats['paperTypes'][paper_type] += 1
            except KeyError:
                stats['paperTypes'][paper_type] = 1

            # collaborations
            co_authors = [
                paper_author.author for paper_author in paper.authors]
            if len(co_authors) == 1:
                single_authorship += 1
                continue
            is_intl_paper = is_nat_paper = False
            for co_author in co_authors:
                if co_author == author:  # skipping the main author
                    continue

                # Since multiple SQLAlchemy sessions might be involved (between
                # 'home_country', 'home_institution', and 'co_author' objects),
                # it's best to use the objects' ids in comparisons.
                country_ids = {c.id for c in co_author.get_countries()}
                if country_ids and home_country.id not in country_ids:
                    is_intl_paper = True
                    break
                institution_ids = {i.id for i in co_author.get_institutions()}
                if home_institution.id not in institution_ids:
                    is_nat_paper = True

            if is_intl_paper:
                intl_collaborations += 1
            elif is_nat_paper:
                nat_collaborations += 1
            else:
                inst_collaborations += 1

        stats['papers']['totalCitationss'] = total_citations
        stats['papers']['thisYearPapers'] = this_year_papers
        stats['papers']['thisYearCitationss'] = this_year_citations
        stats['collaborations']['singleAuthorship'] = single_authorship
        stats['collaborations']['instCollaborations'] = inst_collaborations
        stats['collaborations']['natCollaborations'] = nat_collaborations
        stats['collaborations']['intlCollaborations'] = intl_collaborations

        response = stats
    except AttributeError:
        pass

    return response
