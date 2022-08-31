from pydoc import describe
from tabnanny import check
from turtle import clear
from django.db.models.expressions import Expression
from django.forms.utils import to_current_timezone
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.http import JsonResponse
from django.core import serializers
from django.views.generic import View
from .models import Icon, Rating, Toilet, ToiletImage, UserSetting, UpdateToilet, UpdateToiletImage
from .forms import SearchForm, AddForm
from folium.features import CustomIcon
from folium.plugins import MarkerCluster, LocateControl

from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
User = get_user_model()

import folium, geocoder, random, requests, jinja2, re


class JsonListView(View):
    def get(self, request, *args, **kwargs):

        try:
            user = User.objects.get(id=request.user.id)
            rating = list(Rating.objects.filter(author=user).values())
        except:
            rating = []

        
        return JsonResponse({"data": rating}, content_type="text/json-comment-filtered")

def log(*args, **kwargs):
    WARNING = f'\033[94m\033[1m{args[0]}'
    ENDC = '\033[0m'
    
    args = list(args)
    args.pop(0)
    args = tuple(args)
    args = (WARNING, *args, ENDC)

    print(*args, **kwargs)

def get_links(request):
    links = ["https://google.com"]
    return redirect(random.choice(links))

def get_client_ip(request):
   x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
   if x_forwarded_for:
       ip = x_forwarded_for.split(',')[0]
   else:
       ip = request.META.get('REMOTE_ADDR')
   return ip

def get_client_loc(ip):
    if settings.DEBUG == True: ip = '87.244.235.149'
    
    url = f'http://ip-api.com/json/{ip}'
    response = requests.get(url)
    return response.json()

def edit_map_style(m, style):
    m_start = m[:36]
    m_end   = m[97:]
    return m_start + style + m_end

