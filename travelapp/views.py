from django.shortcuts import render,redirect
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from django.core.mail import send_mail
from django.conf import settings
import random
from . models import User
import time
import pycountry
from . form import TourForm
from . models import Destination
from .models import Tour, Destination
from django.shortcuts import get_object_or_404, render, redirect

# Create your views here.

def tour(request):
    return render(request, 'tour.html')

def booking(request):
    return render(request, 'booking.html')

def gallery(request):
    return render(request, 'gallery.html')

def guides(request):
    return render(request, 'guides.html')

def testimonial(request):
    return render(request, 'testimonial.html')

def contact(request):
    return render(request, 'contact.html')

def Page_404(request):
    return render(request, '404.html')

def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request,'about.html')

def services(request):
    return render(request,'services.html')

def packages(request):
    return render(request,'packages.html')

def blog(request):
    return render(request,'blog.html')

def contact(request):
    return render(request,'contact.html')

def booking(request):
    return render(request,'booking.html')

def destination(request):
    return render (request, 'destination.html')

def add_tour(request):
    destinations = Destination.objects.all()
    form = TourForm(request.POST or None, request.FILES or None)
    
    if form.is_valid():
        tour = form.save(commit=False)
        email = request.session.get('email')
        user = User.objects.get(email=email)
        tour.user = user
        tour.save()
        return redirect('view_tour')
    
    return render(request, 'add_tour.html', {
        'form': form,
        'destinations': destinations
    })

def view_tour(request):
    user = User.objects.get(email = request.session['email'])
    tours = Tour.objects.filter(user=user)
    return render(request, 'view_tour.html', {'tours': tours})


def edit_tour(request,pk):
    tour = get_object_or_404(Tour, id=pk)
    if request.method == 'POST':
        form = TourForm(request.POST, request.FILES, instance=tour)
        if form.is_valid():
            form.save()
            return redirect('view_tour')
    else:
        form = TourForm(instance=tour)
    return render(request, 'edit_tour.html', {
        'form': form,
        'tour': tour,
        'destinations': Destination.objects.all()
    })


def delete_tour(request, pk):
    tour = get_object_or_404(Tour, id=pk)
    tour.delete()
    return redirect('view_tour')


def update_tour(request):
    return render(request, 'update_tour.html')


def profile(request):
    user = User.objects.get(email=request.session['email'])
    countries = [country.name for country in pycountry.countries]
    if request.method == "POST":

         if request.POST.get('fname'):
             user.fname = request.POST.get('fname')
         if request.POST.get('lname'):
            user.lname = request.POST.get('lname')
         if request.POST.get('mobile_number'):
            user.mobile_number = request.POST.get('mobile_number')
         if request.POST.get('country'):
            user.country = request.POST.get('country')
         if request.FILES.get('profile_img'):
            user.profile_img = request.FILES['profile_img']

         user.save()
         return redirect('profile')
    else:
        return render(request, "profile.html", {'user': user,'countries': countries})

def register(request):
    countries = [country.name for country in pycountry.countries]
    if request.method == "POST":
        if request.POST['email'] == "" and request.POST['fname']== "" and request.POST['lname']=="" and request.POST['mobile_number']=="":
            msg = "Requeird all Field"
            return render(request,'register.html',{'msg' : msg})
        try:
            user = User.objects.get(email = request.POST['email'])
            msg = "User Already exists"
            return render (request, 'register.html', {'msg':msg})
        except:
            if request.POST['password']==request.POST['cpassword']:
                User.objects.create(
                    fname = request.POST['fname'],
                    lname = request.POST['lname'],
                    email = request.POST['email'],
                    mobile_number = request.POST['mobile_number'],
                    country = request.POST['country'],
                    password = make_password(request.POST['password']),
                    role = request.POST['role'],
                    profile_img = request.FILES['profile_img'],
                )
                
                msg = "Signup Successfully !!"
                return render (request, "login.html",{'msg':msg})
            else:
                msg = "Password and Confirm Password is not match"
                return render (request, "register.html",{'msg':msg})
    else:
         return render(request, 'register.html', {
            'countries': countries  
        })
            

def login(request):
    if request.method == "POST":
        try:
            user = User.objects.get(email = request.POST['email'])
            if check_password(request.POST['password'],user.password):
                request.session['email'] = user.email
                request.session['profile_img'] = user.profile_img.url
                if user.role == "customer":
                    return redirect('index')
                else:
                    request.session['agent']= user.role
                    return redirect('index')
                
            else:
                msg = "Password doesn't match "
                return render(request,'login.html',{'msg':msg})
        except User.DoesNotExist:
            msg = "Email doesn't Exists "
            return render (request,'login.html',{'msg':msg})
    else:
        return render(request, 'login.html')
    

def logout(request):
    request.session.flush()
    return redirect('login')
   


def forget_password(request):
    if request.method == "POST":
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            
            otp = random.randint(100001,999999)

            subject = "OTP for forget password"
            message =f"Hi {user.fname}  {user.lname}  Your OTP  is { str(otp)}"
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [user.email,]
            send_mail(
                subject,
                message,
                email_from,
                recipient_list,
                fail_silently=False
            )
            request.session['useremail'] = user.email
            request.session['otp'] = str(otp)
            request.session['otp_time'] = time.time()
            return redirect('otp')
        except User.DoesNotExist:
            msg = "Email  does not Exists "
            return render (request, 'forget_password.html',{'msg':msg})
    else:
        return render(request,'forget_password.html')

def update_password(request):
    if request.method == 'POST':
        user = User.objects.get(email = request.session['email'])
        try:
            if check_password(request.POST['oldpassword'],user.password) :
                if request.POST['newpassword'] == request.POST['cpassword']:
                    user.password = make_password(request.POST['newpassword'])
                    user.save()
                    return redirect('login')
                else:
                    msg = "Password and Confirm Password doesn't match"
                    return render(request,'update_password.html',{'msg':msg})
            else:
                msg = "Old password is not match"
                return render(request,'update_password.html',{'msg':msg})
        except:
            msg = "Somthing is wrong"
            return render(request,'update_password.html',{'msg':msg})
    else:
        return render(request,'update_password.html')
    

def otp(request):
    if request.method == "POST":
        
          #   user = User.objects.get(email = request.session['newemail'])
            entered_otp = request.POST.get('uotp')
            session_otp = request.session.get('otp')
            otp_time = request.session.get('otp_time')

            if not session_otp or not otp_time:
                msg = "Session expired. Try again."
                return render(request, 'otp.html', {'msg': msg})
            
            if entered_otp == session_otp:
                del request.session['otp']
                del request.session['otp_time']
                return redirect('resetpassword')  # next page
            
            else:
                 msg = "OTP is invalid"
                 return render(request, 'otp.html', {'msg': msg})

    else:
        return render(request, 'otp.html')




def resetpassword(request):
    if request.method == "POST":
        update_email = request.session.get('useremail')

        if not update_email:
            return redirect ('forget_password')
        
        try:
             user = User.objects.get(email = update_email)
             new_password = request.POST.get('newpassword')
             cpassword = request.POST.get('cpassword')

             if new_password == cpassword :
                user.password = make_password(new_password)
                user.save()
                del request.session['useremail']
                return redirect('login')
             else:
                    msg = "Password and Confirm Password doesn't match"
                    return render(request,'resetpassword.html',{'msg':msg})
        except User.DoesNotExist:
            msg = "User not Found"
            return render(request,'forget_password.html')
    else:
        return render(request,'resetpassword.html')
    


    


 




