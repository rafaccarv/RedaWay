from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from academy import models


class Command(BaseCommand):
    help = "Cria os grupos iniciais com permissões limitadas; não cria contas nem senhas."

    def handle(self, *args, **options):
        student, _ = Group.objects.get_or_create(name="Estudante")
        editor, _ = Group.objects.get_or_create(name="Editor de conteúdo")
        admin_group, _ = Group.objects.get_or_create(name="Administrador")

        content_models = [models.LearningPath, models.Module, models.Lesson, models.Source, models.Theme, models.RepertoireEntry, models.Exercise, models.ExerciseChoice, models.EssayExample, models.Achievement]
        content_permissions = []
        for model in content_models:
            content_type = ContentType.objects.get_for_model(model)
            content_permissions.extend(Permission.objects.filter(content_type=content_type, codename__in=[f"{action}_{model._meta.model_name}" for action in ("view", "add", "change")]))
        editor.permissions.set(content_permissions)
        admin_permissions = list(content_permissions)
        for model in content_models:
            content_type = ContentType.objects.get_for_model(model)
            admin_permissions.extend(Permission.objects.filter(content_type=content_type, codename=f"delete_{model._meta.model_name}"))
        user_type = ContentType.objects.get_for_model(models.User)
        admin_permissions.extend(Permission.objects.filter(content_type=user_type, codename__in=["view_user", "change_user"]))
        for model in [models.LessonProgress, models.ActivityEvent, models.ExerciseAttempt, models.WeeklyGoal, models.StudyStats, models.LessonReward, models.UserAchievement, models.AdminAuditEvent]:
            content_type = ContentType.objects.get_for_model(model)
            admin_permissions.extend(Permission.objects.filter(content_type=content_type, codename=f"view_{model._meta.model_name}"))
        admin_group.permissions.set(admin_permissions)

        self.stdout.write(self.style.SUCCESS("Grupos Estudante, Editor de conteúdo e Administrador preparados."))
        self.stdout.write("A função superadministrador é representada somente por is_superuser e deve ser atribuída via createsuperuser.")
