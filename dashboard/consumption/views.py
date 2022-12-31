# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import models
from django.db.models.functions import TruncDate
from django.shortcuts import render, get_object_or_404

from consumption.models import ConsumptionData, UserData


def summary(request):
    context = {
        'users': all_users(),
        'aggregate_consumption': aggregate_consumption()
    }
    return render(request, 'consumption/summary.html', context)


def aggregate_consumption():
    qs = ConsumptionData.objects.all()
    qs = qs.annotate(date=TruncDate("datetime"))
    qs = qs.order_by("date")
    qs = qs.values("date")
    return qs.annotate(
        total=models.Sum("consumption"),
        average=models.Avg("consumption")
    )


def all_users():
    return UserData.objects.all().annotate(
        total=models.Sum("consumptiondata__consumption"),
        average=models.Avg("consumptiondata__consumption")
    )


def detail(request, user_id):
    user = get_object_or_404(UserData, pk=user_id)
    date_list = user.consumptiondata_set.all() \
        .annotate(date=TruncDate("datetime")) \
        .values_list("date", flat=True) \
        .order_by("-date") \
        .distinct()
    date_list = [str(d) for d in date_list]
    current_date = request.GET.get('current_date', date_list[0])

    date_nation(date_list, current_date)

    user_consumption = user.consumptiondata_set.filter(datetime__date=current_date).order_by("datetime")

    context = {
        "user": user,
        "consumption_list": user_consumption,
        'date_list': date_list,
        'current_date': current_date
    }
    return render(request, 'consumption/detail.html', context)


def date_nation(date_list, current_date, ):
    date_index = date_list.index(current_date)
    if len(date_list) < date_index:
        pass
    print(date_list)
    print(date_index)


def detail_(request, user_id):
    user = get_object_or_404(UserData, pk=user_id)
    user_consumption = user.consumptiondata_set.all().order_by("datetime").reverse()

    paginator = Paginator(user_consumption, 48)
    page_number = request.GET.get('page', 1)

    try:
        pages = paginator.page(page_number)
    except PageNotAnInteger:
        pages = paginator.page(1)
    except EmptyPage:
        pages = paginator.page(1)

    context = {
        "user": user,
        "consumption_list": pages.object_list,
        "pages": pages,
        'paginator': paginator,
        'page_obj': pages,
        'is_paginated': pages.has_other_pages(),
        'object_list': pages.object_list
    }
    return render(request, 'consumption/detail.html', context)
