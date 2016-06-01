from django.views.generic.base import TemplateView
from django.http import HttpResponse

from actionlog.mixins import LogActionMixin
from actionlog.models import ActionLogEntry
from draw.models import Debate
from tournaments.mixins import RoundMixin
from utils.mixins import SuperuserRequiredMixin, PostOnlyRedirectView
from utils.misc import reverse_round

from .models import Venue
from .allocator import allocate_venues

class EditVenuesView(SuperuserRequiredMixin, RoundMixin, TemplateView):

    template_name = "venues_edit.html"

    def get_context_data(self, **kwargs):
        kwargs['draw'] = self.get_round().get_draw()
        return super().get_context_data(**kwargs)


class AutoAllocateVenuesView(LogActionMixin, SuperuserRequiredMixin, RoundMixin, PostOnlyRedirectView):

    def get_redirect_url(self):
        return reverse_round('venues-edit', self.get_round())

    def post(self, request, *args, **kwargs):
        allocate_venues(self.get_round())
        return super().post(request, *args, **kwargs)


class SaveVenuesView(LogActionMixin, SuperuserRequiredMixin, RoundMixin, PostOnlyRedirectView):

    action_log_type = ActionLogEntry.ACTION_TYPE_VENUES_SAVE

    def post(self, request, *args, **kwargs):

        def v_id(a):
            try:
                return int(request.POST[a].split('_')[1])
            except IndexError:
                return None

        data = [(int(a.split('_')[1]), v_id(a)) for a in list(request.POST.keys())]

        debates = Debate.objects.in_bulk([d_id for d_id, _ in data])
        venues = Venue.objects.in_bulk([v_id for _, v_id in data])
        for debate_id, venue_id in data:
            debates[debate_id].venue = venues[venue_id] if venue_id is not None else None
            debates[debate_id].save()

        self.log_action()
        return HttpResponse("ok")