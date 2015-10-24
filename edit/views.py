__author__ = 'jblowe'

import os

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, render_to_response
from django import forms

from cspace_django_site.main import cspace_django_site

config = cspace_django_site.getConfig()
TITLE = 'Edit'

from utils import loginfo, doEdit, getEntityList, setConstants


@login_required()
def index(request):
    context = setConstants({'entity' : 'listentities', 'entitytypes' : getEntityList()})
    return render(request, 'edit.html', context)


@login_required()
def edit(request, entity, csid):

    context = {}
    if request.method == 'GET':
        requestObject = request.GET
        form = forms.Form(requestObject)

        if form.is_valid():
            context['entity'] = entity
            context['csid'] = csid
            loginfo(entity, context, request)
            context = doEdit(request,context)
    else:
        pass

    context = setConstants(context)
    loginfo(entity, context, request)
    return render(request, 'edit.html', context)
