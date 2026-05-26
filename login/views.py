from django.shortcuts import render, redirect

from django.contrib.auth import (
    authenticate,
    login,
    logout
)

from django.contrib.auth.decorators import login_required

from .forms import RegisterForm


def login_view(request):

    

    error = None

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user:

            login(request, user)

            return redirect('dashboard')

        else:

            error = "Invalid username or password"

    return render(
        request,
        'login/login.html',
        {'error': error}
    )


def register_view(request):



    if request.method == 'POST':

        form = RegisterForm(request.POST)

        if form.is_valid():

            user = form.save()

            login(request, user)

            return redirect('dashboard')

        else:

            return render(
                request,
                'login/register.html',
                {
                    'form': form,
                    'error': 'Invalid details or passwords not matching'
                }
            )

    form = RegisterForm()

    return render(
        request,
        'login/register.html',
        {'form': form}
    )


@login_required
def logout_view(request):

    logout(request)

    return redirect('login')