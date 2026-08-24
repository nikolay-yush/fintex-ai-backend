sudo docker compose exec --env-file .env.test backend uv run pytest tests/features/auth/unit/security/test_password.py -v
