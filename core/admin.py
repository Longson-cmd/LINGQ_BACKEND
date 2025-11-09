from django.contrib import admin
from .models import (
    Words,
    Word_Meanings,
    Word_Tags,
    Phrases,
    Phrase_Meanings,
    Phrase_Tags,
    Lessons,
    UploadedAudios,
    UploadedText,
    CustomerProfile,
)

# Register each model
admin.site.register(Words)
admin.site.register(Word_Meanings)
admin.site.register(Word_Tags)
admin.site.register(Phrases)
admin.site.register(Phrase_Meanings)
admin.site.register(Phrase_Tags)
admin.site.register(Lessons)
admin.site.register(UploadedAudios)
admin.site.register(UploadedText)
admin.site.register(CustomerProfile)
