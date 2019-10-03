import os
import json

from sqlalchemy import extract

from elsametric.models.base import Session
from elsametric.models.associations import Author_Department
from elsametric.models.associations import Paper_Keyword
from elsametric.models.associations import Paper_Author
from elsametric.models.associations import Source_Subject
from elsametric.models.author import Author
from elsametric.models.author_profile import Author_Profile
from elsametric.models.country import Country
from elsametric.models.department import Department
from elsametric.models.fund import Fund
from elsametric.models.institution import Institution
from elsametric.models.keyword_ import Keyword
from elsametric.models.paper import Paper
from elsametric.models.source import Source
from elsametric.models.source_metric import Source_Metric
from elsametric.models.subject import Subject


# ==============================================================================
# Config
# ==============================================================================


config_path = os.path.join(os.getcwd(), 'config.json')
with open(config_path, 'r') as config_file:
    config = json.load(config_file)

config = config['api']
home_institution_id_scp = config['home_institution_id_scp']
year_range = config['year_range']
keywords_threshold = config['keywords_threshold']
network_threshold = config['network_threshold']


# ==============================================================================
# Queries: Base
# ==============================================================================


session = Session()

a = session.query(Author)
# prf = session.query(Author_Profile)
# c = session.query(Country)
# d = session.query(Department)
# f = session.query(Fund)
i = session.query(Institution)
# k = session.query(Keyword)
p = session.query(Paper)
# src = session.query(Source)
# m = session.query(Source_Metric)
# sub = session.query(Subject)


# ==============================================================================
# Functions & Variables
# ==============================================================================


initial_response = {'message': 'not found', 'code': 404}

home_institution = i \
    .filter(Institution.id_scp == home_institution_id_scp) \
    .first()


def get_authors_list():
    # This function is not directly involved with the frontend

    # get a list of all faculty members of the home_institution
    authors = a \
        .with_entities(
            Author.id,
            Author.id_frontend,
            Author.first,
            Author.last,
            Author.first_pref,
            Author.last_pref) \
        .distinct() \
        .join((Department, Author.departments)) \
        .join((Institution, Department.institution)) \
        .filter(
            Author.type == 'Faculty',
            Institution.id_scp == home_institution_id_scp) \
        .order_by(Author.last) \
        .all()

    response_backend = {}  # used to map the id_frontend to id, for backend only
    response_frontend = []  # returned to the frontend
    for author in authors:
        response_backend[author.id_frontend] = author.id

        response_frontend.append({
            'idFrontend': author.id_frontend,
            'first': author.first_pref or author.first,
            'last': author.last_pref or author.last
        })
    return response_backend, response_frontend


authors_list_backend, authors_list_frontend = get_authors_list()
authors_tuple_frontend = tuple(authors_list_frontend)


def author_formatter(author, department: bool = False,
                     institution: bool = False, home_institution=None,
                     profile: bool = False):
    # helper function
    result = {}
    if department:
        departments = []
        try:
            for d in author.departments:  # possible TypeError, AttributeError
                if d.name == 'Undefined':  # default initial department
                    continue
                departments.append({
                    'name': d.name,
                    'type': d.type,
                    'idFrontend': d.id_frontend
                })
            result['departments'] = departments
        except (TypeError, AttributeError):
            pass

    if institution:
        institutions = []
        try:
            # possible TypeError, AttributeError
            for i in author.get_institutions():
                if (home_institution) and (i != home_institution):
                    continue
                institutions.append(
                    {'name': i.name, 'idFrontend': i.id_frontend})
            result['institutions'] = institutions
        except (TypeError, AttributeError):
            pass

    if profile:
        profiles = []
        try:
            for prf in author.profiles:  # possible TypeError, AttributeError
                profiles.append(
                    {'type': prf.type, 'address': prf.address})
            result['contact'] = profiles
        except (TypeError, AttributeError):
            pass

    return {
        'idFrontend': author.id_frontend,
        'first': author.first_pref or author.first,
        'last': author.last_pref or author.last,
        'sex': author.sex,
        'type': author.type,
        'rank': author.rank,
        **result
    }


def paper_formatter(paper):
    # helper function
    percentile = None
    quartile = None
    try:
        percentile = next(filter(
            lambda m: m.type == 'Percentile' and m.year == paper.get_year(),
            paper.source.metrics
        ), None)  # possible TypeError, AttributeError

        quartile = f'q{(100 - percentile.value - 1) // 25 + 1}'
    except (TypeError, AttributeError):
        pass

    authors = []
    try:
        for paper_author in paper.authors:
            authors.append({
                **author_formatter(paper_author.author),
                'authorNo': paper_author.author_no
            })
        authors.sort(key=lambda author: author['authorNo'])
    except (TypeError, AttributeError):
        pass

    return {
        'title': paper.title,
        'type': paper.type,
        'typeDescription': paper.type_description,
        'date': paper.get_year(),
        'doi': paper.doi,
        'openAccess': paper.open_access,
        'citedCnt': paper.cited_cnt,
        'source': paper.source.title,
        'quartile': quartile,
        'authors': authors,
        'retrievalTime': paper.retrieval_time
    }


