from sqlalchemy import text

from flask_tutorial.extensions import db


class HealthService:
    def get_status(self) -> dict:
        database_status = "up" if self._ping_database() else "down"
        return {"status": "up", "database": database_status}

    def _ping_database(self) -> bool:
        try:
            db.session.execute(text("SELECT 1"))
            return True
        except Exception:  # noqa: BLE001 - any DB failure means "down", regardless of cause
            return False
