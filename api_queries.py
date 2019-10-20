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


from elsaserver.api.get_authors_list import get_authors_list
from elsaserver.api.get_author_info import get_author_info
from elsaserver.api.get_author_papers import get_author_papers
from elsaserver.api.get_author_papers_year import get_author_papers_year
from elsaserver.api.get_author_papers_keyword import get_author_papers_keyword
from elsaserver.api.get_author_papers_jmetric import get_author_papers_jmetric
from elsaserver.api.get_author_papers_co_id import get_author_papers_co_id
from elsaserver.api.get_author_trend import get_author_trend
from elsaserver.api.get_author_keywords import get_author_keywords
from elsaserver.api.get_author_jmetrics import get_author_jmetrics
from elsaserver.api.get_author_network import get_author_network


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
collaboration_threshold = config['collaboration_threshold']
network_max_count = config['network_max_count']


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

authors_list_backend, authors_list_frontend = get_authors_list(
    session, home_institution_id_scp)
authors_tuple_frontend = tuple(authors_list_frontend)


def front_back_mapper(id_frontend: str):
    if not isinstance(id_frontend, str):
        return None

    try:
        return authors_list_backend[id_frontend]
    except KeyError:
        return None


if __name__ == "__main__":
    pass
