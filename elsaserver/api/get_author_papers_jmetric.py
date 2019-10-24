from typing import Tuple

from .. import \
    Author, Paper, Paper_Author, Source, Source_Metric, \
    Session, extract
from ..helpers import paper_formatter


def get_author_papers_jmetric(
        db: Session, id_backend: int, jmetric: str) -> Tuple[dict]:
    # returns a list of author's papers published in journal with jmetric

    if not isinstance(jmetric, str):
        raise TypeError

    jmetric = jmetric.lower()
    allowed_metrics = tuple(
        [f'p{x}' for x in range(100)] +
        ['q1', 'q2', 'q3', 'q4'])
    if jmetric not in allowed_metrics:
        raise ValueError

    if jmetric[0] == 'p':  # received a percentile value
        top_percentile = bottom_percentile = jmetric[1:]

    if jmetric[0] == 'q':  # received a quartile value
        quartile = int(jmetric[1])
        top_percentile = (4 - quartile) * 25 + 25 - 1
        bottom_percentile = (4 - quartile) * 25

    papers = db \
        .query(Paper) \
        .join((Paper_Author, Paper.authors)) \
        .join((Author, Paper_Author.author)) \
        .join((Source, Paper.source)) \
        .join((Source_Metric, Source.metrics)) \
        .filter(
            Author.id == id_backend,
            Source_Metric.type == 'Percentile',
            Source_Metric.year == extract('year', Paper.date),
            Source_Metric.value >= bottom_percentile,
            Source_Metric.value <= top_percentile) \
        .all()  # empty list if not found
    # possible TypeError
    return tuple(paper_formatter(paper) for paper in papers)
