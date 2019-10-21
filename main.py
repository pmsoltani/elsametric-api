import uvicorn
from fastapi import FastAPI

from elsaserver import \
    INITIAL_RESPONSE, \
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
    get_author_network
from elsaserver.api.get_authors_rank import get_authors_rank

from elsametric.models.base import Session

session = Session()
app = FastAPI()


@app.get('/')
async def home():
    return INITIAL_RESPONSE


@app.get('/a')
async def authors():
    return INITIAL_RESPONSE


@app.get('/a/list')
async def authors_list():
    return authors_frontend


@app.get('/a/rankings')
async def authors_rankings():
    return get_authors_rank(session)


@app.get('/a/{id_frontend}')
async def author_info(id_frontend: str):
    id_backend = front_back_mapper(id_frontend)
    return get_author_info(session, home_institution, id_backend)


@app.get('/a/{id_frontend}/papers')
async def author_papers(id_frontend: str, year: int = None, keyword: str = None,
                        metric: str = None, coID: str = None,):
    params_set = {year, keyword, metric, coID}
    if len(params_set) > 2:  # more than 1 parameter in the request
        return INITIAL_RESPONSE
    id_backend = front_back_mapper(id_frontend)
    if year:
        return get_author_papers_year(
            session, id_backend, year=year, year_range=YEAR_RANGE)
    if keyword:
        return get_author_papers_keyword(session, id_backend, keyword=keyword,
                                         keywords_threshold=KEYWORDS_THRESHOLD)
    if metric:
        return get_author_papers_jmetric(session, id_backend, metric=metric)
    if coID:
        return get_author_papers_co_id(session, id_backend, co_id=coID)
    return get_author_papers(session, id_backend)


@app.get('/a/{id_frontend}/trend')
async def author_trend(id_frontend: str):
    id_backend = front_back_mapper(id_frontend)
    return get_author_trend(session, id_backend)


@app.get('/a/{id_frontend}/keywords')
async def author_keywords(id_frontend: str):
    id_backend = front_back_mapper(id_frontend)
    return get_author_keywords(
        session, id_backend, keywords_threshold=KEYWORDS_THRESHOLD)


@app.get('/a/{id_frontend}/jmetrics')
async def author_jmetrics(id_frontend: str):
    id_backend = front_back_mapper(id_frontend)
    return get_author_jmetrics(session, id_backend)


@app.get('/a/{id_frontend}/network')
async def author_network(id_frontend: str):
    id_backend = front_back_mapper(id_frontend)
    return get_author_network(
        session, id_backend, collaboration_threshold=COLLABORATION_THRESHOLD,
        network_max_count=NETWORK_MAX_COUNT)


if __name__ == "__main__":
    uvicorn.run(f'{__name__}:app', host='0.0.0.0', port=8000, reload=True)
