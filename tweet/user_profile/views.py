from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse 

from .templates.forms.profile_change_form import ProfileChangeForm
from homepage.views import create_combined_post
from posts.models import Comment
from posts.models import Post
from posts.models import Quote    
from users.models import CustomUser
from user_profile.models import UserProfile


def create_combined_profile(request, profile, account):
    own_account_status = False
    is_following = False
    is_followed = False

    if request.user.get_username() == account.get_username():
        own_account_status = True
    else:
        requester_cu = get_object_or_404(CustomUser, email=request.user.get_username())
        requester = get_object_or_404(UserProfile, user_id=requester_cu.id)
        if profile.followers.contains(requester):
            is_following = True
        if profile.following.contains(requester):
            is_followed = True    

    user_profile_stripped = {
        "username": account.user_name,
        "id": profile.id,
        "bio": profile.bio,
        "followers": profile.getFollowers(),
        "following": profile.getFollowing(),
        "location": profile.location,
        "display_picture": profile.display_picture,
        "display_name": profile.display_name,
        "background": profile.background_picture,
        "own_account": own_account_status,
        "is_following": is_following,
        "is_followed": is_followed,
        "dob": account.date_of_birth,
        "doj": account.date_joined,
    }

    return user_profile_stripped

@login_required
def view_profile(request, profile_id):
    return redirect(reverse('profile:posts', args=(profile_id,)))

@login_required
def view_own_profile(request):
    requester_cu = get_object_or_404(CustomUser, email=request.user.get_username())
    user_profile = get_object_or_404(UserProfile, user_id=requester_cu.id)

    return redirect(reverse('profile:posts', args=(user_profile.id,)))

@login_required
def view_user_following(request, profile_id):
    user_profile = get_object_or_404(UserProfile, id=profile_id)
    following = user_profile.following.all()
    context = {"latest_following_list": following}
    return render(request, "view_friends.html", context)


@login_required
def view_user_followers(request, profile_id):
    user_profile = get_object_or_404(UserProfile, id=profile_id)
    followers = user_profile.followers.all()
    context = {"latest_followers_list": followers}
    return render(request, "view_friends.html", context)


@login_required
def view_user_posts(request, profile_id):
    user_profile  = get_object_or_404(UserProfile, id=profile_id)
    user_cu = get_object_or_404(CustomUser, id=user_profile.user_id)

    user_profile_stripped = create_combined_profile(request, user_profile, user_cu)

    latest_posts_list_raw = Post.objects.filter(poster_id=profile_id)
    latest_posts_list = create_combined_post(latest_posts_list_raw)

    context = {"latest_posts_list": latest_posts_list, "profile_data": user_profile_stripped,}
    return render(request, "posts.html", context)


@login_required
def view_user_quotes(request, profile_id):
    latest_quotes_list = Quote.objects.filter(poster_id=profile_id)
    context = {"latest_quotes_list": latest_quotes_list}
    return render(request, "posts.html", context)


@login_required
def view_user_comments(request, profile_id):
    user_profile  = get_object_or_404(UserProfile, id=profile_id)
    user_cu = get_object_or_404(CustomUser, id=user_profile.user_id)

    user_profile_stripped = create_combined_profile(request, user_profile, user_cu)

    latest_comments_list_raw = Comment.objects.filter(poster_id=profile_id)
    latest_comments_list = create_combined_post(latest_comments_list_raw)

    context = {"latest_posts_list": latest_comments_list, "profile_data": user_profile_stripped,}
    return render(request, "comments.html", context)


@login_required
def view_user_reposts(request, profile_id):
    latest_reposts_list = Post.objects.filter(reposts__id=profile_id)
    context = {"latest_reposts_list": latest_reposts_list}
    return render(request, "posts.html", context)


@login_required
def view_user_likes(request, profile_id):
    user_profile  = get_object_or_404(UserProfile, id=profile_id)
    user_cu = get_object_or_404(CustomUser, id=user_profile.user_id)

    user_profile_stripped = create_combined_profile(request, user_profile, user_cu)

    latest_likes_list_raw_p = Post.objects.filter(likes__id=profile_id)
    latest_likes_list_raw_q = Quote.objects.filter(likes__id=profile_id)
    latest_likes_list_raw_c = Comment.objects.filter(likes__id=profile_id)
    latest_likes_list = create_combined_post(latest_likes_list_raw_p) + create_combined_post(latest_likes_list_raw_q) + create_combined_post(latest_likes_list_raw_c)

    context = {"latest_posts_list": latest_likes_list, "profile_data": user_profile_stripped,}
    return render(request, "likes.html", context)