def email_valid(email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

    if(re.fullmatch(regex, email)):
        return True
    else:
        return False

def average(lst):
    if not lst: return 'undefined'
    return round(( sum(lst) / len(lst) ), 2)

def is_none(toilet, field):
    if str(toilet) == field or field == "":
        return None
    else: 
        return field

# Create your views here.
def index(request):
    geo_info = get_client_loc(get_client_ip(request))
    
    lat = geo_info['lat']
    lng = geo_info['lon']
    user_loc = True
    form = SearchForm()
    
    if request.method == 'POST':
        if "address" in request.POST:
            form = SearchForm(request.POST)
            address = form.data['address']
            
            location = geocoder.osm(address)
            lat = location.lat
            lng = location.lng
            user_loc = False
            
            if lat == None and lng == None:
                lat = geo_info['lat']
                lng = geo_info['lon']
                user_loc = True
                
        elif any(i in request.POST for i in ['update', 'updateForm']):
            return updateForm(request)            
        elif "add" in request.POST:
            return addForm(request)
        elif "update" in request.POST:
            return updateForm(request)
        else:
            return addFormSubmit(request)

    
            

        
    m = folium.Map(location=[lat, lng], zoom_start=14)
    LocateControl(auto_start=user_loc).add_to(m)
    marker_cluster = MarkerCluster().add_to(m)
    
    
    latlngpop = folium.LatLngPopup()

    latlngpop._template = jinja2.Template("""
        {% macro script(this, kwargs) %}
        
            var markerIcon = L.icon({
                "iconUrl": '/media/icons/point.png',
                "iconSize": [22, 22],
                });
                
            var {{this.get_name()}};
            
            function latLngPop(e) {
                if ({{this.get_name()}}) {
                    {{this.get_name()}}.setLatLng(e.latlng);
                }
                else{
                    {{this.get_name()}} = new L.Marker([e.latlng.lat, e.latlng.lng], {icon: markerIcon}).addTo({{this._parent.get_name()}});
                }
                
                parent.abc(e.latlng.lat.toFixed(4), e.latlng.lng.toFixed(4));
                
            }{{this._parent.get_name()}}.on('click', latLngPop);
            
            
            
        {% endmacro %}
    """)
    m.add_child(latlngpop)
    
    
    toilets = Toilet.objects.filter(submited=True)
    for t in toilets:
        
        icon_size = t.icon.size
        icon_size = icon_size.split(',')
        icon_anchor = t.icon.anchor
        icon_anchor = icon_anchor.split(',')
        
        icon_image = f"{settings.MEDIA_ROOT}/{str(t.icon.icon)}"
        
        photos = ToiletImage.objects.filter(toilet=t)
        photos_array = []
        for j in photos:
            photo = str(j.images)
            photos_array.append(photo)
        
        user_rating = Rating.objects.filter(toilet=t)
        
        overall_rating = average([i.rating for i in user_rating])
        
        a = u"""
        var {{this.get_name()}} = L.popup();
        function fun{{this.get_name()}}(e) {
                    var a = *A;

                    parent.showPops(a);
                    console.log({{this.get_name()}});
                }
        {{this._parent.get_name()}}.on('click', fun{{this.get_name()}});"""
        
        g = [
            t.title,
            t.description,
            photos_array,
            float(t.price),
            str(t.author),
            t.id,
            overall_rating,
            str([str(t.lat), str(t.lon)]),
        ]
        a = a.replace("*A", f'{g}')


        popup = folium.Popup(t.title)
        popup._template = jinja2.Template(a)
    
        
        icon = CustomIcon(icon_image, icon_size=(int(icon_size[0]),int(icon_size[1])), popup_anchor=(int(icon_anchor[0]),int(icon_anchor[1])),)
        folium.Marker([t.lat, t.lon], popup=popup, icon=icon).add_to(marker_cluster)
    

    
    m = m._repr_html_()
    m = edit_map_style(m, "position:absolute;width:100%;height:93.6%; padding:0; margin:0;")
    
    
    context={
        'm': m,
        'form': form,
    }
    return render(request, 'index.html', context)


@login_required
def addForm(request):
    form = SearchForm(request.POST)
    add = 0
    add = form.data['add']
    add = add.split(",")

    form = AddForm(initial={'lat': add[0], 'lon': add[1]})
    
    m = folium.Map(location=[add[0], add[1]], zoom_start=25, zoom_control=False, scrollWheelZoom=False, dragging=False)

    icon = CustomIcon(f"{settings.MEDIA_ROOT}/icons/point.png", icon_size=(22,22), popup_anchor=(0, -10),)
    folium.Marker([add[0], add[1]], icon=icon).add_to(m)
    
    m = edit_map_style(m._repr_html_(), 'position:absolute;width:50%;height:30%;padding:0; margin:0; margin-left:25%; margin-top:2%; margin-bottom:2%;')

    context={
        'add': add,
        'form': form,
        'lan': add[0],
        'lon': add[1],
        'm': m,
    }
    return render(request, 'add.html', context)


@login_required
def updateForm(request):
    
    
    if "update" not in request.POST:
        POST = request.POST
        
        
        toilet = Toilet.objects.get(id=POST['id'])
        
        if POST.get("delete") == "True":
            toilet = UpdateToilet.objects.create(toilet_id=toilet, clear=True)
            return redirect('/')
            
        title =       is_none(toilet.title, POST.get("title"))
        lat =         is_none(toilet.lat, POST.get("lat"))
        lon =         is_none(toilet.lon, POST.get("lon"))
        description = is_none(toilet.description, POST.get("description"))
        images = request.FILES.getlist('images')
        if POST.get('price') == "" and toilet.price == 0: price = None
        elif POST.get('price') == "": price = 0
        else: price = POST.get('price') 

        
        
        toilet = UpdateToilet.objects.create(
            toilet_id=toilet, 
            title=title, 
            lat=lat, 
            lon=lon, 
            description=description, 
            price=price
            )

            
        for image in images: 
            UpdateToiletImage.objects.create(
                toilet=toilet,
                images=image
                )
        
        
        return redirect('/')
    
    
    
    
    form = SearchForm(request.POST)
    id = form.data["update"]
    
    toilet = Toilet.objects.get(id=id)
    photos = ToiletImage.objects.filter(toilet=toilet)
    
    photos_array = []
    for p in photos:
        photos_array.append(str(p.images.url))
        
    
    context={
        'toilet': toilet,
        'photos': photos_array,
    }
    return render(request, 'update.html', context)


def addFormSubmit(request):
    

    title = request.POST.get('title')
    lat = request.POST.get('lat')
    lon = request.POST.get('lon')
    description = request.POST.get('description')
    user = request.user
    icon = request.POST.get('icon')
    images = request.FILES.getlist('images')
    price = request.POST.get('price')
    if price == '': price = 0
    
    toilet = Toilet.objects.create(
        title=title,
        lat=lat,
        lon=lon,
        description=description,
        author=User.objects.get(id=user.id),
        icon=Icon.objects.all()[int(icon)-1],
        price = price,
    )
    
    for i in range(0, len(images)): 
        log(images[i])
        ToiletImage.objects.create(
            toilet=toilet,
            images=images[i]
        )
    return redirect('/')
  
    
def profile(request, id):
    
    if type(id) is int:    
        user = User.objects.get(id=id)
    else:
        user = User.objects.get(username__iexact=id)
    
    settings = UserSetting.objects.get(user=user)
    toilets = Toilet.objects.filter(author=user, submited=True)
    rating = Rating.objects.filter(author=user)
    
    log(rating)
    
    context = {
        'profile': user,
        'toilets' : toilets,
        'toilets_count': len(toilets),
        'settings': settings,
        'rating' : rating,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def edit_profile(request):
    
    user = User.objects.get(username = request.user)
    settings = UserSetting.objects.get(user=user)
    
    if request.method == 'POST':

        if 'newpassword' in request.POST:
            old = request.POST.get('currentpassword')
            new = request.POST.get('newpassword')
            
            if user.check_password(old):
                user.set_password(new)
                log(old, new)
                #user.save()
                #login(request, user)
                
            
            else: log("NOT! password")
            
        elif 'newemail' in request.POST:
            currentpassword = request.POST.get('currentpassword')
            newemail = request.POST.get('newemail')
            
            if user.check_password(currentpassword) and email_valid(newemail):
                try: 
                    valid = User.objects.get(email = newemail)
                    log('NOT! email')
                except:
                    log(currentpassword, newemail)
                    user.email = newemail
                    #user.save()
                    #user@user.com
        
        elif 'newusername' in request.POST:
            currentpassword = request.POST.get('currentpassword')
            newusername = request.POST.get('newusername')
            
            if user.check_password(currentpassword):
                log(user, newusername)
                user.username = newusername
                user.save()
                
        elif 'bio' in request.POST:
            bio = request.POST.get('bio')
            
            settings.bio = bio
            settings.save()
            
                
    context = {
        'user': user,
        'settings': settings,
    }
    return render(request, 'accounts/edit-profile.html', context)


@staff_member_required
def submit(request):
    

    if request.get_full_path() == '/submit/add/':
        
        toilets = Toilet.objects.filter(submited=False)
        photos_array = []
        for t in toilets:
            photos = ToiletImage.objects.filter(toilet=t)
            photos_array.append(photos[0].images)

        
        toiletlist = zip(toilets, photos_array)
        
        context = {
            "media" : settings.MEDIA_URL,
            "list"  : toiletlist,
            
        }
        return render(request, 'submit.html', context)
    
    else:
        
        context = {
            "media" : settings.MEDIA_URL,
            "list"  : UpdateToilet.objects.all(),
            
        }
        return render(request, 'submitUpdate.html', context)


@staff_member_required
def submit_detail(request, id):
    if request.method == 'POST':
        submit = request.POST.get('submit')
        
        if '/submit/add/' in request.get_full_path() :
            toilet = Toilet.objects.get(id=id)
            
            
            if submit == 'True':
                toilet.submited = True
                toilet.save()
            else:
                toilet.delete()

            return redirect('/submit/add/')
        
        else:
            toilet = UpdateToilet.objects.get(id=id)
            photos = UpdateToiletImage.objects.filter(toilet=toilet)
            
            old_toilet = toilet.toilet_id
            old_photos = ToiletImage.objects.filter(toilet=old_toilet)
            
            
            #return redirect('/submit/update/')
            
            if submit == 'True':
                if toilet.clear: 
                    old_toilet.delete()
                    return redirect('/submit/update/')
                
                if toilet.title: old_toilet.title = toilet.title
                if toilet.description: old_toilet.description = toilet.description
                
                if toilet.price != None:
                    if old_toilet.price == 0: 
                        old_toilet.icon = Icon.objects.get(id=2)
                    elif old_toilet.price > 0 and toilet.price == 0: 
                        old_toilet.icon = Icon.objects.get(id=1)
                    
                    old_toilet.price = toilet.price
                    
                if photos:
                    for photo in photos:
                        ToiletImage.objects.create(
                            toilet = old_toilet,
                            images = photo.images
                        )
                
                old_toilet.save()
                
            
            toilet.delete()
           
            return redirect('/submit/update/')
    
    
    if '/submit/add/' in request.get_full_path() :
    
        toilet = get_object_or_404(Toilet, id=id)
        photos = ToiletImage.objects.filter(toilet=toilet)
        
        photos_array = []
        for p in photos:
            photos_array.append(str(p.images.url))
        
        lat = toilet.lat
        lon = toilet.lon
        m = folium.Map(location=[lat, lon], zoom_start=25, zoom_control=False, scrollWheelZoom=False, dragging=False)
        icon = CustomIcon(f"{settings.MEDIA_ROOT}/icons/point.png", icon_size=(22,22), popup_anchor=(0, -10),)
        folium.Marker([lat, lon], icon=icon).add_to(m)
        m = edit_map_style(m._repr_html_(), 'position:absolute;width:50%;height:30%;padding:0;margin:0;margin-left:50%;margin-top:0%;margin-bottom:2%')
        
        context = {
            'media' : settings.MEDIA_URL,
            'toilet' : toilet,
            'photos' : photos_array,
            'm' : m,
        }
        return render(request, 'submitdetail.html', context)
    
    else:
        
        toilet = get_object_or_404(UpdateToilet, id=id)
        photos = UpdateToiletImage.objects.filter(toilet=toilet)
        
        photos_array = []
        for p in photos:
            photos_array.append(str(p.images.url))
        
        
        old = toilet.toilet_id
        
        old_photos = ToiletImage.objects.filter(toilet=old)
        old_photos_array = []
        for p in old_photos:
            old_photos_array.append(str(p.images.url))
        

        lat, lon = old.lat, old.lon
        m = folium.Map(location=[lat, lon], zoom_start=25, zoom_control=False, scrollWheelZoom=False, dragging=False)
        icon = CustomIcon(f"{settings.MEDIA_ROOT}/icons/point.png", icon_size=(22,22), popup_anchor=(0, -10),)
        folium.Marker([lat, lon], icon=icon).add_to(m)
        m = edit_map_style(m._repr_html_(), 'position:absolute;width:50%;height:30%;padding:0;margin:0;margin-left:50%;margin-top:0%;margin-bottom:2%')
        
        
        context = {
            'media' : settings.MEDIA_URL,
            'toilet' : toilet,
            'photos' : photos_array,
            'old_photos' : old_photos_array,
            'old' : old,
            'm' : m,
        }
        return render(request, 'submitdetailUpdate.html', context)
        
    
def login_view(request):
    logout(request)
    
    
    username = password = error = ''
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(username=username, password=password)

        if user is None:
            try:
                username = User.objects.get(email=username)
                user = authenticate(username=username, password=password)
            
            except User.DoesNotExist:
                error = "Wrong username or password"
        
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('/')
    
    context = {
            "error": error,
        }
    return render(request, 'accounts/login.html', context)


def registration_view(request):
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        
        errors = []
        
        if not email_valid(email):
            errors.append("takyto email mat nemozes")
        try:    
            if User.objects.get(username__iexact=username) is not None:
                errors.append("Vymysli si lepsie meno.")
        except: pass
        try:    
            if User.objects.get(email=email) is not None:
                errors.append("Chces mi povedat ze nemas vlastny email.")
        except: pass
        
        context = {
            "errors": errors,
        }
        if errors:
            return render(request, "accounts/register.html", context)
        
        
        user = User.objects.create_user(
            username = username, 
            email = email,
            password = password,
        )
        settings = UserSetting.objects.create(user=user,)
        return redirect('/')
        

    context = {}
    return render(request, "accounts/register.html", context)


def toilet_page(request, id):
    print(id)
    
    toilet = Toilet.objects.get(id=id)
    if not toilet.submited : return redirect('/')
    
    photos = ToiletImage.objects.filter(toilet=toilet)
    
    lat = toilet.lat
    lon = toilet.lon
    m = folium.Map(location=[lat, lon], zoom_start=25, zoom_control=False, scrollWheelZoom=False, dragging=False)

    icon = CustomIcon(f"{settings.MEDIA_ROOT}/icons/point.png", icon_size=(22,22), popup_anchor=(0, -10),)
    folium.Marker([lat, lon], icon=icon).add_to(m)
    
    m = edit_map_style(m._repr_html_(), 'position:absolute;width:50%;height:30%;padding:0; margin:0; margin-left: 50%;')
    
    context = {
        'media' : settings.MEDIA_URL,
        'toilet' : toilet,
        'photos' : photos,
        'm' : m,
    }

    return render(request, 'toiletpage.html', context)


def rating(request):
    
    author_id = request.POST.get('author_id')
    toilet_id = request.POST.get('toilet_id')
    rating = request.POST.get('rating')
    
    
    user = User.objects.get(id=int(author_id))
    toilet = Toilet.objects.get(id=int(toilet_id))
    
    try:
        rate = Rating.objects.get(author=user, toilet=toilet)
        rate.rating = rating
        rate.save()
    except:
        rate = Rating.objects.create(
            toilet = toilet,
            author=user,
            rating=rating,
        )
    
    return HttpResponse("")


# python manage.py migrate --run-syncdb 
# python manage.py makemigrations
# python manage.py migrate
# python manage.py runserver_plus --cert-file 127.0.0.1.pem --key-file 127.0.0.1-key.pem



# python manage.py runserver_plus --cert-file 127.0.0.1.crt --key-file 127.0.0.1-key.key
# python manage.py runserver_plus --cert-file cert.pem --key-file key.pem