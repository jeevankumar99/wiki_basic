from django import forms
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.urls import reverse
import markdown2
import random
from django.shortcuts import render
import textwrap
from . import util
from . import util


app_name = "encyclopedia"
last_random_page = ''

class SearchForm (forms.Form):
    searchbox = forms.CharField(label='', max_length=50, widget=forms.TextInput(
        attrs={'placeholder': "Search Encylopedia", 'autocomplete': "off"}
    ))

class CreateEntry(forms.Form):
    title_bar = forms.CharField(max_length=45, widget=forms.TextInput(
        attrs={'autocomplete': "off"}
    ))
    content_box = forms.CharField(widget=forms.Textarea)

def index(request):
    """ 
    Renders the index page
    """
    entries = util.list_entries()
    return render(request, "encyclopedia/index.html", {
        "entries": entries,
        "form": SearchForm()
    })


def display_entries(request, name):
    """ 
    Renders the entry page requested by the uesr if it exists,
    else redirects to an error page
    """
    content = util.get_entry(name)    
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
            "content": markdown2.markdown(content[1]    ),
            "title_name": content[0],
            "form": searchbox
        })

def search_entries(request):
    """ 
    Searchs if entry matches the query and redirects the user
    to that page if it exists. If the exact entry doesn't exist, 
    displays a list of all partially matching entries.
    """
    searchbox = SearchForm(request.POST)
    # to store entries
    entries = []

    # if the data entered by user is valid
    if searchbox.is_valid():
        query = query = searchbox.cleaned_data["searchbox"].lower()
        
        # can't use get_entries in case of partial search query
        for entry in util.list_entries():
            if query == entry.lower():
                matched_entry = entry
                return HttpResponseRedirect(f"/wiki/{query}")
            # if query partially matches an entry
            elif query in entry.lower():
                entries.append(entry)
        
        # if no entries mathed the query
        head_message = 'No entries match your Query!'
        if len(entries) > 0:
            head_message = "These entries partially match your Query:-"
        
        return (render(request, "encyclopedia/search.html", {
            "form": searchbox,
            "entries": entries,
            "message": head_message
    }))

def create_entries(request, bypass=False):
    """
    Renders the CREATE page, verifies the data and saves the entry.
    Redirects the user to the created entry page if saved,
    else if it already exists redirects to the error page
    """
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
            # bypass is used by edit_entries function to ignore if entry already exists
            if not bypass:
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
 
def edit_entries(request, name):
    """
    Edits existing entries, uses createa_entries function 
    for rendering the page.
    """
    if request.method == 'GET':
        edit_entry = CreateEntry(initial={"title_bar": name, "content_box": util.get_entry(name)[1]})
        searchbox = SearchForm()
        return render(request, 'encyclopedia/create.html', {
            "page_title": f"Edit {name}",
            "create_form": edit_entry,
            "button_name": "Save",
            "form": searchbox   
        })
    else:
        # passes bypass=True to ignore if entry already exists
        return (create_entries(request, True))

def random_page(request):
    """
    Redirects the user to a page containg a random entry 
    from the existing entries.
    """
    # To exclude the previously generated entry
    global last_random_page
    # If random_page is being used for the first time
    if last_random_page == '':
        random_entry = random.choice(util.list_entries())
    else:
        corrected_list = util.list_entries()
        corrected_list.remove(last_random_page)
        random_entry = random.choice(corrected_list)
    #stores currently generated page to exclude it next time
    last_random_page = random_entry
    return HttpResponseRedirect(f"/wiki/{random_entry}")
