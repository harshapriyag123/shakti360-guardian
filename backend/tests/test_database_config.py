import os
import subprocess
import sys


def test_zerops_postgresql_url_selects_psycopg3_driver():
    env = {**os.environ, "DATABASE_URL": "postgresql://db:secret@db:5432/db"}
    result = subprocess.run(
        [sys.executable, "-c", "from app.database import DATABASE_URL; print(DATABASE_URL)"],
        cwd=os.path.dirname(os.path.dirname(__file__)),
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.strip() == "postgresql+psycopg://db:secret@db:5432/db"


def test_unresolved_railway_reference_falls_back_to_sqlite():
    env = {**os.environ, "DATABASE_URL": "${{Postgres.DATABASE_URL}}"}
    result = subprocess.run(
        [sys.executable, "-c", "from app.database import DATABASE_URL; print(DATABASE_URL)"],
        cwd=os.path.dirname(os.path.dirname(__file__)),
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.strip() == "sqlite:///./shakti360.db"
    assert "unresolved service reference" in result.stderr


def test_malformed_database_url_falls_back_to_sqlite():
    env = {**os.environ, "DATABASE_URL": "not a database url"}
    result = subprocess.run(
        [sys.executable, "-c", "from app.database import DATABASE_URL; print(DATABASE_URL)"],
        cwd=os.path.dirname(os.path.dirname(__file__)),
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.strip() == "sqlite:///./shakti360.db"
    assert "malformed" in result.stderr
