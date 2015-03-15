__author__ = 'jblowe'

import operator

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, render_to_response
from django import forms

from utils import loginfo, Dispatch, appLayout, setConstants, APPS

@login_required()
def index(request):
    # APPS is a dict of configured webapps, show the list sorted by "app title"
    sorted_apps = sorted(APPS.items(), key=operator.itemgetter(1))
    context = setConstants({'apps': sorted_apps}, 'listapps')
    return render(request, 'toolbox.html', context)


@login_required()
def tool(request, appname):
    # if we are here, we have been given a particular appname, e.g. "keyinfo", as part of the url
    context = {'applayout': appLayout[appname]}
    if request.method == 'POST':
        form = forms.Form(request.POST)

        if form.is_valid():
            loginfo(appname, context, request)
            context = Dispatch(context, request)
    else:
        form = forms.Form()

    context['form'] = form
    context = setConstants(context, appname)
    loginfo(appname, context, request)
    return render(request, 'toolbox.html', context)
