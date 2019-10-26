from datetime import datetime
from typing import List

from .. import Author, Country, Paper, Session, home_country, home_institution


paper_types_mapper = {
    'ar': 'article',
    'ip': 'article',
    'cp': 'conference',
    're': 'review',
    'bk': 'book',
    'ch': 'book',
    'tb': 'other',
    'le': 'other',
    'ed': 'other',
    'no': 'other',
    'er': 'other',
    'sh': 'other',
    'ab': 'other',
    'na': 'other'
}


def get_author_stats(db: Session, id_backend: int) -> dict:
    stats = {
        'hIndex': None,
        'i10Index': None,
        'papers': {
            'retrievalTime': None,
            'totalPapers': 0,
            'totalCitations': 0,
            'thisYearPapers': 0,
            'thisYearCitations': 0
        },
        'paperTypes': {
            'retrievalTime': None,
            'article': 0,
            'conference': 0,
            'review': 0,
            'book': 0,
            'other': 0,
        },
        'collaborations': {
            'retrievalTime': None,
            'singleAuthorship': 0,
            'instCollaboration': 0,
            'natCollaboration': 0,
            'intlCollaboration': 0
        }
    }
    total_citations = this_year_papers = this_year_citations = 0
    single_authorship = 0
    inst_collaboration = nat_collaboration = intl_collaboration = 0
    this_year = datetime.now().year

    author: Author
    author = db.query(Author).get(id_backend)  # None if not found

    # h-index & i10-index
    stats['hIndex'] = {
        'value': author.h_index_gsc,  # possible AttributeError
        'retrievalTime': author.retrieval_time_gsc,
    }
    stats['i10Index'] = {
        'value': author.i10_index_gsc,
        'retrievalTime': author.retrieval_time_gsc,
    }

    papers: List[Paper]
    papers = [paper_author.paper for paper_author in author.papers]
    stats['papers']['totalPapers'] = len(papers)
    oldest_retrieval_time = datetime.now()
    for paper in papers:
        # comparing the retrieval times:
        if paper.retrieval_time < oldest_retrieval_time:
            oldest_retrieval_time = paper.retrieval_time
        # papers & citations count
        total_citations += paper.cited_cnt or 0  # citations might be None
        if paper.get_year() == this_year:
            this_year_papers += 1
            this_year_citations += paper.cited_cnt or 0

        # paper types
        paper_type = paper_types_mapper[paper.type]
        try:
            # possible KeyError, TypeError
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
            intl_collaboration += 1
        elif is_nat_paper:
            nat_collaboration += 1
        else:
            inst_collaboration += 1

    stats['papers']['retrievalTime'] = oldest_retrieval_time
    stats['papers']['totalCitations'] = total_citations
    stats['papers']['thisYearPapers'] = this_year_papers
    stats['papers']['thisYearCitations'] = this_year_citations

    stats['paperTypes']['retrievalTime'] = oldest_retrieval_time

    stats['collaborations']['retrievalTime'] = oldest_retrieval_time
    stats['collaborations']['singleAuthorship'] = single_authorship
    stats['collaborations']['instCollaboration'] = inst_collaboration
    stats['collaborations']['natCollaboration'] = nat_collaboration
    stats['collaborations']['intlCollaboration'] = intl_collaboration

    return stats
