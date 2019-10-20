from elsametric.models.paper import Paper
from elsametric.models.associations import Paper_Author
from elsametric.models.author import Author

from ..helpers import network_formatter, network_pruner, get_joint_papers


def get_author_network(session, id_backend: int,
                       collaboration_threshold: int, network_max_count: int):
    response = None
    final_network = []

    try:
        # 1. get a list of (author)'s (papers)
        papers = session \
            .query(Paper) \
            .join((Paper_Author, Paper.authors)) \
            .join((Author, Paper_Author.author)) \
            .filter(Author.id == id_backend) \
            .all()  # empty list if not found

        # 2. add (author) to an (exclusion_list)
        author = session.query(Author).get(id_backend)  # None if not found
        exclusion_list = [author]

        # 3.1. get a list of (author)'s all (co_authors), add to 'final_network'
        # possible AttributeError
        co_authors = author.get_co_authors(threshold=collaboration_threshold)

        # 3.2. limiting the (co_authors) to be at most (network_max_count)
        while (len(co_authors) > network_max_count and
               len(set(co_authors.values())) > 1):
            co_authors = network_pruner(co_authors)

        final_network.extend(network_formatter(author, co_authors))

        # 4. create a dictionary for storing the (co_authors) of each (co)
        co_network = {}

        # 5. for each (co):
        for co in co_authors:

            # 5.1. add (co) to (exclusion_list) and initiate (co_network)
            exclusion_list.append(co)
            co_network[co] = {}

            # 5.2. get a list of (joint_papers) with (author)
            joint_papers = get_joint_papers(papers, co_author=co)

            # 5.3. for each (paper) in (joint_papers)
            for paper in joint_papers:

                # 5.3.1. get a list of joint paper's (authors)
                authors = [
                    paper_author.author for paper_author in paper.authors]

                # 5.3.2 add (authors) to the (co_network) for (co)
                for auth in authors:
                    if auth in exclusion_list:
                        continue
                    if auth not in co_authors.keys():
                        continue
                    try:
                        co_network[co][auth] += 1
                    except KeyError:
                        co_network[co][auth] = 1

            # 5.4 prune the (co_network) according to (collaboration_threshold)
            co_network[co] = {k: v for k, v in co_network[co].items()
                              if v >= collaboration_threshold}

        for co, network in co_network.items():
            final_network.extend(network_formatter(co, network))

        response = tuple(final_network)
    except AttributeError:
        pass

    return response
