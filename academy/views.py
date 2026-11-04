from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import FileResponse, Http404, JsonResponse
from django.db import IntegrityError, transaction
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from datetime import timedelta

from .forms import NoteForm, ProfileForm, RegistrationForm, sanitize_note_html
from .models import Achievement, ActivityEvent, EssayExample, Exercise, ExerciseAttempt, ExerciseChoice, LearningPath, Lesson, LessonProgress, LessonReward, Note, RepertoireEntry, Source, StudyStats, Theme, User, UserAchievement, WeeklyGoal


def home(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    paths = LearningPath.objects.filter(is_published=True).annotate(lesson_count=Count("modules__lessons", filter=Q(modules__lessons__is_published=True))).order_by("order")[:3]
    return render(request, "academy/home.html", {"paths": paths})


def register(request):
    if not settings.REDAWAY_REGISTRATION_ENABLED:
        raise Http404
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = RegistrationForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        try:
            with transaction.atomic():
                user = form.save()
                student_group, _ = Group.objects.get_or_create(name="Estudante")
                user.groups.add(student_group)
        except IntegrityError:
            if User.objects.filter(email__iexact=form.cleaned_data["email"]).exists():
                form.add_error("email", "Este e-mail já está cadastrado. Entre na sua conta ou use outro e-mail.")
            else:
                raise
        else:
            login(request, user)
            messages.success(request, "Sua conta está pronta. Vamos começar sua jornada.")
            return redirect("dashboard")
    return render(request, "academy/register.html", {"form": form})


@login_required
def dashboard(request):
    paths = LearningPath.objects.filter(is_published=True).annotate(lesson_count=Count("modules__lessons", filter=Q(modules__lessons__is_published=True)))
    progress = LessonProgress.objects.filter(user=request.user, completed_at__isnull=False)
    completed_ids = set(progress.values_list("lesson_id", flat=True))
    total_lessons = Lesson.objects.filter(module__path__is_published=True, is_published=True).count()
    completed_count = len(completed_ids)
    today = timezone.localdate()
    week_start = today - timedelta(days=today.weekday())
    goal, _ = WeeklyGoal.objects.get_or_create(user=request.user, week_start=week_start)
    weekly_completed = LessonProgress.objects.filter(user=request.user, completed_at__date__gte=week_start).count()
    study_stats, _ = StudyStats.objects.get_or_create(user=request.user)
    visible_streak = study_stats.current_streak if study_stats.last_study_date and study_stats.last_study_date >= today - timedelta(days=1) else 0
    last_progress = LessonProgress.objects.filter(user=request.user).select_related("lesson", "lesson__module", "lesson__module__path").order_by("-started_at").first()
    next_lesson = None
    if last_progress and not last_progress.is_complete:
        next_lesson = last_progress.lesson
    if next_lesson is None:
        next_lesson = Lesson.objects.filter(is_published=True, module__path__is_published=True).exclude(id__in=completed_ids).select_related("module", "module__path").first()
    competency_progress = []
    recommended_competency_lesson = None
    recommendation_candidates = []
    competency_attempts = ExerciseAttempt.objects.filter(user=request.user, exercise__competency__gt="").select_related("exercise", "choice").order_by("-attempted_at")
    for code, label in Exercise.Competency.choices:
        attempts = list(competency_attempts.filter(exercise__competency=code)[:20])
        latest_per_exercise = {}
        for item in attempts:
            latest_per_exercise.setdefault(item.exercise_id, item)
        recent = list(latest_per_exercise.values())
        accuracy = round(sum(a.is_correct for a in recent) / len(recent) * 100) if len(recent) >= 2 else None
        competency_progress.append({"code": code, "label": label, "attempts": len(attempts), "sample_size": len(recent), "accuracy": accuracy})
        lessons = Lesson.objects.filter(module__path__slug="as-cinco-competencias", is_published=True, module__lessons__is_published=True)
        target_lesson = lessons.filter(slug={"C1":"escrita-formal-e-clareza-sintatica", "C2":"tema-genero-e-repertorio", "C3":"projeto-de-texto-e-argumentos", "C4":"coesao-e-encadeamento", "C5":"proposta-de-intervencao"}[code]).select_related("module", "module__path").first()
        if target_lesson and not LessonProgress.objects.filter(user=request.user, lesson=target_lesson, completed_at__isnull=False).exists():
            recommendation_candidates.append((0 if accuracy is not None else 1, accuracy if accuracy is not None else 101, target_lesson))
    if recommendation_candidates:
        recommended_competency_lesson = sorted(recommendation_candidates, key=lambda item: (item[0], item[1]))[0][2]
    return render(request, "academy/dashboard.html", {
        "paths": paths,
        "completed_count": completed_count,
        "total_lessons": total_lessons,
        "completion_percent": round(completed_count / total_lessons * 100) if total_lessons else 0,
        "next_lesson": next_lesson,
        "recent_progress": LessonProgress.objects.filter(user=request.user, completed_at__isnull=False).select_related("lesson", "lesson__module__path").order_by("-completed_at")[:4],
        "goal": goal,
        "goal_options": range(1, 15),
        "weekly_completed": weekly_completed,
        "earned_achievements": UserAchievement.objects.filter(user=request.user).select_related("achievement").order_by("-earned_at")[:3],
        "study_stats": study_stats,
        "visible_streak": visible_streak,
        "competency_progress": competency_progress,
        "recommended_competency_lesson": recommended_competency_lesson,
    })


@login_required
def update_weekly_goal(request):
    if request.method == "POST":
        today = timezone.localdate()
        week_start = today - timedelta(days=today.weekday())
        raw_target = request.POST.get("target_lessons", "")
        try:
            target = int(raw_target)
        except (TypeError, ValueError):
            target = 0
        if 1 <= target <= 14:
            WeeklyGoal.objects.update_or_create(user=request.user, week_start=week_start, defaults={"target_lessons": target})
            messages.success(request, "Sua meta semanal foi atualizada.")
        else:
            messages.error(request, "Escolha uma meta entre 1 e 14 aulas por semana.")
    return redirect("dashboard")


@login_required
def path_list(request):
    paths = LearningPath.objects.filter(is_published=True).annotate(lesson_count=Count("modules__lessons", filter=Q(modules__lessons__is_published=True)))
    return render(request, "academy/paths.html", {"paths": paths})


@login_required
def path_detail(request, path_slug):
    path = get_object_or_404(LearningPath.objects.filter(is_published=True).annotate(lesson_count=Count("modules__lessons", filter=Q(modules__lessons__is_published=True))), slug=path_slug)
    modules = path.modules.filter(lessons__is_published=True).distinct().prefetch_related("lessons").all()
    completed_ids = set()
    if request.user.is_authenticated:
        completed_ids = set(LessonProgress.objects.filter(user=request.user, completed_at__isnull=False, lesson__module__path=path).values_list("lesson_id", flat=True))
    return render(request, "academy/path_detail.html", {"path": path, "modules": modules, "completed_ids": completed_ids})


@login_required
def profile(request):
    form = ProfileForm(request.POST or None, request.FILES or None, instance=request.user)
    if request.method == "POST" and form.is_valid():
        try:
            form.save()
        except IntegrityError:
            if User.objects.filter(email__iexact=form.cleaned_data["email"]).exclude(pk=request.user.pk).exists():
                form.add_error("email", "Este e-mail já está cadastrado. Entre na sua conta ou use outro e-mail.")
            else:
                raise
        else:
            messages.success(request, "Seu perfil foi atualizado.")
            return redirect("profile")
    return render(request, "academy/profile.html", {"form": form})


@login_required
def delete_account(request):
    if request.method == "POST":
        confirmation = request.POST.get("confirmation", "")
        password = request.POST.get("password", "")
        if confirmation == "EXCLUIR" and request.user.check_password(password):
            from django.contrib.auth import logout
            user = request.user
            logout(request)
            user.delete()
            messages.success(request, "Sua conta e os registros de aprendizagem associados foram excluídos.")
            return redirect("home")
        messages.error(request, "Confirme digitando EXCLUIR e informe sua senha atual.")
    return render(request, "academy/delete_account.html")


def privacy_policy(request):
    return render(request, "academy/privacy.html")


@login_required
def profile_photo(request):
    if not request.user.photo:
        raise Http404
    try:
        from PIL import Image
        with request.user.photo.open("rb") as photo_file:
            image_format = Image.open(photo_file).format
        content_type = {"JPEG": "image/jpeg", "PNG": "image/png", "WEBP": "image/webp"}.get(image_format)
        if content_type is None:
            raise Http404
        response = FileResponse(request.user.photo.open("rb"), content_type=content_type)
    except (FileNotFoundError, OSError, ValueError):
        raise Http404
    response["Cache-Control"] = "private, no-store"
    response["X-Content-Type-Options"] = "nosniff"
    return response


@login_required
def lesson_detail(request, path_slug, lesson_slug):
    lesson = get_object_or_404(Lesson.objects.select_related("module", "module__path"), slug=lesson_slug, module__path__slug=path_slug, module__path__is_published=True, is_published=True)
    progress, _ = LessonProgress.objects.get_or_create(user=request.user, lesson=lesson)
    if request.method == "POST":
        with transaction.atomic():
            progress = LessonProgress.objects.select_for_update().get(pk=progress.pk, user=request.user)
            if not progress.is_complete:
                today = timezone.localdate()
                progress.completed_at = timezone.now()
                progress.save(update_fields=["completed_at"])
                reward, created = LessonReward.objects.get_or_create(user=request.user, lesson=lesson, defaults={"points": 10})
                if created:
                    stats, _ = StudyStats.objects.get_or_create(user=request.user)
                    yesterday = today - timedelta(days=1)
                    if stats.last_study_date == today:
                        pass
                    elif stats.last_study_date == yesterday:
                        stats.current_streak += 1
                    else:
                        stats.current_streak = 1
                    stats.longest_streak = max(stats.longest_streak, stats.current_streak)
                    stats.last_study_date = today
                    stats.points += reward.points
                    stats.save(update_fields=["current_streak", "longest_streak", "last_study_date", "points"])
                    ActivityEvent.objects.create(user=request.user, event_type="lesson_completed", label=f"Concluiu: {lesson.title}", lesson=lesson)
                    completed_count = LessonProgress.objects.filter(user=request.user, completed_at__isnull=False).count()
                    for badge in Achievement.objects.filter(required_lessons__lte=completed_count):
                        UserAchievement.objects.get_or_create(user=request.user, achievement=badge)
        messages.success(request, "Aula concluída. Seu progresso foi salvo.")
        return redirect("lesson", path_slug=path_slug, lesson_slug=lesson_slug)
    following = Lesson.objects.filter(module=lesson.module, is_published=True, order__gt=lesson.order).first()
    if following is None:
        following = Lesson.objects.filter(module__path=lesson.module.path, is_published=True, module__order__gt=lesson.module.order).order_by("module__order", "order").first()
    exercise = lesson.exercises.filter(is_published=True).first()
    return render(request, "academy/lesson.html", {"lesson": lesson, "progress": progress, "following": following, "exercise": exercise})


@login_required
def theme_list(request):
    themes = Theme.objects.filter(is_published=True)
    query = request.GET.get("q", "").strip()
    if query:
        themes = themes.filter(Q(title__icontains=query) | Q(context__icontains=query) | Q(category__icontains=query))
    categories = Theme.objects.filter(is_published=True).order_by("category").values_list("category", flat=True).distinct()
    years = Theme.objects.filter(is_published=True, year__isnull=False).order_by("-year").values_list("year", flat=True).distinct()
    category = request.GET.get("category", "").strip()
    if category in categories:
        themes = themes.filter(category=category)
    difficulty = request.GET.get("difficulty", "").strip()
    if difficulty in Theme.Difficulty.values:
        themes = themes.filter(difficulty=difficulty)
    origin = request.GET.get("origin", "").strip()
    if origin in Theme.Origin.values:
        themes = themes.filter(origin=origin)
    year = request.GET.get("year", "").strip()
    if year.isdecimal() and len(year) == 4:
        themes = themes.filter(year=int(year))
    return render(request, "academy/theme_list.html", {"themes": themes.prefetch_related("sources", "repertoires"), "query": query, "categories": categories, "years": years, "difficulties": Theme.Difficulty.choices, "origins": Theme.Origin.choices})


@login_required
def repertoire_list(request):
    entries = RepertoireEntry.objects.filter(is_published=True)
    query = request.GET.get("q", "").strip()
    if query:
        entries = entries.filter(
            Q(title__icontains=query) | Q(origin_author__icontains=query)
            | Q(central_concept__icontains=query) | Q(explanation__icontains=query)
            | Q(context__icontains=query) | Q(applications__icontains=query)
            | Q(use_example__icontains=query)
        )
    category = request.GET.get("category", "").strip()
    valid_categories = {value for value, _label in RepertoireEntry.Category.choices}
    if category in valid_categories:
        entries = entries.filter(category=category)
    return render(request, "academy/repertoire_list.html", {
        "entries": entries.prefetch_related("sources"), "query": query,
        "categories": RepertoireEntry.Category.choices, "selected_category": category,
        "result_count": entries.count(),
    })


@login_required
def repertoire_detail(request, repertoire_slug):
    entry = get_object_or_404(
        RepertoireEntry.objects.filter(is_published=True).prefetch_related("sources", "themes"),
        slug=repertoire_slug,
    )
    related_themes = [theme for theme in entry.themes.all() if theme.is_published]
    return render(request, "academy/repertoire_detail.html", {"entry": entry, "related_themes": related_themes})


def _notes_workspace(request, form=None, active_note=None, is_new=False, editor_body=None):
    notes = Note.objects.filter(user=request.user)
    query = request.GET.get("q", "").strip()
    if query:
        notes = notes.filter(Q(title__icontains=query) | Q(topic__icontains=query) | Q(body__icontains=query))
    return render(request, "academy/notes_workspace.html", {
        "notes": notes, "query": query, "form": form, "active_note": active_note,
        "is_new": is_new, "editor_body": editor_body,
    })


@login_required
def notes_home(request):
    return _notes_workspace(request)


@login_required
def note_new(request):
    form = NoteForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        note = form.save(commit=False)
        note.user = request.user
        note.save()
        messages.success(request, "Nota criada.")
        return redirect("note_edit", note_id=note.pk)
    editor_body = sanitize_note_html(request.POST.get("body", "")) if request.method == "POST" else ""
    return _notes_workspace(request, form=form, is_new=True, editor_body=editor_body)


@login_required
def note_edit(request, note_id):
    note = get_object_or_404(Note, pk=note_id, user=request.user)
    form = NoteForm(request.POST or None, instance=note)
    if request.method == "POST" and form.is_valid():
        updated_note = form.save(commit=False)
        updated_note.user = request.user
        updated_note.save()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"ok": True, "saved_at": updated_note.updated_at.strftime("%H:%M")})
        messages.success(request, "Nota salva.")
        return redirect("note_edit", note_id=note.pk)
    if request.method == "POST" and request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"ok": False, "errors": form.errors.get_json_data()}, status=400)
    editor_body = sanitize_note_html(request.POST.get("body", "")) if request.method == "POST" else note.body
    return _notes_workspace(request, form=form, active_note=note, editor_body=editor_body)


