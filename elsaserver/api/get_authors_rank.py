from elsametric.models.author import Author

from .. import authors_backend

def get_authors_rank(session):
    stats = {
        'h_index_gsc': [],
        'i10_index_gsc': [],
        'total_papers': [],
        'total_citations': [],
    }

    for id_backend in authors_backend.values():
        try:
            author = session.query(Author).get(id_backend)  # None if not found
            # possible AttributeError
            stats['h_index_gsc'].append(author.h_index_gsc)
            stats['i10_index_gsc'].append(author.i10_index_gsc)
            # possible TypeError
            stats['total_papers'].append(sum(author.get_papers().values()))
            stats['total_citations'].append(
                sum(author.get_citations().values()))
        except (AttributeError, TypeError) as e:
            print(e)
            pass

    return stats
