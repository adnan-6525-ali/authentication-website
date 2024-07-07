from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from .models import OTP
import random
from django.contrib import messages

@login_required(login_url='/login/')
def Home(request):
    full_name = request.user.first_name + " " + request.user.last_name
    return render(request, "home.html", {"fullname": full_name})

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_via_email(email, otp):
    subject = 'OTP Code to Verify your Email Address'
    message = f'''Dear Sir/Mam,

Welcome to platform! Thank you for registering with us. We’re excited to have you on board.

To complete your registration, please use the following verification OTP code:

Your OTP code is: {otp}

If you have any questions or need assistance, feel free to reach out to our support team.'''
    email_from = 'moadnan6525@gmail.com'  # Update with your email
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)

def Login(request):
    if request.method == "POST":
        uname = request.POST.get("username")
        passw = request.POST.get("password")
        user = authenticate(request, username=uname, password=passw)
        
        if user is not None:
            if user.userprofile.email_verified:
                login(request, user)
                messages.success(request, "Login Succesfully.")
                return redirect("home")
            else:
                messages.error(request, "Please verify your email to log in.")
                return redirect("login")
        else:
            messages.error(request, "Username or password incorrect!")
            return redirect("login")
    
    return render(request, "login.html")

def Signup(request):
    if request.method == "POST":
        fname = request.POST.get("first_name")
        lname = request.POST.get("last_name")
        uname = request.POST.get("username")
        email = request.POST.get("email")
        pass1 = request.POST.get("password1")
        pass2 = request.POST.get("password2")
        contains_char_and_digit = lambda s: any(c.isalpha() for c in s) and any(c.isdigit() for c in s)

        if pass1 == pass2:
            if User.objects.filter(username=uname).exists():
                msg = "Username already exists!"
                messages.error(request, msg)
                return redirect("signup")
            elif User.objects.filter(email=email).exists():
                msg = "Email already Registered!"
                messages.error(request, msg)
                return redirect("signup")
            elif not contains_char_and_digit(uname):
                msg = "Username should contain both characters and digits."
                messages.error(request, msg)
                return redirect("signup")
            elif not contains_char_and_digit(pass1):
                msg = "Password should contain both characters and digits."
                messages.error(request, msg)
                return redirect("signup")
            else:
                myUser = User.objects.create_user(username=uname, email=email, password=pass1, first_name=fname, last_name=lname)
                myUser.is_active = False  # Deactivate account until email is verified
                myUser.save()
                
                otp = generate_otp()
                OTP.objects.create(user=myUser, otp=otp)
                send_otp_via_email(email, otp)
                request.session['user_id'] = myUser.id
                msg = "Registered Succesfully! Please verify Your Email Address"
                messages.success(request, msg)
                return redirect("verify_otp")
        else:
            msg = "Passwords do not match!"
            messages.error(request, msg)
            return redirect("signup")
    
    return render(request, "signup.html")

def VerifyOTP(request):
    user_id = request.session.get('user_id')
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return HttpResponse("User does not exist")

    if request.method == "POST":
        if 'otp' in request.POST:
            otp = (
                request.POST.get("otp1") +
                request.POST.get("otp2") +
                request.POST.get("otp3") +
                request.POST.get("otp4") +
                request.POST.get("otp5") +
                request.POST.get("otp6")
            )
            if OTP.objects.filter(user=user, otp=otp).exists():
                otp_instance = OTP.objects.get(user=user, otp=otp)
                if otp_instance.is_valid():
                    user.userprofile.email_verified = True
                    user.userprofile.save()
                    user.is_active = True  # Activate user account after successful OTP verification
                    user.save()
                    login(request, user)
                    msg = "Verified Successfully! Your are Logged in..."
                    messages.success(request, msg)
                    return redirect("home")
                else:
                    msg = "OTP has expired!"
                    messages.error(request, msg)
                    return redirect("verify_otp")
            else:
                msg = "Invalid OTP!"
                messages.error(request, msg)
                return redirect("verify_otp")
        elif 'edit_email' in request.POST:
            new_email = request.POST.get("new_email")
            user.email = new_email
            user.save()
            otp = generate_otp()
            OTP.objects.create(user=user, otp=otp)
            send_otp_via_email(new_email, otp)
            msg = "EMail Updated Successfully! New OTP is sent on your New EMail"
            messages.success(request, msg)
            return redirect("verify_otp")
    return render(request, "verify_otp.html", {"email": user.email})

def Logout(request):
    logout(request)
    return redirect("login")
