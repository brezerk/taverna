
from django.shortcuts import render_to_response
from django.core.context_processors import csrf

def rr(template):
    def decor(view):
        def wrapper(request, *args, **kwargs):
            val = view(request, *args, **kwargs)
            if type(val) == type({}):
                val.update({'user': request.user})
                val.update(csrf(request))
                return render_to_response(template, val)
            else:
                return val
        return wrapper
    return decor

