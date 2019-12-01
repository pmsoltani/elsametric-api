"""Imports definitions and creates variables."""

import io
import json
from pathlib import Path

from environs import Env

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


env = Env()
env.read_env()

BACKEND_CORS_ORIGINS = env('BACKEND_CORS_ORIGINS', '')

with env.prefixed('API_'):

    HOME_INSTITUTION_ID_SCP = env.int("HOME_INSTITUTION_ID_SCP")
    HOME_COUNTRY_DOMAIN = env("HOME_COUNTRY_DOMAIN")
    YEAR_RANGE = env.list("YEAR_RANGE", subcast=int)
    KEYWORDS_THRESHOLD = env.int("KEYWORDS_THRESHOLD")
    COLLABORATION_THRESHOLD = env.int("COLLABORATION_THRESHOLD")
    NETWORK_MAX_COUNT = env.int("NETWORK_MAX_COUNT")


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
