from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.db.models.functions import Lower
from pathlib import Path
from uuid import uuid4
from django.utils import timezone


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Informe um e-mail.")
        email = self.normalize_email(email).lower()
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True or extra_fields.get("is_superuser") is not True:
            raise ValueError("Superusuário precisa ter is_staff e is_superuser ativos.")
        return self._create_user(email, password, **extra_fields)


def profile_photo_upload_to(instance, filename):
    suffix = Path(filename).suffix.lower()
    return f"profile-photos/{uuid4().hex}{suffix}"


class User(AbstractUser):
    username = None
    email = models.EmailField("e-mail", unique=True)
    first_name = models.CharField("nome", max_length=150)
    last_name = models.CharField("sobrenome", max_length=150, blank=True)
    photo = models.ImageField("foto de perfil", upload_to=profile_photo_upload_to, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name"]
    objects = UserManager()

    class Meta:
        verbose_name = "estudante"
        verbose_name_plural = "estudantes"
        constraints = [models.UniqueConstraint(Lower("email"), name="unique_user_email_case_insensitive")]

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        previous_photo = None
        if self.pk:
            previous_photo = type(self).objects.filter(pk=self.pk).values_list("photo", flat=True).first()
        self.email = self.email.strip().lower()
        super().save(*args, **kwargs)
        if previous_photo and previous_photo != self.photo.name:
            self.photo.storage.delete(previous_photo)


class Note(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notes")
    title = models.CharField("título", max_length=160)
    topic = models.CharField("tema", max_length=120, blank=True)
    body = models.TextField("conteúdo", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at", "title"]
        verbose_name = "nota pessoal"
        verbose_name_plural = "notas pessoais"

    def __str__(self):
        return self.title


class LearningPath(models.Model):
    title = models.CharField("título", max_length=160)
    slug = models.SlugField(unique=True)
    summary = models.CharField("resumo", max_length=260)
    description = models.TextField("descrição", blank=True)
    order = models.PositiveSmallIntegerField(default=0)
    is_published = models.BooleanField("publicada", default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "title"]
        verbose_name = "trilha"
        verbose_name_plural = "trilhas"

    def __str__(self):
        return self.title


class Module(models.Model):
    path = models.ForeignKey(LearningPath, on_delete=models.CASCADE, related_name="modules")
    title = models.CharField("título", max_length=160)
    slug = models.SlugField()
    summary = models.CharField("resumo", max_length=260, blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "title"]
        constraints = [models.UniqueConstraint(fields=["path", "slug"], name="unique_module_slug_per_path")]
        verbose_name = "módulo"
        verbose_name_plural = "módulos"

    def __str__(self):
        return f"{self.path}: {self.title}"


class Lesson(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField("título", max_length=180)
    slug = models.SlugField()
    summary = models.CharField("resumo", max_length=260, blank=True)
    objective = models.CharField("objetivo de aprendizagem", max_length=260, blank=True)
    body = models.TextField("conteúdo", blank=True)
    reference_note = models.CharField("referência e páginas", max_length=240, blank=True)
    order = models.PositiveSmallIntegerField(default=0)
    estimated_minutes = models.PositiveSmallIntegerField(default=8)
    is_published = models.BooleanField("publicada", default=False)
    sources = models.ManyToManyField("Source", blank=True, related_name="lessons")

    class Meta:
        ordering = ["order", "title"]
        constraints = [models.UniqueConstraint(fields=["module", "slug"], name="unique_lesson_slug_per_module")]
        verbose_name = "aula"
        verbose_name_plural = "aulas"

    def __str__(self):
        return self.title


class LessonProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="lesson_progress")
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="student_progress")
    started_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_position = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "lesson"], name="unique_user_lesson_progress")]
        verbose_name = "progresso da aula"
        verbose_name_plural = "progressos das aulas"

    @property
    def is_complete(self):
        return self.completed_at is not None

    def __str__(self):
        return f"{self.user}: {self.lesson}"


