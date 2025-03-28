init:
	# Only for new checkouts
	poetry install

run-debug:
	poetry run flask --app d6_api --debug run

run-production:
	poetry run gunicorn --chdir d6_api 'd6_api:create_app()'

shell:
	poetry run flask --app d6_api shell

# Don't forget to set ALEMBIC_MSG
db-upgrade:
	poetry run flask --app d6_api db revision "$(ALEMBIC_MSG)"
	poetry run flask --app d6_api db upgrade

db-dump:
	# Dump the database to data/data.json
	poetry run python -c "from d6_api import create_app; app=create_app(); from d6_api.util import dump_db; dump_db(app)"
	mv d6_api/data/data.json d6_api/data/data.json.tmp
	cat d6_api/data/data.json.tmp | jq . > d6_api/data/data.json
	rm d6_api/data/data.json.tmp

db-create:
	# Create the database from data/data.json
	poetry run python -c "from d6_api import create_app; app=create_app(); from d6_api.util import create_db; create_db(app)"
