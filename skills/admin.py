from django.contrib import admin
from .models import Skill, Profile, ExchangeRequest


# Admin site customization
admin.site.site_header = "SkillSwap Administration"
admin.site.site_title = "SkillSwap Admin"
admin.site.index_title = "SkillSwap Admin Dashboard"


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "bio")
    search_fields = ("user__username", "user__first_name")
    filter_horizontal = ("skills_to_teach", "skills_to_learn")


@admin.register(ExchangeRequest)
class ExchangeRequestAdmin(admin.ModelAdmin):
    list_display = (
        "sender",
        "receiver",
        "status",
        "created_at",
    )

    list_filter = ("status", "created_at")
    search_fields = (
        "sender__user__username",
        "receiver__user__username",
    )