@login_required
@require_POST
def note_delete(request, note_id):
    note = get_object_or_404(Note, pk=note_id, user=request.user)
    note.delete()
    messages.success(request, "Nota excluída.")
    return redirect("notes_home")


@login_required
def official_materials(request):
    return render(request, "academy/official_materials.html", {"sources": Source.objects.filter(is_official=True)})


@login_required
def essay_examples(request):
    examples = EssayExample.objects.filter(is_published=True).select_related("source", "theme").order_by("-edition_year", "title")
    cartilha = Source.objects.filter(title="A Redação do Enem 2026 — Cartilha do Participante").first()
    return render(request, "academy/essay_examples.html", {"examples": examples, "cartilha": cartilha})


@login_required
def essay_example_detail(request, essay_slug):
    example = get_object_or_404(
        EssayExample.objects.filter(is_published=True).select_related("source", "text_source", "theme"),
        slug=essay_slug,
    )
    cartilha = Source.objects.filter(title="A Redação do Enem 2026 — Cartilha do Participante").first()
    return render(request, "academy/essay_example_detail.html", {"example": example, "cartilha": cartilha})


@login_required
def writing_workshop(request):
    return render(request, "academy/writing_workshop.html")


@login_required
def exercise_detail(request, exercise_slug):
    exercise = get_object_or_404(Exercise.objects.prefetch_related("choices"), slug=exercise_slug, is_published=True)
    attempt = None
    selected = None
    if request.method == "POST":
        choice = get_object_or_404(ExerciseChoice, pk=request.POST.get("choice"), exercise=exercise)
        attempt = ExerciseAttempt.objects.create(user=request.user, exercise=exercise, choice=choice, is_correct=choice.is_correct)
        return redirect(f"/exercicios/{exercise.slug}/?tentativa={attempt.pk}")
    attempt_id = request.GET.get("tentativa")
    if attempt_id:
        attempt = ExerciseAttempt.objects.filter(pk=attempt_id, user=request.user, exercise=exercise).select_related("choice").first()
        if attempt:
            selected = attempt.choice
    return render(request, "academy/exercise.html", {"exercise": exercise, "attempt": attempt, "selected": selected})
