from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    error = None

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        if not username or not password:
            error = "Please enter both username and password."
        else:
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
              
                next_url = request.GET.get('next', 'dashboard')
                return redirect(next_url)
            else:
                error = "Invalid username or password. Please try again."

    return render(request, 'login/login.html', {'error': error})


def register_view(request):

    if request.user.is_authenticated:
        return redirect('dashboard')

    errors = {}

    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():

            user = form.save()


            login(request, user)

            return redirect('dashboard')
        else:

            for field, field_errors in form.errors.items():
                if field == 'username':
                    errors['username'] = field_errors[0]
                elif field == 'email':
                    errors['email'] = field_errors[0]
                elif field == 'password1':
                    errors['password1'] = field_errors[0]
                elif field == 'password2':
                    errors['password2'] = field_errors[0]
                elif field == '__all__':
                    errors['general'] = field_errors[0]

    else:
        form = RegisterForm()

    return render(request, 'login/register.html', {
        'form':   form,
        'errors': errors,
    })

def logout_view(request):
    logout(request)
    return redirect('login')