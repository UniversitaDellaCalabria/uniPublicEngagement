"""uniPublicEngagement URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include

# from rest_framework.documentation import include_docs_urls
# from rest_framework.schemas import get_schema_view


urlpatterns = [
    path(f'{settings.ADMIN_PATH}/', admin.site.urls),
    # path('docs/', include_docs_urls(title=API_TITLE, description=API_DESCRIPTION)),
    # path('schema/', get_schema_view(title=API_TITLE)),
]

urlpatterns += path('', include('pe_management.urls', namespace='public_engagement')),
urlpatterns += path('', include('template.urls', namespace='template')),
urlpatterns += path('', include('accounts.urls', namespace='accounts')),

if 'saml2_sp' in settings.INSTALLED_APPS:
    from djangosaml2 import views as saml2_views

    import saml2_sp.urls

    urlpatterns += path('', include((saml2_sp.urls, 'sp',))),

    urlpatterns += path('{}/login/'.format(settings.SAML2_URL_PREFIX),
                        saml2_views.LoginView.as_view(), name='login'),
    urlpatterns += path('{}/acs/'.format(settings.SAML2_URL_PREFIX),
                        saml2_views.AssertionConsumerServiceView.as_view(), name='saml2_acs'),
    urlpatterns += path('{}/logout/'.format(settings.SAML2_URL_PREFIX),
                        saml2_views.LogoutInitView.as_view(), name='logout'),
    urlpatterns += path('{}/ls/'.format(settings.SAML2_URL_PREFIX),
                        saml2_views.LogoutView.as_view(), name='saml2_ls'),
    urlpatterns += path('{}/ls/post/'.format(settings.SAML2_URL_PREFIX),
                        saml2_views.LogoutView.as_view(), name='saml2_ls_post'),
    urlpatterns += path('{}/metadata/'.format(settings.SAML2_URL_PREFIX),
                        saml2_views.MetadataView.as_view(), name='saml2_metadata'),
else:
    urlpatterns += path('{}/login/'.format(settings.LOCAL_URL_PREFIX),
                        auth_views.LoginView.as_view(
                            template_name='login.html'),
                        name='login'),
    urlpatterns += path('{}/logout/'.format(settings.LOCAL_URL_PREFIX),
                        auth_views.LogoutView.as_view(
                            template_name='logout.html', next_page='/'),
                        name='logout'),
