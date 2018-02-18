from django.conf.urls import url
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from extuser import forms, views


urlpatterns = [
    url(r'^$', views.main, name="main"),
    url(r'^login/$', auth_views.LoginView.as_view(
        template_name='extuser/login.html',
        authentication_form=forms.AuthenticationForm
        ),
        name="login"),
    url(r'^password_reset/$', auth_views.PasswordResetView.as_view(
        template_name='extuser/password_reset.html',
        email_template_name='extuser/password_reset_email.html',
        success_url=reverse_lazy('extuser:password_reset_done')
        ),
        name='password_reset'),
    url(r'^password_reset/done/$', auth_views.PasswordResetDoneView.as_view(
        template_name='extuser/password_reset_done.html',
        ),
        name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='extuser/password_reset_confirm.html',
            success_url=reverse_lazy('extuser:password_reset_complete')
            ),
        name='password_reset_confirm'),
    url(r'^reset/done/$', auth_views.PasswordResetCompleteView.as_view(
        template_name='extuser/password_reset_complete.html',
        ),
        name='password_reset_complete'),
    url(r'^registration/$', views.registration, name="registration"),
    url(r'^confirmation/(?P<key>([-\w]+))/$', views.confirmation_email, name="confirmation"),
    url(r'^confirmation_resend/$', views.resend_confirmation_email, name="confirmation_resend"),
    url(r'^logout/$', auth_views.LogoutView.as_view(
        next_page='extuser:main',
        ),
        name='logout'),
]
