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
from .models import Tour, Destination, Cart, Booking, FavouriteDestination
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import date
import razorpay
from django.conf import settings
from datetime import date
from django.views.decorators.csrf import csrf_exempt
# Create your views here.

def tour(request):
    tour_types = Tour.objects.values_list('tour_type', flat=True).distinct()
    return render(request, 'tour.html', {
        'tour_types': tour_types,
    })

def tour_by_type(request, tour_type):
    tours = Tour.objects.filter(tour_type=tour_type)
    return render(request, 'tour_by_type.html', {
        'tours': tours,
        'tour_type': tour_type,
    })

def toggle_favourite(request, dest_id):
    if 'email' not in request.session:
        return redirect('login')
    
    user = User.objects.get(email=request.session['email'])
    destination = get_object_or_404(Destination, id=dest_id)
    
    fav, created = FavouriteDestination.objects.get_or_create(user=user, destination=destination)
    
    if not created:
        fav.delete()  
    
    return redirect('destination')


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
    destinations = Destination.objects.all()
    countries = destinations.values_list('country', flat=True).distinct()
    national_tours = Tour.objects.filter(category='national') 
    international_tours = Tour.objects.filter(category='international') 
    tour_types = Tour.objects.values_list('tour_type', flat=True).distinct()
    liked_ids = []
    if 'email' in request.session:
        user = User.objects.get(email=request.session['email'])
        liked_ids = FavouriteDestination.objects.filter(user=user).values_list('destination_id', flat=True)
    
    return render(request, 'index.html', {
        'destinations': destinations,
        'countries': countries,
        'liked_ids': liked_ids,
        'national_tours':national_tours,
        'international_tours':international_tours,
        'tour_types':tour_types,
    })

def about(request):
    return render(request,'about.html')

def services(request):
    return render(request,'services.html')

def blog(request):
    return render(request,'blog.html')

def contact(request):
    return render(request,'contact.html')


def destination(request):
    destinations = Destination.objects.all()
    countries = destinations.values_list('country', flat=True).distinct()
    
    liked_ids = []
    if 'email' in request.session:
        user = User.objects.get(email=request.session['email'])
        liked_ids = FavouriteDestination.objects.filter(user=user).values_list('destination_id', flat=True)
    

    return render(request, 'destination.html', {
        'destinations': destinations,
        'countries': countries,
        'liked_ids': liked_ids,
    })

def add_tour(request):
    if 'email' not in request.session:
        return redirect('login')
    
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

def add_to_cart(request,id):
    if 'email' not in request.session:
        return redirect('login')

    if request.method == "POST":
        tour_id = request.POST.get('tour_id')
        tour_date = request.POST.get('tour_date')
        persons = int(request.POST.get('persons', 1))
        tour = Tour.objects.get(id=tour_id)
        user = User.objects.get(email=request.session['email'])
        total = tour.price_per_person * persons
        Cart.objects.create(
            user = user,
            tour = tour,
            tour_date = tour_date,
            tour_quantity = persons,
            tour_price = tour.price_per_person,
            total_price = total
        )
        return redirect('booking_success', id)

def booking(request, tour_id):
    if 'email' not in request.session:
        return redirect('login')
    
    tour = get_object_or_404(Tour, id=tour_id)
    return render(request, 'booking.html', {
        'tour': tour,
        'today': date.today().isoformat()  # date picker mein past date disable hoga
    })


def create_booking(request, tour_id):
    if 'email' not in request.session:
        return redirect('login')
    
    if request.method == 'POST':
        tour = get_object_or_404(Tour, id=tour_id)
        user = User.objects.get(email=request.session['email'])
        
        tour_date = request.POST.get('tour_date')
        persons = int(request.POST.get('persons', 1))
        total_price = tour.price_per_person * persons

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        order = client.order.create({
            "amount": int(total_price * 100),
            "currency": "INR",
            "payment_capture": 1
        })

        request.session['pending_booking'] = {
            'tour_id': tour.id,
            'tour_date': str(tour_date),
            'total_persons': persons,
            'total_price': str(total_price),
            'razorpay_order_id': order['id'],
        }

        return render(request, 'payment_page.html', {
            'tour': tour,
            'user': user,
            'persons': persons,
            'total_price': total_price,
            'amount_paise': int(total_price * 100),
            'razorpay_key': settings.RAZORPAY_KEY_ID,
            'razorpay_order_id': order['id'],
        })
    
    return redirect('packages')

@csrf_exempt
def payment_success(request):
    if request.method == 'POST':
        payment_id = request.POST.get('razorpay_payment_id')
        order_id   = request.POST.get('razorpay_order_id')
        signature  = request.POST.get('razorpay_signature')

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        try:
            client.utility.verify_payment_signature({
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            })

            pending = request.session.get('pending_booking')
            if not pending:
                return redirect('packages')

            user = User.objects.get(email=request.session['email'])
            tour = get_object_or_404(Tour, id=pending['tour_id'])

            booking = Booking.objects.create(
                user=user,
                tour=tour,
                tour_date=pending['tour_date'],
                total_persons=pending['total_persons'],
                total_price=pending['total_price'],
                razorpay_order_id=pending['razorpay_order_id'],
                razorpay_payment_id=payment_id,
                is_paid=True
            )

            del request.session['pending_booking']

            return render(request, 'payment_success.html', {'booking': booking})

        except:
            return render(request, 'payment_failed.html')
    
    return redirect('packages')


def view_tour(request):
    if 'email' not in request.session:
        return redirect('login')
    
    user = User.objects.get(email = request.session['email'])
    tours = Tour.objects.filter(user=user)
    return render(request, 'view_tour.html', {'tours': tours})


def edit_tour(request,pk):
    if 'email' not in request.session:
        return redirect('login')
    
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




def packages(request):
    tours = Tour.objects.all()
    return render(request,'packages.html', {'tours': tours})


def tour_details(request):
    return render(request, 'tour_details.html')


def delete_tour(request, pk):
    tour = get_object_or_404(Tour, id=pk)
    tour.delete()
    return redirect('view_tour')


def update_tour(request):
    return render(request, 'update_tour.html')


def profile(request):
    user = User.objects.get(email=request.session['email'])
    countries = [country.name for country in pycountry.countries]
    favourites = FavouriteDestination.objects.filter(user=user).select_related('destination')
    favourite_count = favourites.count()
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
        return render(request, "profile.html", {'user': user,'countries': countries,'favourites': favourites,'favourite_count':favourite_count})

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
            message =f"Hi {user.fname}  {user.lname}  Your OTP  is {str(otp)}"
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