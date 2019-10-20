import io
import json
from pathlib import Path

# from sqlalchemy import extract

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


from elsaserver.api.get_institution_authors import get_institution_authors
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


CURRENT_DIR = Path.cwd()
with io.open(CURRENT_DIR / 'config.json', 'r') as config_file:
    config = json.load(config_file)
config = config['api']

HOME_INSTITUTION_ID_SCP = config['home_institution_id_scp']
YEAR_RANGE = config['year_range']
KEYWORDS_THRESHOLD = config['keywords_threshold']
COLLABORATION_THRESHOLD = config['collaboration_threshold']
NETWORK_MAX_COUNT = config['network_max_count']
INITIAL_RESPONSE = {'message': 'not found', 'code': 404}


# ==============================================================================
# Functions & Variables
# ==============================================================================


session = Session()
home_institution = session \
    .query(Institution) \
    .filter(Institution.id_scp == HOME_INSTITUTION_ID_SCP) \
    .first()

authors_backend, authors_frontend = get_institution_authors(
    session, HOME_INSTITUTION_ID_SCP)


def front_back_mapper(id_frontend: str):
    if not isinstance(id_frontend, str):
        return None

    try:
        return authors_backend[id_frontend]
    except KeyError:
        return None


if __name__ == "__main__":
    pass
