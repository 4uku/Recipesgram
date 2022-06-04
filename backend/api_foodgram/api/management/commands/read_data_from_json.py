import json

from django.core.management.base import BaseCommand

from api.models import Ingredient, Tag


class Command(BaseCommand):

    def add_objects(self, model, reader):
        model_object = model
        for row in reader:
            model_object.objects.create(**row)
        return f'Database Update {model}'

    def handle(self, *args, **options):
        with open('data/ingredients.json', 'rb') as ingredients:
            reader_ingredients = json.load(ingredients)
        with open('data/tags.json', 'rb') as tags:
            reader_tags = json.load(tags)
        self.stdout.write(
            self.style.SUCCESS(
                self.add_objects(Ingredient, reader_ingredients)))
        self.stdout.write(
            self.style.SUCCESS(
                self.add_objects(Tag, reader_tags)))
