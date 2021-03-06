from random import sample
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import FormView
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from whowin.forms import FighterSelectForm, ContactForm
from whowin.models import Fight, Fighter



class FightView(FormView):

    fight = None
    template_name = 'whowin/match.html'

    def get_success_url(self):
        return reverse('home')

    def get_context_data(self, **kwargs):
        context = super(FightView, self).get_context_data(**kwargs)
        context['m1'] = Fighter.objects.get(id=self.kwargs['f1'])
        context['m2'] = Fighter.objects.get(id=self.kwargs['f2'])
        return context

    def get_form(self, form_class):

        if self.kwargs['f1'] == self.kwargs['f2']:
            self.template_name = '404.html'

        a = Fighter.objects.get(id=self.kwargs['f1'])
        b = Fighter.objects.get(id=self.kwargs['f2'])
        if self.request.user.is_authenticated():
            self.fight = Fight(member1=a, member2=b, member1_start_rank=a.rank,
                               member2_start_rank=b.rank, member1_start_rating=a.rating,
                               member2_start_rating=b.rating, user=self.request.user)
        else:
            self.fight = Fight(member1=a, member2=b, member1_start_rank=a.rank,
                               member2_start_rank=b.rank, member1_start_rating=a.rating,
                               member2_start_rating=b.rating, user=None)

        choices = [(self.fight.member1.id, self.fight.member1.name),
                   (self.fight.member2.id, self.fight.member2.name)]
        kwargs = super(FightView, self).get_form_kwargs()
        kwargs.update({"choices": choices})
        form = FighterSelectForm(**kwargs)
        return form

    def form_valid(self, form):
        win = Fighter.objects.get(
            id=form.cleaned_data['who_would_win_in_a_fight_between'])

        if win == self.fight.member1:
            lose = self.fight.member2
        else:
            lose = self.fight.member1
        self.fight.rankupdate(win)
        self.fight.member1_end_rating = self.fight.member1.rating
        self.fight.member2_end_rating = self.fight.member2.rating
        self.fight.winner = win
        self.fight.loser = lose
        self.fight.save()

        fighterlist = list(Fighter.objects.order_by('-rating', 'name'))
        for fighter in fighterlist:
            r = fighterlist.index(fighter)
            r += 1
            fighter.rank = r
            fighter.save()

        fighter1 = Fighter.objects.get(id=self.fight.member1.id)
        fighter2 = Fighter.objects.get(id=self.fight.member2.id)
        self.fight.member1_end_rank = fighter1.rank
        self.fight.member2_end_rank = fighter2.rank
        self.fight.save()

        return super(FightView, self).form_valid(form)


class TopTenView(ListView):
    queryset = Fighter.objects.order_by('-rating')[:10]
    context_object_name = 'fighter_list'
    template_name = 'whowin/topten.html'


class BottomTenView(ListView):
    queryset = Fighter.objects.order_by('rating')[:10]
    context_object_name = 'fighter_list'
    template_name = 'whowin/bottomten.html'


class FighterDetailView(DetailView):
    model = Fighter
    template_name = 'whowin/fighterdetail.html'

    def get_context_data(self, **kwargs):
        context = super(FighterDetailView, self).get_context_data(**kwargs)
        data = []
        for fight in Fight.objects.all():
            if fight.member1 == self.object:
                data.append(fight.member1_end_rating)
            elif fight.member2 == self.object:
                data.append(fight.member2_end_rating)
            else:
                pass

        fightswon = Fight.objects.filter(winner=self.object).count()
        fightslost = Fight.objects.filter(loser=self.object).count()
        context['won'] = fightswon
        context['lost'] = fightslost
        context['ratings'] = data
        return context


class FighterListView(ListView):
    template_name = 'whowin/fighterlist.html'
    context_object_name = 'all_fighters'
    queryset = Fighter.objects.order_by('name')


class AboutView(TemplateView):
    template_name = 'whowin/about.html'


class StatsView(TemplateView):

    template_name = 'whowin/stats.html'

    def get_context_data(self, **kwargs):
        context = super(StatsView, self).get_context_data(**kwargs)
        total = Fight.objects.count()
        num = Fighter.objects.count()
        context['total'] = total
        context['numfighters'] = num
        return context


class ContactView(FormView):
    template_name = 'whowin/contact.html'
    form_class = ContactForm

    def get_success_url(self):
        return reverse('success')

    def form_valid(self, form):
        form.send_email()
        return super(ContactView, self).form_valid(form)


class SuccessView(TemplateView):
    template_name = 'whowin/success.html'


def home_view(request):
    fi1, fi2 = sample(Fighter.objects.all(), 2)

    return HttpResponseRedirect(reverse('fight', kwargs={'f1': fi1.id,
                                                         'f2': fi2.id
                                                         }))


class UserStatsView(TemplateView):
    template_name = 'whowin/userstats.html'

    def dispatch(self, request, *args, **kwargs):

        if not self.request.user.is_authenticated():
            return redirect('/account/login/')
        else:
            return super(UserStatsView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(UserStatsView, self).get_context_data(**kwargs)
        context['user'] = self.request.user
        context['total'] = Fight.objects.filter(user=self.request.user).count()
        context['previous5'] = Fight.objects.filter(user=self.request.user).order_by('start').reverse()[:5]
        return context
