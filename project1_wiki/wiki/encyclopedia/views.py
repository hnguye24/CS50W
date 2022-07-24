from nis import match
from queue import Empty
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib import messages
from . import util
from . import forms


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def wiki(request, title):
    entry = util.get_entry(title)
    if entry is None:
        return render(request, "encyclopedia/error.html", {
            "error_title": "Page Not Found",
            "error_message": f"Sorry, \"{title}\" page does not exist."
        })
    
    return render(request, "encyclopedia/wiki.html", {
        "title": title.capitalize(),
        "entry": entry
    })


def search(request):
    if request.method == "POST":
        search = request.POST['q']
        entry = util.get_entry(search)
        if entry is None:
            # show list of available pages that contains the substring
            matched_entries = []
            entries = util.list_entries()
            for entry in entries:
                if search.lower() in entry.lower():
                    matched_entries.append(entry)
            if len(matched_entries) != 0:
                return render(request, "encyclopedia/search_results.html", {
                    "entries": matched_entries
                })
            else: # show no pages found
                return render(request, "encyclopedia/error.html", {
                    "error_title": "No Pages Found Based on Search",
                    "error_message": f"Sorry, no pages were found that matched with \"{search}\"."
                })
        else: # if page is found, redirect to page
            return HttpResponseRedirect(f'/wiki/{search}')


def create(request):
    form = forms.create_page_form()
    if request.method == "POST":
        form = forms.create_page_form(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            # if page doesn't exist add to disk and redirect to page, else show error page
            if util.get_entry(title) is None:
                util.save_entry(title, content)
                return HttpResponseRedirect(f'/wiki/{title}')
            else:
                # return original form values with error message
                messages.error(request, f"\"{title.capitalize()}\" page already exist. Use a different title.")
                return render(request, "encyclopedia/create.html", {
                    "form": form   
                })
    else:
        return render(request, "encyclopedia/create.html", {
            "form": form   
        })