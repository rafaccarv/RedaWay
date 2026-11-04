from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from .models import AdminAuditEvent, Achievement, ActivityEvent, EssayExample, Exercise, ExerciseAttempt, ExerciseChoice, LearningPath, Lesson, LessonProgress, LessonReward, Module, RepertoireEntry, Source, StudyStats, Theme, User, UserAchievement, WeeklyGoal


@admin.register(User)
class AcademyUserAdmin(UserAdmin):
    ordering = ("email",)
    list_display = ("email", "first_name", "last_name", "is_staff", "is_active")
    search_fields = ("email", "first_name", "last_name")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Perfil", {"fields": ("first_name", "last_name")}),
        ("Permissões", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Datas", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = ((None, {"classes": ("wide",), "fields": ("email", "first_name", "password1", "password2")}),)
    filter_horizontal = ("groups", "user_permissions")
    username_field = "email"

    def get_fieldsets(self, request, obj=None):
        if request.user.is_superuser or obj is None:
            return super().get_fieldsets(request, obj)
        return (
            (None, {"fields": ("email", "password")}),
            ("Perfil", {"fields": ("first_name", "last_name")}),
            ("Conta", {"fields": ("is_active",)}),
            ("Datas", {"fields": ("last_login", "date_joined")}),
        )

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return super().get_readonly_fields(request, obj)
        return ("last_login", "date_joined")

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            if change:
                existing = User.objects.get(pk=obj.pk)
                obj.is_staff = existing.is_staff
                obj.is_superuser = existing.is_superuser
            else:
                obj.is_staff = False
                obj.is_superuser = False
        super().save_model(request, obj, form, change)
        AdminAuditEvent.objects.create(
            actor=request.user, action="update" if change else "create",
            object_type=obj._meta.label, object_id=str(obj.pk),
            changes={"fields": [name for name in form.changed_data if name not in {"password", "password1", "password2"}]},
        )
        if not change:
            student_group, _ = Group.objects.get_or_create(name="Estudante")
            obj.groups.add(student_group)

    def delete_model(self, request, obj):
        object_type, object_id = obj._meta.label, str(obj.pk)
        super().delete_model(request, obj)
        AdminAuditEvent.objects.create(actor=request.user, action="delete", object_type=object_type, object_id=object_id)


class AuditedAdminMixin:
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        AdminAuditEvent.objects.create(
            actor=request.user, action="update" if change else "create",
            object_type=obj._meta.label, object_id=str(obj.pk),
            changes={"fields": list(form.changed_data)},
        )

    def delete_model(self, request, obj):
        object_type, object_id = obj._meta.label, str(obj.pk)
        super().delete_model(request, obj)
        AdminAuditEvent.objects.create(actor=request.user, action="delete", object_type=object_type, object_id=object_id)

    def delete_queryset(self, request, queryset):
        object_type = queryset.model._meta.label
        object_ids = [str(pk) for pk in queryset.values_list("pk", flat=True)]
        super().delete_queryset(request, queryset)
        AdminAuditEvent.objects.bulk_create([
            AdminAuditEvent(actor=request.user, action="delete", object_type=object_type, object_id=object_id)
            for object_id in object_ids
        ])


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 0


class ModuleInline(admin.TabularInline):
    model = Module
    extra = 0


@admin.register(LearningPath)
class LearningPathAdmin(AuditedAdminMixin, admin.ModelAdmin):
    list_display = ("title", "order", "is_published")
    list_filter = ("is_published",)
    prepopulated_fields = {"slug": ("title",)}
    inlines = (ModuleInline,)


@admin.register(Module)
class ModuleAdmin(AuditedAdminMixin, admin.ModelAdmin):
    list_display = ("title", "path", "order")
    list_filter = ("path",)
    prepopulated_fields = {"slug": ("title",)}
    inlines = (LessonInline,)


@admin.register(Lesson)
class LessonAdmin(AuditedAdminMixin, admin.ModelAdmin):
    list_display = ("title", "module", "order", "is_published")
    list_filter = ("is_published", "module__path")
    search_fields = ("title", "summary", "body")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("sources",)


class ExerciseChoiceInline(admin.TabularInline):
    model = ExerciseChoice
    extra = 2


@admin.register(Exercise)
class ExerciseAdmin(AuditedAdminMixin, admin.ModelAdmin):
    list_display = ("title", "lesson", "is_published")
    list_filter = ("is_published",)
    prepopulated_fields = {"slug": ("title",)}
    inlines = (ExerciseChoiceInline,)


@admin.register(Theme)
class ThemeAdmin(AuditedAdminMixin, admin.ModelAdmin):
    list_display = ("title", "origin", "year", "difficulty", "is_published")
    list_filter = ("origin", "category", "difficulty", "year", "is_published")
    search_fields = ("title", "context", "central_problem")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("sources",)


@admin.register(RepertoireEntry)
class RepertoireAdmin(AuditedAdminMixin, admin.ModelAdmin):
    list_display = ("title", "category", "is_published")
    list_filter = ("category", "is_published")
    search_fields = ("title", "central_concept", "explanation")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("sources",)


@admin.register(Source)
class SourceAdmin(AuditedAdminMixin, admin.ModelAdmin):
    list_display = ("title", "institution", "edition", "is_official")
    list_filter = ("is_official", "institution")
    search_fields = ("title", "institution", "edition")


@admin.register(EssayExample)
class EssayExampleAdmin(AuditedAdminMixin, admin.ModelAdmin):
    list_display = ("title", "slug", "theme", "text_source", "source", "is_published")
    list_filter = ("is_published",)
    search_fields = ("title", "attribution", "full_text", "analysis")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Achievement)
