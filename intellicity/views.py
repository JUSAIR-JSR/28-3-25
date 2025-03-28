from django.shortcuts import render

# Create your views here.
def index_dashboard(request):
    return render(request,'blank_layout.html')