def network_formatter(from_, to_dict: dict):
    result = []
    for k, v in to_dict.items():
        result.append({
            'from': {
                'first': from_.first_pref or from_.first,
                'last': from_.last_pref or from_.last,
                'idFrontend': from_.id_frontend,
            },
            'to': {
                'first': k.first_pref or k.first,
                'last': k.last_pref or k.last,
                'idFrontend': k.id_frontend
            },
            'value': v,
        })

    return result


def get_joint_papers(papers: list, co_author, format_results: bool = False):
    joint_papers = []
    for paper in papers:
        # possible AttributeError
        authors = [paper_author.author for paper_author in paper.authors]
        if co_author in authors:
            joint_papers.append(paper)
    if format_results:
        joint_papers = [paper_formatter(paper) for paper in joint_papers]

    return joint_papers


def get_author(id_frontend: str):
    response = initial_response
    try:
        id_ = authors_list_backend[id_frontend]  # possible KeyError
        author = a.get(id_)  # None if not found
        if author:
            response = author_formatter(
                author, department=True, profile=True, institution=True,
                home_institution=home_institution)
    except KeyError:
        pass  # return initial response

    return response


def get_author_papers(id_frontend: str):
    # returns a list of all papers for the author 'id_frontend'
    response = initial_response

    try:
        id_ = authors_list_backend[id_frontend]  # possible KeyError
        papers = p \
            .join((Paper_Author, Paper.authors)) \
            .join((Author, Paper_Author.author)) \
            .filter(Author.id == id_) \
            .all()
        # possible TypeError
        response = tuple(paper_formatter(p) for p in papers)
    except (KeyError, TypeError):
        pass

    return response


def get_author_papers_year(id_frontend: str, year: int):
    # returns a list of papers published in 'year' for the author 'id_frontend'
    response = initial_response

    # simple checks on incoming requests
    if not(isinstance(year, int)):
        return response
    if not(year_range[0] <= year <= year_range[1]):
        return response

    try:
        id_ = authors_list_backend[id_frontend]  # possible KeyError
        papers = p \
            .join((Paper_Author, Paper.authors)) \
            .join((Author, Paper_Author.author)) \
            .filter(Author.id == id_, extract('year', Paper.date) == year) \
            .all()
        # possible TypeError
        response = tuple(paper_formatter(p) for p in papers)
    except (KeyError, TypeError):
        pass

    return response


def get_author_papers_keyword(id_frontend: str, keyword: str):
    # returns a list of papers containing 'keyword' for the author 'id_frontend'
    response = initial_response
    if not(isinstance(keyword, str)):  # a simple check on incoming requests
        return response

    try:
        id_ = authors_list_backend[id_frontend]  # possible KeyError
        author = a.get(id_)

        # checking if the requested keyword is genuine
        # possible AttributeError
        keywords_list = list(
            author.get_keywords(threshold=keywords_threshold).keys())
        if not(keywords_list) or (keyword not in keywords_list):
            raise ValueError

        papers = p \
            .join((Paper_Author, Paper.authors)) \
            .join((Author, Paper_Author.author)) \
            .join((Keyword, Paper.keywords)) \
            .filter(Author.id == id_, Keyword.keyword == keyword) \
            .all()
        # possible TypeError
        response = tuple(paper_formatter(p) for p in papers)
    except (KeyError, AttributeError, ValueError, TypeError):
        pass

    return response


def get_author_papers_q(id_frontend: str, q: str):
    # returns a list of papers published in a 'q' journal of author 'id_frontend'
    response = initial_response
    # simple checks on incoming requests
    if not(isinstance(q, str)):
        return response
    if q.lower() not in ['q1', 'q2', 'q3', 'q4']:
        return response

    try:
        id_ = authors_list_backend[id_frontend]  # possible KeyError
        quartile = int(q[1])
        top_percentile = (4 - quartile) * 25 + 25 - 1
        bottom_percentile = (4 - quartile) * 25
        papers = p \
            .join((Paper_Author, Paper.authors)) \
            .join((Author, Paper_Author.author)) \
            .join((Source, Paper.source)) \
            .join((Source_Metric, Source.metrics)) \
            .filter(
                Author.id == id_,
                Source_Metric.type == 'Percentile',
                Source_Metric.year == extract('year', Paper.date),
                Source_Metric.value >= bottom_percentile,
                Source_Metric.value <= top_percentile
            ) \
            .all()
        # possible TypeError
        response = tuple(paper_formatter(p) for p in papers)
    except (KeyError, TypeError):
        pass

    return response


