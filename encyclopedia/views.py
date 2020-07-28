from django import forms
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.urls import reverse
import markdown2
import random
from django.shortcuts import render
from . import util
from . import util


app_name = "encyclopedia"
last_random_page = ''

class SearchForm (forms.Form):
    searchbox = forms.CharField(label='', max_length=50, widget=forms.TextInput(
        attrs={'placeholder': "Search Encylopedia"}
    ))

class CreateEntry(forms.Form):
    title_bar = forms.CharField(label="Title", max_length=45, widget=forms.TextInput)
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

def create(request, bypass=False):
    searchbox = SearchForm()
    if request.method == 'GET':
        create_entry = CreateEntry()
        return render(request, 'encyclopedia/create.html', {
            "page_title": "Create Entry",
            "form": searchbox,
            "create_form": create_entry,
            "button_name": "Create",
            "action_url": ''
        })
    else:
        create_entry = CreateEntry(request.POST)
        if create_entry.is_valid():
            if not bypass:
                for entry in util.list_entries():
                    if entry.lower() == create_entry.cleaned_data["title_bar"].lower():
                        return render(request, 'encyclopedia/error.html', {
                            "error": "Error",
                            "message": f"{create_entry.cleaned_data['title_bar']} already exists in entries"
                        })
            print ("line 100 working"   )
            util.save_entry(
                create_entry.cleaned_data["title_bar"], 
                create_entry.cleaned_data["content_box"])
            return HttpResponseRedirect(f"/wiki/{create_entry.cleaned_data['title_bar']}")
 
def edit(request, name):

    if request.method == 'GET':
        edit_entry = CreateEntry(initial={"title_bar": name, "content_box": util.get_entry(name)})
        searchbox = SearchForm()
        return render(request, 'encyclopedia/create.html', {
            "page_title": f"Edit {name}",
            "create_form": edit_entry,
            "button_name": "Save",
            "form": searchbox   
        })
    else:
        return (create(request, True))

def random_page(request):
    global last_random_page
    if last_random_page == '':
        random_entry = random.choice(util.list_entries())
    else:
        corrected_list = util.list_entries()
        corrected_list.remove(last_random_page)
        random_entry = random.choice(corrected_list)
    last_random_page = random_entry
    return HttpResponseRedirect(f"/wiki/{random_entry}")

