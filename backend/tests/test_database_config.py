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
