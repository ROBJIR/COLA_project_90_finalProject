import logging

from django import forms
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group, User
from django.db import transaction
from django.shortcuts import redirect
from django.views import View

from syslog.views.logging import SysLogging

from .web import WebRenderMixin

logger = logging.getLogger("cassiopeia.auth")

# Displays the current user profile.
# Zobrazuje profil aktuálního uživatele.
class UserProfile(WebRenderMixin, View):
    # Initializes the profile context.
    # Inicializuje kontext profilu.
    def __init__(self):
        self.web_data = {}
    # Renders the profile or redirects an anonymous request.
    # Vykresluje profil nebo přesměrovává nepřihlášeného uživatele.
    def get(self, request):
        if request.user.is_authenticated:
            return self.page_render(request, 'userprofile', self.web_data)
        else:
            return redirect("login")

# Validates the optional profile details in the second registration step.
# Ověřuje nepovinné údaje profilu ve druhém kroku registrace.
class RegistrationDetailsForm(forms.Form):
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    email = forms.EmailField(max_length=254, required=False)


# Handles the two-step account registration flow.
# Obsluhuje dvoukrokovou registraci účtu.
class UserRegistration(WebRenderMixin, View):
    # Initializes the registration context.
    # Inicializuje kontext registrace.
    def __init__(self):
        self.web_data = {}
    # Renders the first registration step or the current profile.
    # Vykresluje první krok registrace nebo aktuální profil.
    def get(self, request):
        if request.user.is_authenticated:
            return self.page_render(request, 'userprofile', self.web_data)
        else:
            self.web_data = {'registration_step':'(step 1/2)'}
            return self.page_render(request, 'userregistration', self.web_data)

    # Validates credentials or saves account details for the submitted step.
    # Podle odeslaného kroku ověřuje přihlašovací údaje nebo ukládá údaje účtu.
    def post(self, request):
        if request.user.is_authenticated:
            return self.page_render(request, 'userprofile', self.web_data)
        else:
            if request.POST.get("registration_step") == '(step 1/2)':
                form = UserCreationForm(data={
                    "username": request.POST.get("username", "").lower(),
                    "password1": request.POST.get("password", ""),
                    "password2": request.POST.get("password-again", ""),
                })
                if form.is_valid():
                    user = form.save()  # Vytvoří uživatele s hashovaným heslem.
                    request.session["registration_user_id"] = user.pk
                    msg = f"User <strong>{user}</strong> was successfully created."
                    SysLogging.log(
                        request,
                        alert_code='success',
                        webmessage_show='auth',
                        module_code='UserRegistration',
                        action_code='registration',
                        step_code=None,
                        status_code='success',
                        parameters_value={},
                        retval_value=user,
                        error_code=None,
                        error_message=None,
                        webmessage_body=msg)
                    self.web_data = {'registration_step': '(step 2/2)'}
                    return self.page_render(request, 'userregistration', self.web_data)

                SysLogging.log(
                    request,
                    alert_code='danger',
                    webmessage_show='auth',
                    module_code='UserRegistration',
                    action_code='registration',
                    step_code=None,
                    status_code='error',
                    parameters_value={},
                    retval_value='',
                    error_code=None,
                    error_message=None,
                    webmessage_body=''.join(error for errors in form.errors.values()
                                                  for error in errors)
                )
                self.web_data = {'registration_step': '(step 1/2)'}
                return self.page_render(request, 'userregistration', self.web_data)


            if request.POST.get("registration_step") == '(step 2/2)':
                user_id = request.session.get("registration_user_id")
                user = User.objects.filter(pk=user_id).first() if user_id is not None else None
                if user is None:
                    request.session.pop("registration_user_id", None)
                    self.web_data = {
                        "registration_step": "(step 1/2)",
                        "registration_error": "Your registration session has expired. Start again.",
                    }
                    return self.page_render(request, "userregistration", self.web_data)

                form = RegistrationDetailsForm(request.POST)
                if not form.is_valid():
                    self.web_data = {
                        "registration_step": "(step 2/2)",
                        "registration_error": " ".join(
                            error for errors in form.errors.values() for error in errors
                        ),
                    }
                    return self.page_render(request, "userregistration", self.web_data)

                with transaction.atomic():
                    user.first_name = form.cleaned_data["first_name"]
                    user.last_name = form.cleaned_data["last_name"]
                    user.email = form.cleaned_data["email"]
                    user.save(update_fields=["first_name", "last_name", "email"])
                    public_group = Group.objects.filter(name="public").first()
                    if public_group is not None:
                        user.groups.add(public_group)
                request.session.pop("registration_user_id", None)

                SysLogging.log(
                    request,
                    alert_code='success',
                    webmessage_show='web',
                    module_code='UserRegistration',
                    action_code='saveUserDetail',
                    step_code=None,
                    status_code='success',
                    parameters_value={},
                    retval_value='',
                    error_code=None,
                    error_message=None,
                    webmessage_body='User saved successfully. Now you have to log in!'
                )
                return redirect("login")

        self.web_data = {"registration_step": "(step 1/2)"}
        return self.page_render(request, "userregistration", self.web_data)


