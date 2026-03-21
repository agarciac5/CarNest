from django.shortcuts import render, redirect
from .forms import RegistroForm
from django.contrib import messages
from django.contrib.auth import authenticate, login

def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario registrado correctamente")
            return redirect('login')
        else:
            messages.error(request, "Error en el formulario")
    else:
        form = RegistroForm()

    return render(request, 'usuarios/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Inicio de sesión exitoso")
            return redirect('/')
        else:
            messages.error(request, "Usuario o contraseña incorrectos")

    return render(request, 'usuarios/login.html')