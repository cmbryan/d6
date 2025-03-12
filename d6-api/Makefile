init:
	# Only for new checkouts
	poetry install

run-debug:
	poetry run flask --app d6_api --debug run

run-production:
	poetry run gunicorn --chdir d6_api 'd6_api:create_app()'