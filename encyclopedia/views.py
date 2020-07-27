from django import forms
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.urls import reverse
import markdown2
from django.shortcuts import render
from . import util
from . import util


app_name = "encyclopedia"


class SearchForm (forms.Form):
    searchbox = forms.CharField(label='', max_length=50, widget=forms.TextInput(
        attrs={'placeholder': "Search Encylopedia"}
    ))

class CreateEntry(forms.Form):
    title_bar = forms.CharField(label="Title", max_length=45)
    content_box = forms.CharField(label="Description", widget=forms.Textarea)

def index(request):
    entries = util.list_entries()
    return render(request, "encyclopedia/index.html", {
        "entries": entries,
        "form": SearchForm()
    })


def display_entries(request, name):
    
    # checks if page exists
    content = None
    for entry in util.list_entries():
        if name.lower() == entry.lower():
            content = util.get_entry(entry)
            title = entry
            break
    
    searchbox = SearchForm()
    # if page is not found
    if content == None:
        return render(request, "encyclopedia/error.html", {
            "error": 'Error 404: Page not Found',
            "message": f"The Entry ({name}) you are looking for was not found!"
        })
    else: 
        return render(request, "encyclopedia/titles.html", {
            # convert string to html (\n to <br> etc.)
            "content": markdown2.markdown(content),
            "title_name": title,
            "form": searchbox
        })

def search_entries(request):
    searchbox = SearchForm(request.POST)
    entries = []
    if searchbox.is_valid():
        query = query = searchbox.cleaned_data["searchbox"].lower()
        for entry in util.list_entries():
            if query == entry.lower():
                matched_entry = entry
                entries = []
                return HttpResponseRedirect(f"/wiki/{query}")
            elif query in entry.lower():
                entries.append(entry)
        head_message = 'No entries match your Query!'
        if len(entries) > 0:
            head_message = "These entries partially match your Query:-"
        return (render(request, "encyclopedia/search.html", {
            "form": searchbox,
            "entries": entries,
            "message": head_message
    }))

def create(request):
    searchbox = SearchForm()
    if request.method == 'GET':
        create_entry = CreateEntry()
        return render(request, 'encyclopedia/create.html', {
            "form": searchbox,
            "create_form": create_entry
        })
    else:
        create_entry = CreateEntry(request.POST)
        if create_entry.is_valid():
            for entry in util.list_entries():
                if entry.lower() == create_entry.cleaned_data["title_bar"].lower():
                    return render(request, 'encyclopedia/error.html', {
                        "error": "Error",
                        "message": f"{create_entry.cleaned_data['title_bar']} already exists in entries"
                    })
            util.save_entry(
                create_entry.cleaned_data["title_bar"], 
                create_entry.cleaned_data["content_box"])
            return HttpResponseRedirect(f"/wiki/{create_entry.cleaned_data['title_bar']}")
 