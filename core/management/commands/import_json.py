from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Words, Word_Meanings, Word_Tags, Phrases, Phrase_Tags, Phrase_Meanings
import json
import os


default_data_path = os.path.join("core", "management",  "default_data.json")
class Command(BaseCommand):
    help = "Create one user and his data, then classify his vocabularies"

    def handle(self, *args, **options):

        try:
            first_user = User.objects.get(username = "test@example.com")
        except User.DoesNotExist:
            first_user = User.objects.create_user(
                username = "test@example.com",
                email = "test@example.com",
                password = "1234abcd"
            )

        if Words.objects.exists():
            print("words table was already imported")
        else:
            with open(default_data_path, "r", encoding="utf-8") as file:
                data = json.load(file)
                words_data = data["words"]
                phrases_data = data["phrases"]
            for status, item in enumerate(words_data):
                for idx, word in enumerate(item["en"]):
                    word_obj = Words.objects.create(
                        user = first_user,
                        word_key = word,
                        word_status = status
                    )

                    Word_Meanings.objects.create(
                        word = word_obj, 
                        meaning = item["vi"][idx]
                    )

                    Word_Tags.objects.create(
                        word = word_obj,
                        tag = item["type"][idx]
                    )
            
            for status, item in enumerate(phrases_data):
                
                for idx, word in enumerate(item["en"]):
                    phrase_obj = Phrases.objects.create(
                        user = first_user,
                        phrase = word,
                        phrase_status = status + 1
                    )

                    Phrase_Meanings.objects.create(
                        phrase = phrase_obj,
                        meaning = item["vi"][idx]

                    )

                    Phrase_Tags.objects.create(
                        phrase = phrase_obj,
                        tag = item["type"][idx]
                    )
            self.stdout.write(self.style.SUCCESS(
                f"Imported data for first user successfully!"
            ))