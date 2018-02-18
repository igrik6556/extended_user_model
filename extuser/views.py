from django.shortcuts import redirect, render
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from extuser.models import User, EmailConfirmation
from extuser.forms import UserCreationForm, ResendConfirmationForm

from django.utils.translation import ugettext as _

def main(request):
    users = User.objects.all()
    return render(request,
                  'extuser/main.html',
                  {
                      'users': users,
                  })


def registration(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            c = form.save(commit=False)
            c.save()
            return redirect('extuser:main')
    else:
        form = UserCreationForm()
    return render(request,
                  'extuser/registration.html',
                  {
                      'form': form,
                  })


def confirmation_email(request, key):
    user = EmailConfirmation.objects.confirmation(key.lower())
    if user:
        if user.is_confirm:
            messages.add_message(request, messages.SUCCESS, _("Activation was successful."))
        else:
            messages.add_message(request, messages.SUCCESS, _("The activation period has expired"))
        return redirect('extuser:main')
    messages.add_message(request, messages.ERROR, _("The activation period has expired."))
    return redirect('extuser:main')


def resend_confirmation_email(request):
    if request.method == "POST":
        try:
            user = User.objects.get(email=request.POST['email'])
        except ObjectDoesNotExist:
            messages.add_message(request, messages.ERROR, _("The user does not exist."))
            return redirect("extuser:main")
        if user.is_confirm:
            messages.add_message(request, messages.SUCCESS, _("User is already confirmed"))
        else:
            user.emailconfirmation.delete()
            user.save()
            messages.add_message(request, messages.SUCCESS, _("The confirmation email has send"))
        return redirect("extuser:main")
    else:
        form = ResendConfirmationForm()
    return render(request,
                  'extuser/confirmation_resend.html',
                  {
                      'form': form,
                  })