@login_required
def view_user_media(request, profile_id):
    user_profile  = get_object_or_404(UserProfile, id=profile_id)
    user_cu = get_object_or_404(CustomUser, id=user_profile.user_id)

    user_profile_stripped = create_combined_profile(request, user_profile, user_cu)

    latest_media_list=[]

    context = {"latest_posts_list": latest_media_list, "profile_data": user_profile_stripped,}
    return render(request, "media.html", context)


@login_required
def view_user_bookmarks(request):
    requester_cu = get_object_or_404(CustomUser, email=request.user.get_username())
    requester = get_object_or_404(UserProfile, user_id=requester_cu.id)

    latest_posts_raw = Post.objects.filter(bookmarks__id=requester.id)
    latest_posts = create_combined_post(latest_posts_raw)

    context = {"latest_posts_list": latest_posts, "username": requester_cu.user_name}
    return render(request, "bookmarks.html", context)


@login_required
def create_follow(request, profile_id):
    requester_cu = get_object_or_404(CustomUser, email=request.user.get_username())
    requester = get_object_or_404(UserProfile, user_id=requester_cu.id)
    profile_to_follow = get_object_or_404(UserProfile, user_id=profile_id)

    # make sure not trying to follow self
    if requester.id == profile_id:
        return HttpResponseRedirect(reverse("profile:home", args=(profile_id,)))
    else:
        requester.following.add(profile_to_follow)
        profile_to_follow.followers.add(requester)
        return HttpResponse()


@login_required
def delete_follow(request, profile_id):
    requester_cu = get_object_or_404(CustomUser, email=request.user.get_username())
    requester = get_object_or_404(UserProfile, user_id=requester_cu.id)
    profile_to_follow = get_object_or_404(UserProfile, user_id=profile_id)

    # make sure not trying to unfollow self
    if requester.id == profile_id:
        return HttpResponseRedirect(reverse('profile:home'), args=(profile_id,))
    else:
        requester.following.remove(profile_to_follow)
        profile_to_follow.followers.remove(requester)
        return HttpResponse()


@login_required
def remove_follow(request, profile_id):
    requester_cu = get_object_or_404(CustomUser, email=request.user.get_username())
    requester = get_object_or_404(UserProfile, user_id=requester_cu.id)
    profile_to_follow = get_object_or_404(UserProfile, user_id=profile_id)

    # make sure not trying to remove self as follower
    if requester.id == profile_id:
        return HttpResponseRedirect(reverse('profile:home'), args=(profile_id,))
    else:
        requester.following.remove(profile_to_follow)
        requester.followers.remove(profile_to_follow)
        profile_to_follow.following.remove(requester)
        profile_to_follow.followers.remove(requester)

        return HttpResponse()

@login_required
def view_messages(request):
    pass

@login_required
def view_notifications(request):
    requester_cu = get_object_or_404(CustomUser, email=request.user.get_username())
    requester = get_object_or_404(UserProfile, user_id=requester_cu.id)

    context = {"username": requester_cu.user_name}
    return render(request, "notifications.html", context)


@login_required
def edit_profile(request):
    if request.method == "POST":
        form = ProfileChangeForm(request.POST)

        if form.is_valid():
            poster_cu = get_object_or_404(CustomUser, email=request.user.get_username())
            poster = get_object_or_404(UserProfile, user_id=poster_cu.id)

            if form.cleaned_data['display_name'] != None:
                poster.display_name=form.cleaned_data['display_name']
            
            if form.cleaned_data['location'] != None:
                poster.location=form.cleaned_data['location']

            if form.cleaned_data['bio'] != None:
                poster.bio=form.cleaned_data['bio']
                
            if form.cleaned_data['date_of_birth'] != None:
                poster_cu.date_of_birth=form.cleaned_data['date_of_birth']

            poster.save()
            poster_cu.save()

        return HttpResponse(status=204)
    
    else:
        form = ProfileChangeForm()

    return render(request, "profile_edit.html", {"form": form})

# def view_user_dp(request, profile_id):
#     user = get_object_or_404(UserProfile, id=user_id)
#     return render(request, "display_picture.html", {"image": user.display_picture})


# def user_media(request, profile_id):
#     pass

    

