from django.contrib import admin

from .models import Choice, Question


# Add Choice under Question
# class ChoiceInline(admin.StackedInline):
class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 0


# customize question form in admin
class QuestionAdmin(admin.ModelAdmin):
    # fields = ['pub_date', 'question_text']

    # add "Date Information" section title
    fieldsets = [
        (None, {"fields": ["question_text"]}),
        ("Date Information", {"fields": ["pub_date"]}),
    ]
    inlines = [ChoiceInline]

    # add columns to listing table
    list_display = ["question_text", "pub_date", "was_published_recently"]

    # filter
    list_filter = ["pub_date"]


admin.site.register(Question, QuestionAdmin)
# admin.site.register(Choice)
