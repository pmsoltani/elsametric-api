"""Imports definitions and creates variables."""

import io
import json
from pathlib import Path

from elsametric.models.base import SessionLocal, VARCHAR_COLUMN_LENGTH
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


# ==============================================================================
# Config
# ==============================================================================


CURRENT_DIR = Path.cwd()
with io.open(CURRENT_DIR / 'config.json', 'r') as config_file:
    config = json.load(config_file)
config = config['api']

HOME_INSTITUTION_ID_SCP = config['home_institution_id_scp']
HOME_COUNTRY_DOMAIN = config['home_country_domain']
YEAR_RANGE = config['year_range']
KEYWORDS_THRESHOLD = config['keywords_threshold']
COLLABORATION_THRESHOLD = config['collaboration_threshold']
NETWORK_MAX_COUNT = config['network_max_count']


# ==============================================================================
# Functions & Variables
# ==============================================================================


db = SessionLocal()
home_country = db \
    .query(Country) \
    .filter(Country.domain == HOME_COUNTRY_DOMAIN) \
    .first()
home_institution = db \
    .query(Institution) \
    .filter(Institution.id_scp == HOME_INSTITUTION_ID_SCP) \
    .first()

authors_backend, authors_frontend = get_institution_authors(
    db, HOME_INSTITUTION_ID_SCP)