class AchievementAdmin(AuditedAdminMixin, admin.ModelAdmin):
    list_display = ("title", "required_lessons")


class ReadOnlyStudentRecordAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(ActivityEvent)
class ActivityEventAdmin(ReadOnlyStudentRecordAdmin):
    list_display = ("user", "event_type", "label", "created_at")
    list_filter = ("event_type", "created_at")
    search_fields = ("user__email", "label")


@admin.register(ExerciseAttempt)
class ExerciseAttemptAdmin(ReadOnlyStudentRecordAdmin):
    list_display = ("user", "exercise", "is_correct", "attempted_at")
    list_filter = ("is_correct", "attempted_at")
    search_fields = ("user__email", "exercise__title")


@admin.register(WeeklyGoal)
class WeeklyGoalAdmin(ReadOnlyStudentRecordAdmin):
    list_display = ("user", "week_start", "target_lessons")
    search_fields = ("user__email",)


@admin.register(StudyStats)
class StudyStatsAdmin(ReadOnlyStudentRecordAdmin):
    list_display = ("user", "points", "current_streak", "longest_streak", "last_study_date")
    search_fields = ("user__email",)


@admin.register(LessonReward)
class LessonRewardAdmin(ReadOnlyStudentRecordAdmin):
    list_display = ("user", "lesson", "points", "awarded_at")
    search_fields = ("user__email", "lesson__title")


@admin.register(UserAchievement)
class UserAchievementAdmin(ReadOnlyStudentRecordAdmin):
    list_display = ("user", "achievement", "earned_at")
    search_fields = ("user__email", "achievement__title")


@admin.register(AdminAuditEvent)
class AdminAuditEventAdmin(ReadOnlyStudentRecordAdmin):
    list_display = ("actor", "action", "object_type", "object_id", "created_at")
    readonly_fields = ("actor", "action", "object_type", "object_id", "changes", "created_at")


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ("user", "lesson", "started_at", "completed_at")
    list_filter = ("completed_at",)
    search_fields = ("user__email", "lesson__title")
    readonly_fields = ("user", "lesson", "started_at", "completed_at", "last_position")

    def has_add_permission(self, request):
        return False
