from django.conf.urls import url
from django.contrib import admin
from django.utils import six

from admin_sso import settings
from admin_sso.forms import AssignmentForm
from admin_sso.models import Assignment


class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['__str__' if six.PY3 else '__unicode__', 'user', 'weight',
                    'create_user', 'make_superuser', 'group_list']
    raw_id_fields = ['user']
    form = AssignmentForm

    fields = ['domain', 'username_mode', 'username', 'weight', 'user',
              'create_user', 'make_superuser', 'groups']

    def group_list(self, obj):
        return ', '.join(obj.groups.all().values_list('name', flat=True))

    def get_urls(self):
        from admin_sso.views import start, end
        info = (self.model._meta.app_label, self.model._meta.model_name)
        return [
            url(r'^start/$', start,
                name='%s_%s_start' % info),
            url(r'^end/$', end,
                name='%s_%s_end' % info),
        ] + super(AssignmentAdmin, self).get_urls()

admin.site.register(Assignment, AssignmentAdmin)


if settings.DJANGO_ADMIN_SSO_ADD_LOGIN_BUTTON:
    admin.site.login_template = 'admin_sso/login.html'
