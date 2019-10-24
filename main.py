"""Main API file which employs FastAPI."""

from enum import Enum
from typing import Iterator

import uvicorn
from fastapi import FastAPI, Depends, Path, Query, HTTPException
from sqlalchemy.orm import Session

from elsaserver import \
    VARCHAR_COLUMN_LENGTH as ID_LEN, \
    YEAR_RANGE, \
    KEYWORDS_THRESHOLD, \
    COLLABORATION_THRESHOLD, \
    NETWORK_MAX_COUNT, \
    SessionLocal, \
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

# from elsametric.models.base import SessionLocal


# Dependency
def get_db() -> Iterator[Session]:
    """Manage instances of SQLAlchemy's Sessions to interact with db."""
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

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
    """Restricts requests' paths to pre-defined values."""

    trend = 'trend'
    keywords = 'keywords'
    network = 'network'
    jmetrics = 'jmetrics'
    stats = 'stats'
    papers = 'papers'


@app.get('/')
async def home():
    """Manage API route for root."""
    raise HTTPException(**PAGE404)


@app.get('/a')
async def authors():
    """Manage API route for /a."""
    raise HTTPException(**PAGE404)


@app.get('/a/list')
async def authors_list():
    """Manage API route for /a/list."""
    return authors_frontend


# @app.get('/a/rankings')
# async def authors_rankings():
#     return get_authors_rank(session)


@app.get('/a/{id_frontend}')
def author_info(
        id_frontend: str = Path(..., min_length=ID_LEN, max_length=ID_LEN),
        db: Session = Depends(get_db)):
    """Manage API route for /a/{id_frontend}."""
    try:
        id_backend = front_back_mapper(id_frontend)
        response = get_author_info(db, home_institution, id_backend)
        if not response:
            raise KeyError
        return response
    except (KeyError, TypeError):
        raise HTTPException(**AUTHOR404)


@app.get('/a/{id_frontend}/{author_path}')
def get_author_path(
        *, id_frontend: str = Path(..., min_length=ID_LEN, max_length=ID_LEN),
        author_path: AuthorPath,
        year: int = Query(None, ge=YEAR_RANGE[0], le=YEAR_RANGE[1]),
        keyword: str = None, jmetric: str = None, coID: str = None,
        db: Session = Depends(get_db)):
    """Manage API route for /a/{id_frontend}/{author_path}."""
    if author_path == AuthorPath.trend:
        try:
            id_backend = front_back_mapper(id_frontend)
            return get_author_trend(db, id_backend)
        except (KeyError, AttributeError):
            raise HTTPException(**AUTHOR404)

    if author_path == AuthorPath.keywords:
        try:
            id_backend = front_back_mapper(id_frontend)
            return get_author_keywords(db, id_backend,
                                       keywords_threshold=KEYWORDS_THRESHOLD)
        except (KeyError, AttributeError):
            raise HTTPException(**AUTHOR404)

    if author_path == AuthorPath.network:
        try:
            id_backend = front_back_mapper(id_frontend)
            return get_author_network(
                db, id_backend,
                collaboration_threshold=COLLABORATION_THRESHOLD,
                network_max_count=NETWORK_MAX_COUNT)
        except (KeyError, AttributeError):
            raise HTTPException(**AUTHOR404)

    if author_path == AuthorPath.jmetrics:
        try:
            id_backend = front_back_mapper(id_frontend)
            return get_author_jmetrics(db, id_backend)
        except (KeyError, AttributeError):
            raise HTTPException(**AUTHOR404)

    if author_path == AuthorPath.stats:
        try:
            id_backend = front_back_mapper(id_frontend)
            return get_author_stats(db, id_backend)
        except (KeyError, AttributeError):
            raise HTTPException(**AUTHOR404)

    if author_path == AuthorPath.papers:
        try:
            params_set = {year, keyword, jmetric, coID}
            if len(params_set) > 2:
                # bad request (more than 1 parameter supplied)
                raise HTTPException(**PAPERS404)

            id_backend = front_back_mapper(id_frontend)
            if year:
                return get_author_papers_year(
                    db, id_backend, year=year, year_range=YEAR_RANGE)
            if keyword:
                return get_author_papers_keyword(
                    db, id_backend, keyword=keyword,
                    keywords_threshold=KEYWORDS_THRESHOLD)
            if jmetric:
                return get_author_papers_jmetric(
                    db, id_backend, jmetric=jmetric)
            if coID:
                return get_author_papers_co_id(
                    db, id_backend, co_id=coID)
            return get_author_papers(db, id_backend)
        except (KeyError, ValueError, TypeError):
            raise HTTPException(**PAPERS404)
    raise HTTPException(**AUTHOR404)


if __name__ == "__main__":
    uvicorn.run(f'{__name__}:app', host='0.0.0.0', port=8000, reload=True)
