from enum import Enum
import uvicorn
from fastapi import FastAPI, HTTPException

from elsaserver import \
    YEAR_RANGE, \
    KEYWORDS_THRESHOLD, \
    COLLABORATION_THRESHOLD, \
    NETWORK_MAX_COUNT, \
    authors_frontend, \
    front_back_mapper, \
    home_institution, \
    get_author_info, \
    get_author_papers, \
    get_author_papers_year, \
    get_author_papers_keyword, \
    get_author_papers_jmetric, \
    get_author_papers_co_id, \
    get_author_trend, \
    get_author_keywords, \
    get_author_jmetrics, \
    get_author_network, \
    get_author_stats

from elsametric.models.base import Session

session = Session()
app = FastAPI()
PAGE404 = {
    'status_code': 404,
    'detail': 'The requested page not found.'
}
AUTHOR404 = {
    'status_code': 404,
    'detail': 'The requested author not found.'
}
PAPERS404 = {
    'status_code': 404,
    'detail': 'The requested paper(s) not found.'
}


class AuthorPath(str, Enum):
    trend = 'trend'
    keywords = 'keywords'
    network = 'network'
    jmetrics = 'jmetrics'
    stats = 'stats'
    papers = 'papers'


@app.get('/')
async def home():
    raise HTTPException(**PAGE404)


@app.get('/a')
async def authors():
    raise HTTPException(**PAGE404)


@app.get('/a/list')
async def authors_list():
    return authors_frontend


# @app.get('/a/rankings')
# async def authors_rankings():
#     return get_authors_rank(session)


@app.get('/a/{id_frontend}')
async def author_info(id_frontend: str):
    try:
        id_backend = front_back_mapper(id_frontend)
        response = get_author_info(session, home_institution, id_backend)
        if not response:
            raise KeyError
        return response
    except (KeyError, TypeError):
        raise HTTPException(**AUTHOR404)


@app.get('/a/{id_frontend}/{author_path}')
async def get_author_path(id_frontend: str, author_path: AuthorPath,
                          year: int = None, keyword: str = None,
                          metric: str = None, coID: str = None):
    print(locals())
    if author_path == AuthorPath.trend:
        try:
            id_backend = front_back_mapper(id_frontend)
            return get_author_trend(session, id_backend)
        except (KeyError, AttributeError):
            raise HTTPException(**AUTHOR404)

    if author_path == AuthorPath.keywords:
        try:
            id_backend = front_back_mapper(id_frontend)
            return get_author_keywords(session, id_backend,
                                       keywords_threshold=KEYWORDS_THRESHOLD)
        except (KeyError, AttributeError):
            raise HTTPException(**AUTHOR404)

    if author_path == AuthorPath.network:
        try:
            id_backend = front_back_mapper(id_frontend)
            return get_author_network(
                session, id_backend,
                collaboration_threshold=COLLABORATION_THRESHOLD,
                network_max_count=NETWORK_MAX_COUNT)
        except (KeyError, AttributeError):
            raise HTTPException(**AUTHOR404)

    if author_path == AuthorPath.jmetrics:
        try:
            id_backend = front_back_mapper(id_frontend)
            return get_author_jmetrics(session, id_backend)
        except (KeyError, AttributeError):
            raise HTTPException(**AUTHOR404)

    if author_path == AuthorPath.stats:
        try:
            id_backend = front_back_mapper(id_frontend)
            return get_author_stats(session, id_backend)
        except (KeyError, AttributeError):
            raise HTTPException(**AUTHOR404)

    if author_path == AuthorPath.papers:
        try:
            params_set = {year, keyword, metric, coID}
            if len(params_set) > 2:
                # bad request (more than 1 parameter supplied)
                raise HTTPException(**PAPERS404)

            id_backend = front_back_mapper(id_frontend)
            if year:
                return get_author_papers_year(
                    session, id_backend, year=year, year_range=YEAR_RANGE)
            if keyword:
                return get_author_papers_keyword(
                    session, id_backend, keyword=keyword,
                    keywords_threshold=KEYWORDS_THRESHOLD)
            if metric:
                return get_author_papers_jmetric(
                    session, id_backend, metric=metric)
            if coID:
                return get_author_papers_co_id(session, id_backend, co_id=coID)
            return get_author_papers(session, id_backend)
        except (KeyError, ValueError, TypeError):
            raise HTTPException(**PAPERS404)
    raise HTTPException(**AUTHOR404)


if __name__ == "__main__":
    uvicorn.run(f'{__name__}:app', host='0.0.0.0', port=8000, reload=True)
