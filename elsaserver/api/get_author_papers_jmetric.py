from sqlalchemy import extract

from elsametric.models.paper import Paper
from elsametric.models.associations import Paper_Author
from elsametric.models.author import Author
from elsametric.models.source import Source
from elsametric.models.source_metric import Source_Metric

from ..helpers import paper_formatter


def get_author_papers_jmetric(session, id_backend: int, metric: str):
    # returns a list of author's papers published in journal with metric
    response = None
    # simple checks on incoming requests
    if not isinstance(metric, str):
        return response

    metric = metric.lower()
    allowed_metrics = tuple(
        [f'p{x}' for x in range(100)] +
        ['q1', 'q2', 'q3', 'q4'])
    if metric not in allowed_metrics:
        return response

    try:
        if metric[0] == 'p':  # received a percentile value
            # received a quartile value
            top_percentile = bottom_percentile = metric[1:]
        if metric[0] == 'q':
            quartile = int(metric[1])
            top_percentile = (4 - quartile) * 25 + 25 - 1
            bottom_percentile = (4 - quartile) * 25
        papers = session \
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
        response = tuple(paper_formatter(paper) for paper in papers)
    except TypeError:
        pass

    return response