class Source(models.Model):
    title = models.CharField("documento ou fonte", max_length=220)
    institution = models.CharField("instituição/autoria", max_length=180)
    edition = models.CharField("edição/ano", max_length=80, blank=True)
    url = models.URLField("link da fonte", blank=True)
    page = models.CharField("página ou referência", max_length=40, blank=True)
    excerpt = models.TextField("trecho de referência", blank=True)
    is_official = models.BooleanField("fonte oficial", default=False)

    class Meta:
        ordering = ["institution", "title"]
        verbose_name = "fonte"
        verbose_name_plural = "fontes"

    def __str__(self):
        return f"{self.institution}: {self.title}"


class Theme(models.Model):
    class Difficulty(models.TextChoices):
        INTRODUCTORY = "introductory", "Inicial"
        INTERMEDIATE = "intermediate", "Intermediário"
        ADVANCED = "advanced", "Avançado"

    class Origin(models.TextChoices):
        OFFICIAL = "official", "Oficial"
        REDAWAY = "redaway", "Autoral RedaWay"

    title = models.CharField("título", max_length=200)
    slug = models.SlugField(unique=True)
    category = models.CharField("categoria", max_length=100)
    difficulty = models.CharField(max_length=20, choices=Difficulty.choices, default=Difficulty.INTRODUCTORY)
    year = models.PositiveSmallIntegerField("ano", null=True, blank=True)
    origin = models.CharField(max_length=12, choices=Origin.choices, default=Origin.REDAWAY)
    context = models.TextField("contextualização", blank=True)
    central_problem = models.TextField("problema central", blank=True)
    reflection_questions = models.TextField("questões para reflexão", blank=True)
    argument_paths = models.TextField("caminhos argumentativos", blank=True)
    essay_prompt = models.TextField("proposta de redação", blank=True)
    sources = models.ManyToManyField(Source, blank=True, related_name="themes")
    repertoires = models.ManyToManyField("RepertoireEntry", blank=True, related_name="themes")
    is_published = models.BooleanField("publicado", default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-year", "title"]
        verbose_name = "tema"
        verbose_name_plural = "temas"

    def __str__(self):
        return self.title


class RepertoireEntry(models.Model):
    class Category(models.TextChoices):
        PHILOSOPHY = "philosophy", "Filosofia"
        SOCIOLOGY = "sociology", "Sociologia"
        HISTORY = "history", "História"
        LITERATURE = "literature", "Literatura"
        CINEMA = "cinema", "Cinema"
        CULTURE = "culture", "Cultura"
        SCIENCE = "science", "Ciência e tecnologia"
        LAW = "law", "Constituição e direitos"

    title = models.CharField("nome", max_length=200)
    slug = models.SlugField(unique=True)
    category = models.CharField(max_length=20, choices=Category.choices)
    origin_author = models.CharField("autor ou origem", max_length=180, blank=True)
    context = models.TextField("contextualização", blank=True)
    explanation = models.TextField("explicação", blank=True)
    central_concept = models.CharField("conceito central", max_length=220, blank=True)
    applications = models.TextField("possíveis aplicações", blank=True)
    use_example = models.TextField("exemplo de uso", blank=True)
    sources = models.ManyToManyField(Source, blank=True, related_name="repertoires")
    is_published = models.BooleanField("publicado", default=False)

    class Meta:
        ordering = ["category", "title"]
        verbose_name = "repertório"
        verbose_name_plural = "repertórios"

    def __str__(self):
        return self.title


class Exercise(models.Model):
    class Competency(models.TextChoices):
        C1 = "C1", "Competência 1 · escrita formal"
        C2 = "C2", "Competência 2 · tema e repertório"
        C3 = "C3", "Competência 3 · projeto de texto"
        C4 = "C4", "Competência 4 · coesão"
        C5 = "C5", "Competência 5 · intervenção"

    title = models.CharField("título", max_length=180)
    slug = models.SlugField(unique=True)
    prompt = models.TextField("enunciado")
    explanation = models.TextField("explicação geral", blank=True)
    competency = models.CharField("competência do Enem", max_length=2, choices=Competency.choices, blank=True)
    lesson = models.ForeignKey(Lesson, null=True, blank=True, on_delete=models.SET_NULL, related_name="exercises")
    is_published = models.BooleanField("publicado", default=False)

    class Meta:
        ordering = ["title"]
        verbose_name = "exercício"
        verbose_name_plural = "exercícios"

    def __str__(self):
        return self.title


class ExerciseChoice(models.Model):
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name="choices")
    text = models.CharField("alternativa", max_length=500)
    feedback = models.TextField("feedback desta alternativa", blank=True)
    is_correct = models.BooleanField("resposta adequada", default=False)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "alternativa"
        verbose_name_plural = "alternativas"

    def __str__(self):
        return self.text[:80]


class ExerciseAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="exercise_attempts")
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name="attempts")
    choice = models.ForeignKey(ExerciseChoice, on_delete=models.PROTECT, related_name="attempts")
    is_correct = models.BooleanField()
    attempted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-attempted_at"]
        verbose_name = "tentativa de exercício"
        verbose_name_plural = "tentativas de exercícios"

    def __str__(self):
        return f"{self.user}: {self.exercise}"


class WeeklyGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="weekly_goals")
    week_start = models.DateField()
    target_lessons = models.PositiveSmallIntegerField(default=3)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "week_start"], name="unique_user_weekly_goal")]
        verbose_name = "meta semanal"
        verbose_name_plural = "metas semanais"


class StudyStats(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="study_stats")
    points = models.PositiveIntegerField(default=0)
    current_streak = models.PositiveSmallIntegerField(default=0)
    longest_streak = models.PositiveSmallIntegerField(default=0)
    last_study_date = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = "estatística de estudo"
        verbose_name_plural = "estatísticas de estudo"


class LessonReward(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="lesson_rewards")
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="student_rewards")
    points = models.PositiveSmallIntegerField(default=10)
    awarded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "lesson"], name="unique_user_lesson_reward")]
        verbose_name = "recompensa de aula"
        verbose_name_plural = "recompensas de aulas"


class ActivityEvent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="activity_events")
    event_type = models.CharField(max_length=50)
    label = models.CharField(max_length=180)
    lesson = models.ForeignKey(Lesson, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "atividade do estudante"
        verbose_name_plural = "atividades do estudante"


class Achievement(models.Model):
    title = models.CharField("título", max_length=120, unique=True)
    description = models.CharField("descrição", max_length=240)
    required_lessons = models.PositiveSmallIntegerField(default=1)

    class Meta:
        ordering = ["required_lessons"]
        verbose_name = "conquista"
        verbose_name_plural = "conquistas"


class UserAchievement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="achievements")
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE, related_name="students")
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "achievement"], name="unique_user_achievement")]
        verbose_name = "conquista do estudante"
        verbose_name_plural = "conquistas dos estudantes"


class EssayExample(models.Model):
    title = models.CharField("título", max_length=200)
    slug = models.SlugField(max_length=60, unique=True)
    edition_year = models.PositiveSmallIntegerField("edição do Enem", null=True, blank=True)
    text_source_page = models.PositiveSmallIntegerField("página da fonte integral", null=True, blank=True)
    theme = models.ForeignKey(Theme, null=True, blank=True, on_delete=models.SET_NULL, related_name="essay_examples")
    source = models.ForeignKey(Source, on_delete=models.PROTECT, related_name="essay_examples")
    text_source = models.ForeignKey(Source, null=True, blank=True, on_delete=models.PROTECT, related_name="transcribed_essays")
    attribution = models.CharField("autoria/atribuição", max_length=220, blank=True)
    permission_note = models.CharField(
        "atribuição e observação de uso",
        max_length=220,
        blank=True,
        help_text="Registre a fonte, a atribuição e os limites de reprodução; não declare uma autorização que não foi verificada.",
    )
    full_text = models.TextField("texto integral", blank=True)
    analysis = models.TextField("análise didática", blank=True)
    is_published = models.BooleanField("publicado", default=False)

    class Meta:
        verbose_name = "redação exemplar"
        verbose_name_plural = "redações exemplares"

    def __str__(self):
        return self.title


class AdminAuditEvent(models.Model):
    actor = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="admin_audit_events")
    action = models.CharField(max_length=80)
    object_type = models.CharField(max_length=120)
    object_id = models.CharField(max_length=80, blank=True)
    changes = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "evento de auditoria administrativa"
        verbose_name_plural = "eventos de auditoria administrativa"
