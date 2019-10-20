from elsametric.models.author import Author


def get_author_jmetrics(session, id_backend: int):
    response = None

    try:
        author = session.query(Author).get(id_backend)  # None if not found
        metrics = [
            {'name': 'q1', 'percentiles': []},
            {'name': 'q2', 'percentiles': []},
            {'name': 'q3', 'percentiles': []},
            {'name': 'q4', 'percentiles': []},
            {'name': 'undefined', 'value': 0},
        ]
        for metric in author.get_metrics():  # possible AttributeError
            if metric[0] == 'Undefined':
                metrics[-1]['value'] = metric[1]
                continue

            quartile = (100 - metric[0] - 1) // 25 + 1
            metrics[quartile-1]['percentiles'].append({
                'name': f'p{metric[0]}',
                'value': metric[1]
            })

        response = tuple(metrics)
    except AttributeError:
        pass

    return response