# Handles the login form and authentication.
# Obsluhuje přihlašovací formulář a ověřuje totožnost uživatele.
class UserLogin(WebRenderMixin, View):
    # Initializes the login context.
    # Inicializuje kontext přihlášení.
    def __init__(self):
        self.web_data = {}
    # Renders the login form.
    # Vykresluje přihlašovací formulář.
    def get(self, request):
        return self.page_render(request, 'userlogin', self.web_data)
    # Authenticates the submitted credentials and returns the corresponding response.
    # Ověřuje odeslané přihlašovací údaje a vrací odpovídající odpověď.
    def post(self, request):
        username = request.POST.get("username", "").strip().lower()
        form = AuthenticationForm(request, data={"username": username, "password": request.POST.get("password", "")})
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            logger.info("Logged user %r.", user.get_username())

            SysLogging.log(
                request,
                alert_code='info',
                webmessage_show=None,
                module_code='userLogin',
                action_code='login',
                step_code=request.user.username,
                status_code='success',
                parameters_value={"username":request.user.username},
                retval_value=request.user.username,
            )

            return redirect("profile")
        else:
            logger.warning("Failed login attempt for username %r.",request.POST.get("username"),
            )
            SysLogging.log(
                request,
                alert_code='danger',
                webmessage_show='auth',
                module_code='userLogin',
                action_code='login',
                step_code=None,
                status_code='error',
                parameters_value={"username":request.POST.get("username")},
                retval_value=request.POST.get("username"),
                error_code='error-2010',
                error_message='Incorrect username or password!',
            )

            return self.page_render(request, 'userLogin', self.web_data)

# Ends the current authenticated session.
# Ukončuje aktuální přihlášenou relaci.
class UserLogout(LoginRequiredMixin, View):
    # Signs the user out and redirects to the next page.
    # Odhlašuje uživatele a přesměrovává na další stránku.
    def post(self, request):
        username = request.user.get_username()
        logout(request)

        logger.info("Logged out user %r.", username)

        SysLogging.log(
            request,
            alert_code='success',
            webmessage_show='web',
            module_code='userLogout',
            action_code='logout',
            step_code=None,
            status_code='success',
            parameters_value={'username':username},
            retval_value=username,
            error_code=None,
            error_message=None,
            webmessage_body='User has been successfully logged out.',
        )

        return redirect("home")

# Handles password changes for signed-in users.
# Obsluhuje změnu hesla přihlášených uživatelů.
class UserPasswordChange(LoginRequiredMixin, WebRenderMixin, View):
    # Renders the password change form in the profile.
    # Vykresluje formulář pro změnu hesla v profilu.
    def get(self, request):
        self.webdata = {"profile_action": "change_password"}
        return self.page_render(request, 'userprofile', self.webdata)
    # Validates the password change and reports the result.
    # Ověřuje změnu hesla a oznamuje výsledek.
    def post(self, request):
        self.webdata = {"profile_action": "change_password"}
        form = PasswordChangeForm(request.user, data={
            "old_password": request.POST.get("oldpassword", ""),
            "new_password1": request.POST.get("newpassword1", ""),
            "new_password2": request.POST.get("newpassword2", ""),
        })
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            SysLogging.log(
                request, alert_code="success", webmessage_show="auth", module_code="userprofile",
                action_code="change_password", status_code="success",
                parameters_value={"username": user.get_username()},
                webmessage_body="Password has been successfully changed.",
            )
            return redirect("profile")

        self.webdata["password_error"] = " ".join(
            error for errors in form.errors.values() for error in errors
        )
        SysLogging.log(
            request, alert_code="danger", module_code="userprofile",
            action_code="change_password", status_code="error",
            parameters_value={"username": request.user.get_username()},
            error_message="Password change validation failed.",
        )
        return self.page_render(request, "userprofile", self.webdata)
