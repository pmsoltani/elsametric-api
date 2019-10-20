from elsametric.models.author import Author
from elsametric.models.department import Department
from elsametric.models.institution import Institution


def get_authors_list(session, institution_id_scp):
    # This function is not directly involved with the frontend

    # get a list of all faculty members of the home_institution
	authors = session \
		.query(Author) \
		.with_entities(
			Author.id,
			Author.id_frontend,
			Author.first,
			Author.last,
			Author.first_pref,
			Author.last_pref) \
		.distinct() \
		.join((Department, Author.departments)) \
		.join((Institution, Department.institution)) \
		.filter(
			Author.type == 'Faculty',
			Institution.id_scp == institution_id_scp) \
		.order_by(Author.last) \
		.all()

	response_backend = {}  # used to map the id_frontend to id, for backend only
	response_frontend = []  # returned to the frontend
	for author in authors:
		response_backend[author.id_frontend] = author.id

		response_frontend.append({
			'idFrontend': author.id_frontend,
			'first': author.first_pref or author.first,
			'last': author.last_pref or author.last
		})
	return response_backend, response_frontend
