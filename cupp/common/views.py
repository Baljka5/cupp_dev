from django.views import generic as g
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.models import Group

from cupp import constants as c
from cupp.point.models import Type

from cupp.common.forms import MySettingsForm


class Map(LoginRequiredMixin, g.TemplateView):
    template_name = 'common/map.html'

    def get_template_names(self):
        # Check if the user is a superuser
        if self.request.user.is_superuser:
            return [self.template_name]
        elif self.request.user.groups.filter(name='Event').exists():
            return ['event/show.html']
        elif self.request.user.groups.filter(name='Store Trainer').exists():
            return ['store_trainer/show.html']
        elif self.request.user.groups.filter(name='license').exists():
            return ['license/show.html']
        elif self.request.user.groups.filter(name='legal_team').exists():
            return ['license/show.html']
        elif self.request.user.groups.filter(name='Store planner').exists():
            return ['common/map.html']
        elif self.request.user.groups.filter(name='Store Consultant').exists():
            return ['store_consultant/show.html']
        elif self.request.user.groups.filter(name='Store Consultant').exists():
            return ['competitors/show.html']
        elif self.request.user.groups.filter(name='Area').exists():
            return ['competitors/show.html']
        elif self.request.user.groups.filter(name='SC Direct').exists():
            return ['competitors/show.html']
        elif self.request.user.groups.filter(name='Area').exists():
            return ['store_consultant/show.html']
        elif self.request.user.groups.filter(name='SC Direct').exists():
            return ['store_consultant/show.html']
        elif self.request.user.groups.filter(name='Rent').exists():
            return ['rent/show.html']
        elif self.request.user.groups.filter(name='ST Manager').exists():
            return ['store_trainer/show.html']
        elif self.request.user.groups.filter(name='plannig_manager').exists():
            return ['store_consultant/index.html']
        return [self.template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['types'] = Type.objects.all()
        context['types'] = c.CHOICES_POINT_TYPE
        context['grades'] = c.CHOICES_POINT_GRADE
        context['users'] = User.objects.all()
        return context


class MySettings(LoginRequiredMixin, g.FormView):
    template_name = 'common/my_settings.html'
    form_class = MySettingsForm
    success_url = reverse_lazy('my_settings')

    def get_initial(self):
        initial = super().get_initial()
        user = self.request.user

        initial['first_name'] = user.first_name
        initial['last_name'] = user.last_name

        return initial

    def form_valid(self, form):
        user = self.request.user

        user.first_name = form.cleaned_data['first_name']
        user.last_name = form.cleaned_data['last_name']
        user.save()

        messages.add_message(self.request, messages.INFO, c.MSG_SAVED)

        return super().form_valid(form)
