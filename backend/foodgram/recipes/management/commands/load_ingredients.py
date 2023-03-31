from django.core.management.base import BaseCommand
from csv import DictReader

from recipes.models import Ingredients

ALREDY_LOADED_ERROR_MESSAGE = """
If you need to reload child data from a CSV file,
first delete the database file to destroy the database.
Then run `python manage.py move" for a new empty
database with tables"""


class Command(BaseCommand):
    help = 'Загрузка ингредиентов'

    def handle(self, *args, **kwargs):
        if Ingredients.objects.exists():
            print('child data already loaded...exiting.')
            print(ALREDY_LOADED_ERROR_MESSAGE)
            return
        print("Loading childrens data")

        for row in DictReader(
            open('../ingredients.csv', encoding="utf8")
        ):
            child = Ingredients(
                name=row['name'],
                measurement_unit=row['measurement_unit'],
            )
            child.save()
