from typing import Tuple

from .. import Author, Session


def get_author_jmetrics(db: Session, id_backend: int) -> Tuple[dict]:
    metrics = [
        {'name': 'q1', 'percentiles': []},
        {'name': 'q2', 'percentiles': []},
        {'name': 'q3', 'percentiles': []},
        {'name': 'q4', 'percentiles': []},
        {'name': 'undefined', 'value': 0},
    ]
    author = db.query(Author).get(id_backend)  # None if not found
    for metric in author.get_metrics():  # possible AttributeError
        if metric[0] == 'Undefined':
            metrics[-1]['value'] = metric[1]
            continue

        quartile = (100 - metric[0] - 1) // 25 + 1
        metrics[quartile-1]['percentiles'].append({
            'name': f'p{metric[0]}',
            'value': metric[1]
        })

    return tuple(metrics)
