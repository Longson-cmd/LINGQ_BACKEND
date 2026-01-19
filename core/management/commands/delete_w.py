from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Words, Word_Meanings, Word_Tags, Phrases, Phrase_Meanings, Phrase_Tags


class Command(BaseCommand):
    help = "Delete words and phrase data of test@example.com"

    def handle(self, *args, **options):
        try:
            user = User.objects.get(username = "test@example.com")
            Words.objects.filter(user = user).delete()
            Phrases.objects.filter(user = user).delete()
            self.stdout.write(self.style.SUCCESS(
                f"Delete data for  user successfully!"
            ))
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR("User test@example.com does not exist")
            )

