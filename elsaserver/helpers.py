from elsaserver import authors_backend


def author_formatter(author, department: bool = False,
                     institution: bool = False, home_institution=None,
                     profile: bool = False):
    # helper function
    result = {}
    if department:
        departments = []
        try:
            for d in author.departments:  # possible TypeError, AttributeError
                if d.name == 'Undefined':  # default initial department
                    continue
                departments.append({
                    'name': d.name,
                    'type': d.type,
                    'idFrontend': d.id_frontend
                })
            result['departments'] = departments
        except (TypeError, AttributeError):
            pass

    if institution:
        institutions = []
        try:
            # possible TypeError, AttributeError
            for i in author.get_institutions():
                if (home_institution) and (i != home_institution):
                    continue
                institutions.append(
                    {'name': i.name, 'idFrontend': i.id_frontend})
            result['institutions'] = institutions
        except (TypeError, AttributeError):
            pass

    if profile:
        profiles = []
        try:
            for prf in author.profiles:  # possible TypeError, AttributeError
                profiles.append(
                    {'type': prf.type, 'address': prf.address})
            result['contact'] = profiles
        except (TypeError, AttributeError):
            pass
    return {
        'idFrontend': author.id_frontend,
        'first': author.first_pref or author.first,
        'last': author.last_pref or author.last,
        'sex': author.sex,
        'type': author.type,
        'rank': author.rank,
        **result
    }


def paper_formatter(paper):
    # TODO: What if paper is None?
    percentile = None
    quartile = None
    try:
        percentile = next(filter(
            lambda m: m.type == 'Percentile' and m.year == paper.get_year(),
            paper.source.metrics
        ), None)  # possible TypeError, AttributeError

        quartile = f'q{(100 - percentile.value - 1) // 25 + 1}'
    except (TypeError, AttributeError):
        pass

    authors = []
    try:
        for paper_author in paper.authors:
            authors.append({
                **author_formatter(paper_author.author),
                'authorNo': paper_author.author_no
            })
        authors.sort(key=lambda author: author['authorNo'])
    except (TypeError, AttributeError):
        pass

    return {
        'title': paper.title,
        'type': paper.type,
        'typeDescription': paper.type_description,
        'date': paper.get_year(),
        'doi': paper.doi,
        'openAccess': paper.open_access,
        'citedCnt': paper.cited_cnt,
        'source': paper.source.title,
        'quartile': quartile,
        'authors': authors,
        'retrievalTime': paper.retrieval_time
    }


def network_formatter(from_author, to_authors: dict):
    result = []
    for k, v in to_authors.items():
        result.append({
            'from': {
                'first': from_author.first_pref or from_author.first,
                'last': from_author.last_pref or from_author.last,
                'idFrontend': from_author.id_frontend,
            },
            'to': {
                'first': k.first_pref or k.first,
                'last': k.last_pref or k.last,
                'idFrontend': k.id_frontend
            },
            'value': v,
        })

    return result


def network_pruner(network: dict):
    if not network:
        return network
    min_value = min(network.values())
    return {k: v for k, v in network.items() if v > min_value}


def get_joint_papers(papers: list, co_author, format_results: bool = False):
    # TODO: What if papers or co_author is None?
    joint_papers = []
    for paper in papers:
        # possible AttributeError
        authors = [paper_author.author for paper_author in paper.authors]
        if co_author in authors:
            joint_papers.append(paper)
    if format_results:
        joint_papers = [paper_formatter(paper) for paper in joint_papers]

    return joint_papers


def front_back_mapper(id_frontend: str):
    if not isinstance(id_frontend, str):
        return None

    try:
        return authors_backend[id_frontend]
    except KeyError:
        return None
