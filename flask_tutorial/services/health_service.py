from flask_tutorial.repositories.health_repository import HealthRepository


class HealthService:
    def __init__(self, repository: HealthRepository | None = None):
        self.repository = repository or HealthRepository()

    def get_status(self) -> dict:
        database_status = "up" if self.repository.ping_database() else "down"
        return {"status": "up", "database": database_status}
