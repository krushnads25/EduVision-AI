from app.models.vacancy import Vacancy
from app.repositories.base import BaseRepository


class VacancyRepository(BaseRepository[Vacancy]):
    def __init__(self):
        super().__init__(Vacancy)
