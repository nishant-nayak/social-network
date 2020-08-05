import json

from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import redirect


from .models import User, Comment, Follower, Post
from .forms import NewPostForm

def reidx(request):
    return redirect('index', page=1)

def refollow(request):
    return redirect('following', page=1)

def reuser(request, name):
    return redirect('userpage', permanent=True, name=name, page=1)

def index(request, page):
    post_form = NewPostForm()
    all_posts = Post.objects.all().order_by('time').reverse()
    posts = [post.serialize(request) for post in all_posts]
    paginator = Paginator(posts, 10)

    page_obj = paginator.get_page(page)
    return render(request, "network/index.html", {
        'post_form': post_form,
        'page_obj': page_obj,
        'range': range(1, paginator.num_pages + 1)
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index", args=[1]))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index", args=[1]))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index", args=[1]))
    else:
        return render(request, "network/register.html")

@csrf_exempt
def newpost(request):
    if request.method != 'POST':
        return JsonResponse({'error': "POST request required."}, status=400)
    
    data = json.loads(request.body)
    text = data.get("text","")

    obj = Post(user=request.user, text=text)
    obj.save()
    result = Post.objects.filter(user=request.user, text=text).latest('time').serialize(request)

    return JsonResponse({
        "message": "New post posted successfully!",
        "result": result,
        "current_user": request.user.username
        }, status=201)

def userpage(request, name, page):
    user = User.objects.get(username=name)
    followers = Follower.objects.filter(following=user).count()
    following = Follower.objects.filter(user=user).count()
    all_posts = Post.objects.filter(user=user).order_by('time').reverse()
    posts = [post.serialize(request) for post in all_posts]
    paginator = Paginator(posts, 10)

    if request.user.is_authenticated:
        is_following = Follower.objects.filter(user=request.user, following=user).count()
    else:
        is_following = False
    
    page_obj = paginator.get_page(page)
    return render(request, 'network/userpage.html', {
        'name': name,
        'followers': followers,
        'following': following,
        'page_obj': page_obj,
        'is_following': is_following,
        'range': range(1, paginator.num_pages + 1)
    })

@csrf_exempt
def follow(request):
    if request.method != 'POST':
        return JsonResponse({'error':'Request method must be POST'}, status=400)
    
    data = json.loads(request.body)
    value = data.get("value","")
    username = data.get("username", "")
    user = User.objects.get(username=username)

    if value == "Follow":
        f = Follower(user=request.user, following=user)
        f.save()
    elif value == "Unfollow":
        try:
            Follower.objects.filter(user=request.user, following=user).delete()
        except:
            return JsonResponse({'error':'Follower record does not exist.'}, status=400)
    return JsonResponse({'message':'Record updated successfully.'}, status=201)


@login_required(login_url='login')
def following(request, page):
    following_users = Follower.objects.filter(user=request.user).values_list('following',flat=True)
    all_posts = Post.objects.filter(user__in=following_users).order_by('time').reverse()
    posts = [post.serialize(request) for post in all_posts]
    paginator = Paginator(posts, 10)

    page_obj = paginator.get_page(page)
    return render(request, 'network/following.html', {
        'page_obj': page_obj,
        'range': range(1, paginator.num_pages + 1)
    })

@csrf_exempt
def editpost(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Request method must be POST'}, status=400)
    
    data = json.loads(request.body)
    post_id = int(data.get("id"))
    post_text = data.get("text","")
    try:
        post = Post.objects.get(pk=post_id)
    except:
        return JsonResponse({'error': 'Invalid Post ID.'}, status=400)
    
    post.text = post_text
    post.save(update_fields=['time','text'])

    result = Post.objects.get(pk=post_id).serialize(request)

    return JsonResponse({
        'message': 'Post updated successfully!',
        'result': result,
        'current_user': request.user.username
        }, status=201)

@login_required(login_url='login')
@csrf_exempt
def likepost(request):
    if request.method != "POST":
        return JsonResponse({'error':'The request method must be POST.'}, status=400)
    
    data = json.loads(request.body)
    post_id = int(data.get("id"))
    try:
        post = Post.objects.get(pk=post_id)
    except:
        return JsonResponse({'error': 'Invalid Post ID.'}, status=400)
    
    user = request.user
    if post.likes.filter(username=user.username).exists():
        post.likes.remove(user)
    else:
        post.likes.add(user)
        
    result = Post.objects.get(pk=post_id).serialize(request)

    return JsonResponse({
        'result': result
    }, status=201)