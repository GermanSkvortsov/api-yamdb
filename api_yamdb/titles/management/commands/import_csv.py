import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from titles.models import Category, Genre, Title
from users.models import User
from reviews.models import Review, Comment


FIELD_MAPPING = {
    'category': 'category_id',
    'author': 'author_id',
    'review_id': 'review_id',
}


class Command(BaseCommand):
    help = 'Импорт данных из CSV файлов'

    def import_row(self, model, row):
        """Логика обработки одной строки CSV."""
        for old_name, new_name in FIELD_MAPPING.items():
            if old_name in row:
                row[new_name] = row.pop(old_name)
        if model == User and not row.get('password'):
            row['password'] = 'not_set_in_csv_123'
        obj_id = row.pop('id')
        model.objects.update_or_create(id=obj_id, defaults=row)

    def handle(self, *args, **options):
        data_files = [
            (User, 'users.csv'),
            (Category, 'category.csv'),
            (Genre, 'genre.csv'),
            (Title, 'titles.csv'),
            (Review, 'review.csv'),
            (Comment, 'comments.csv'),
        ]

        for model, filename in data_files:
            path = os.path.join(settings.BASE_DIR, 'static/data', filename)
            if not os.path.exists(path):
                continue
            with open(path, mode='r', encoding='utf-8') as f:
                for row in csv.DictReader(f):
                    self.import_row(model, row)
            self.stdout.write(self.style.SUCCESS(f'Загружен {filename}'))
        self.import_m2m()

    def import_m2m(self):
        """Импорт связей ManyToMany."""
        path = os.path.join(settings.BASE_DIR, 'static/data/genre_title.csv')
        if os.path.exists(path):
            with open(path, mode='r', encoding='utf-8') as f:
                for row in csv.DictReader(f):
                    title = Title.objects.get(id=row['title_id'])
                    title.genre.add(Genre.objects.get(id=row['genre_id']))