def get_author_papers_co_id(id_frontend: str, co_id: str):
    # returns joint papers between author 'id_frontend' and co_author co_id
    response = initial_response

    # simple checks on incoming requests
    if not(isinstance(co_id, str)):
        return response

    try:
        id_ = authors_list_backend[id_frontend]  # possible KeyError
        if co_id == id_frontend:
            raise ValueError
        if len(co_id) != len(id_frontend):  # possible TypeError
            raise ValueError
        co_author = a.filter(Author.id_frontend == co_id).first()
        if not co_author:
            raise ValueError

        papers = p \
            .join((Paper_Author, Paper.authors)) \
            .join((Author, Paper_Author.author)) \
            .filter(Author.id == id_) \
            .all()

        joint_papers = get_joint_papers(papers, co_author, format_results=True)
        response = tuple(joint_papers)
    except (KeyError, ValueError, TypeError, AttributeError):
        pass

    return response


def get_author_trend(id_frontend: str):
    response = initial_response
    try:
        id_ = authors_list_backend[id_frontend]  # possible KeyError
        author = a.get(id_)  # None if not found
        papers_trend = author.get_papers()  # possible AttributeError
        citations_trend = author.get_citations()

        trend = []
        for year in papers_trend:
            trend.append({
                'year':year,
                'papers': papers_trend[year],
                'citations': citations_trend[year]
            })
        response = tuple(trend)
    except (KeyError, AttributeError):
        pass

    return response


def get_author_keywords(id_frontend: str):
    response = initial_response

    try:
        id_ = authors_list_backend[id_frontend]  # possible KeyError
        author = a.get(id_)

        # possible AttributeError
        response = author.get_keywords(threshold=keywords_threshold)
    except (KeyError, AttributeError):
        pass

    return response


def get_author_qs(id_frontend: str):
    response = initial_response

    try:
        id_ = authors_list_backend[id_frontend]  # possible KeyError
        author = a.get(id_)  # None if not found
        metrics = [
            {'name': 'q1', 'percentiles': []},
            {'name': 'q2', 'percentiles': []},
            {'name': 'q3', 'percentiles': []},
            {'name': 'q4', 'percentiles': []},
        ]
        for i in author.get_metrics():  # possible AttributeError
            quartile = (100 - i[0] - 1) // 25 + 1
            metrics[quartile-1]['percentiles'].append({
                'name': f'p{i[0]}',
                'value': i[1]
            })

        response = tuple(metrics)
    except (KeyError, AttributeError):
        pass

    return response


def get_author_network(id_frontend: str):
    response = initial_response
    final_network = []

    try:
        # 1. get a list of (author)'s (papers)
        id_ = authors_list_backend[id_frontend]  # possible KeyError
        papers = p \
            .join((Paper_Author, Paper.authors)) \
            .join((Author, Paper_Author.author)) \
            .filter(Author.id == id_) \
            .all()

        # 2. add (author) to an (exclusion_list)
        author = a.get(id_)  # None if not found
        exclusion_list = [author]

        # 3. get a list of (author)'s all (co_authors), add to 'final_network'
        # possible AttributeError
        co_authors = author.get_co_authors(threshold=network_threshold)
        final_network.extend(network_formatter(author, co_authors))

        # 4. create a dictionary for storing the (co_authors) of each (co)
        co_network = {}

        # 5. for each (co):
        for co in co_authors:

            # 5.1. add (co) to (exclusion_list) and initiate (co_network)
            exclusion_list.append(co)
            co_network[co] = {}

            # 5.2. get a list of (joint_papers) with (author)
            joint_papers = get_joint_papers(papers, co_author=co)

            # 5.3. for each (paper) in (joint_papers)
            for paper in joint_papers:

                # 5.3.1. get a list of joint paper's (authors)
                authors = [
                    paper_author.author for paper_author in paper.authors]

                # 5.3.2 add (authors) to the (co_network) for (co)
                for auth in authors:
                    if auth in exclusion_list:
                        continue
                    try:
                        co_network[co][auth] += 1
                    except KeyError:
                        co_network[co][auth] = 1

            # 5.4 prune the (co_network) according to (network_threshold)
            co_network[co] = {k: v for k, v in co_network[co].items()
                              if v >= network_threshold}

        for co, network in co_network.items():
            final_network.extend(network_formatter(co, network))

        response = tuple(final_network)
    except (KeyError, AttributeError):
        pass

    return response


if __name__ == "__main__":
    pass
