from django.views import View
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from hypercar import settings


class WelcomeView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse('<h2>Welcome to the Hypercar Service!</h2>')


class MenuView(View):
    def get(self, request):
        return render(request, 'tickets/menu.html')


class ServiceManager(View):
    def get(self, request, service, *args, **kwargs):
        template_name = "tickets/tickets.html"
        line = settings.line_of_cars
        if not settings.ticket_number:
            settings.ticket_number = 1
            minutes_to_wait = 0
        else:
            settings.ticket_number += 1
            minutes_to_wait = 2 * len(line["change_oil"])
            if service == "inflate_tires" or service == "diagnostic":
                minutes_to_wait += 5 * len(line["inflate_tires"])
            if service == "diagnostic":
                minutes_to_wait += 30 * len(line["diagnostic"])
        line[service].append(settings.ticket_number)

        context = {
            "ticket_number": settings.ticket_number,
            "minutes_to_wait": minutes_to_wait,
        }
        return render(request, template_name, context)


class ProcessingView(View):
    def get(self, request, *args, **kwargs):
        template_name = "tickets/processing.html"
        context = {
            "change_oil": len(settings.line_of_cars["change_oil"]),
            "inflate_tires": len(settings.line_of_cars["inflate_tires"]),
            "diagnostic": len(settings.line_of_cars["diagnostic"])
        }
        return render(request, template_name, context=context)

    def post(self, request):
        processing_line = settings.line_of_cars
        if settings.ticket_number > 0:
            settings.ticket_number -= 1
        if len(processing_line["change_oil"]) > 0:
            settings.next = processing_line["change_oil"][0]
            processing_line["change_oil"] = processing_line["change_oil"][1:]
        elif len(processing_line["inflate_tires"]) > 0:
            settings.next = processing_line["inflate_tires"][0]
            processing_line["inflate_tires"] = processing_line["inflate_tires"][1:]
        elif len(processing_line["diagnostic"]) > 0:
            settings.next = processing_line["diagnostic"][0]
            processing_line["diagnostic"] = processing_line["diagnostic"][1:]
        return redirect('next')


class NextView(View):
    def get(self, request, *args, **kwargs):
        template_name = "tickets/next.html"
        if settings.next > 0:
            context = {
                'number': settings.next
            }
            return render(request, template_name, context=context)
        else:
            return render(request, template_name)
