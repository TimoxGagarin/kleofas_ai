migration:
	alembic revision --autogenerate -m "${MESSAGE}"

migrate:
	alembic upgrade head

rollback:
	alembic downgrade -1