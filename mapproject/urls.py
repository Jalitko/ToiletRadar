"""mapproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib import auth
from django.urls import path, include
from jinja2.environment import Template
from map import views as map_views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', map_views.index, name='index'),
    path('link/', map_views.get_links, name='link'),
    path('userrating/', map_views.JsonListView.as_view(), name='json-view'),
    
    
    path('accounts/signup/', map_views.registration_view, name='signup'),
    path('accounts/login/', map_views.login_view, name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/edit/', map_views.edit_profile, name='edit_profile'),
    path('profile/<int:id>/', map_views.profile, name='profile'),
    path('profile/<str:id>/', map_views.profile, name='profile'),
    
    #path('submit/', map_views.submit, name='submit'),
    path('submit/add/', map_views.submit, name='submit'),
    path('submit/update/', map_views.submit, name='submitUpdate'),
    path('submit/add/<int:id>/', map_views.submit_detail, name='submit_detail'),
    path('submit/update/<int:id>/', map_views.submit_detail, name='submit_detailUpdate'),
    
    path('toilet/<int:id>/', map_views.toilet_page, name='toilet_page'),
    
    path('ratingform/', map_views.rating, name='rating'),
    
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

#urlpatterns += patterns('', (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}))



