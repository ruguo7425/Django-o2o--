from django.contrib.auth.decorators import login_required


class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        view_fun = super().as_view(**initkwargs)
        view_fun = login_required(view_fun)
        return view_fun
