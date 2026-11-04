from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.urls import path

from .forms import EmailAuthenticationForm, NormalizedPasswordResetForm
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("cadastro/", views.register, name="register"),
    path("login/", auth_views.LoginView.as_view(template_name="academy/login.html", authentication_form=EmailAuthenticationForm), name="login"),
    path("sair/", auth_views.LogoutView.as_view(), name="logout"),
    path("app/", views.dashboard, name="dashboard"),
    path("notas/", views.notes_home, name="notes_home"),
    path("notas/nova/", views.note_new, name="note_new"),
    path("notas/<int:note_id>/", views.note_edit, name="note_edit"),
    path("notas/<int:note_id>/excluir/", views.note_delete, name="note_delete"),
    path("app/meta-semanal/", views.update_weekly_goal, name="update_weekly_goal"),
    path("app/perfil/", views.profile, name="profile"),
    path("app/perfil/foto/", views.profile_photo, name="profile_photo"),
    path("app/excluir-conta/", views.delete_account, name="delete_account"),
    path("app/senha/", login_required(auth_views.PasswordChangeView.as_view(template_name="academy/password_change.html", success_url="/app/senha/atualizada/")), name="password_change"),
    path("app/senha/atualizada/", auth_views.PasswordChangeDoneView.as_view(template_name="academy/password_change_done.html"), name="password_change_done"),
    path("trilhas/", views.path_list, name="paths"),
    path("trilhas/<slug:path_slug>/", views.path_detail, name="path_detail"),
    path("trilhas/<slug:path_slug>/aulas/<slug:lesson_slug>/", views.lesson_detail, name="lesson"),
    path("temas/", views.theme_list, name="themes"),
    path("repertorios/", views.repertoire_list, name="repertoires"),
    path("repertorios/<slug:repertoire_slug>/", views.repertoire_detail, name="repertoire_detail"),
    path("materiais-oficiais/", views.official_materials, name="official_materials"),
    path("privacidade/", views.privacy_policy, name="privacy"),
    path("redacoes-exemplares/", views.essay_examples, name="essay_examples"),
    path("redacoes-exemplares/<slug:essay_slug>/", views.essay_example_detail, name="essay_example_detail"),
    path("oficina/", views.writing_workshop, name="writing_workshop"),
    path("exercicios/<slug:exercise_slug>/", views.exercise_detail, name="exercise"),
    path("recuperar-senha/", auth_views.PasswordResetView.as_view(template_name="academy/password_reset.html", email_template_name="academy/password_reset_email.html", subject_template_name="academy/password_reset_subject.txt", form_class=NormalizedPasswordResetForm, success_url="/recuperar-senha/enviado/"), name="password_reset"),
    path("recuperar-senha/enviado/", auth_views.PasswordResetDoneView.as_view(template_name="academy/password_reset_done.html"), name="password_reset_done"),
    path("recuperar-senha/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(template_name="academy/password_reset_confirm.html", success_url="/recuperar-senha/concluido/"), name="password_reset_confirm"),
    path("recuperar-senha/concluido/", auth_views.PasswordResetCompleteView.as_view(template_name="academy/password_reset_complete.html"), name="password_reset_complete"),
]
