from django.contrib.auth import authenticate
from django.shortcuts import render, redirect
from django.contrib.auth.models import User,auth
from django.contrib import  messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Profile,Post,LikePost, FollowersCount
from itertools import chain
from django.db.models import Q
import random

# Create your views here.
@login_required(login_url='signin')
def index(request):
    user_object = User.objects.get(username=request.user)
    user_profile = Profile.objects.get(user=user_object)
    like_post= LikePost.objects.all()
    followings = []
    feeds = []
    liked = []
    suggestList =[]
    likedPost = []
    following = FollowersCount.objects.filter(follower=user_object)
    myLikes = LikePost.objects.filter(username=user_object)
    feedis =  Post.objects.filter(user=user_object)
    feeds.append(feedis)  
    
    
    
    for users in following:
    
        
        followings.append(users.user)
        
    for liker in myLikes:
        newLikePost = LikePost.objects.filter(post_id=liker.post_id)
        liked.append(liker.post_id)
        likedPost.append(newLikePost)
        
        
    for  usernames in followings:
        feed =  Post.objects.filter(user=usernames)
        #feed =  Post.objects.filter(Q(user=usernames) | Q(user=user_object))
        
        feeds.append(feed)
        
        
 
    followingPosts = list(chain(*feeds))
    myLyk = list(chain(*likedPost))
    
    #user suggestion starts
    all_users = User.objects.all()
    user_following_all =[]
    for user in following:
        suggestuser = User.objects.get(username=user.user)
        user_following_all.append(suggestuser)
        
    newSuggestList = [x for x in list(all_users) if (x not in list(user_following_all))]
    current_user =  User.objects.filter(username=request.user.username)
    final_suggestion  = [x for x in list(newSuggestList) if ( x not in list(current_user))]
    random.shuffle(final_suggestion)
    
    suggestionProfile =[]
    suggestProfileList = []
    
    for users in final_suggestion:
        suggestionProfile.append(users.id)
        
    for  ids in suggestionProfile:
        profList = Profile.objects.filter(id_user=ids)
        suggestProfileList.append(profList)
        
        
    suggestions = list(chain(*suggestProfileList))
    
    
    #user suggestion ends
    random.shuffle(feeds)
    
    
    
    profile_data = {
        'userObj':user_object,
        'profile':user_profile,
        'posts':feeds,
        'likes':liked,
        'allLikes':like_post,
        'myPosts':followingPosts,
        'follows':followings,
        'likedPosts':likedPost,
        'suggestions':suggestions[:5]
    }
    
    
    return render(request,'index.html',profile_data)



@login_required(login_url='signin')
def settings(request):
    user_profile = Profile.objects.get(user=request.user)
    profile_data = {
        'profile':user_profile
    }
    
    if request.method == "POST":
        
        if  request.FILES.get('image') == None:
            image = user_profile.profileimage
            bio = request.POST['bio']
            location = request.POST['location']
            
            user_profile.profileimage = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()
            
        if request.FILES.get('image') != None:
            image = request.FILES.get('image')
            bio = request.POST['bio']
            location = request.POST['bio']
            
            user_profile.profileimage = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()
            
        messages.info(request, "Account updated successfully")
        return redirect('settings')
    
    
    return render(request,'setting.html',profile_data)


@login_required(login_url='signin')
def upload(request):
    
    if request.method == "POST":
        user = request.user.username
        image = request.FILES.get('image_upload')
        caption = request.POST['caption']
        
        new_post = Post.objects.create(user=user, image=image,caption=caption)
        new_post.save()
        
        messages.info(request, "Your data has been posted successfully")
        return redirect('/') 
        
    else:
        return redirect('/') 
        
    #return HttpResponse("<h5>Upload View</h5>")

@login_required(login_url='signin')
def follow(request):
    if request.method == "POST":
        follower  = request.POST['follower']
        user  = request.POST['user']
        follow_filter = FollowersCount.objects.filter(follower=follower, user=user).first()
        
        if follow_filter:
            delete_follower = FollowersCount.objects.get(follower=follower, user=user)
            delete_follower.delete()
            if request.POST['url']:
                url = request.POST['url']
                return redirect(''+url)
            else:
                return redirect('/profile/'+user)
        
        else:
            new_follower = FollowersCount.objects.create(follower=follower, user=user)
            new_follower.save()
            if request.POST['url']:
                url = request.POST['url']
                return redirect(''+url)
            else:
                return redirect('/profile/'+user)
        
    
    else:
        return redirect('/')

@login_required(login_url='signin')
def search(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)
    
    following = FollowersCount.objects.filter(follower=user_object)
    followings =[]
    resultImages =[]
    followed = []
    results=[]
    
    for users in following:
    
        
        followings.append(users.user)
    
    

    
    
    profile_data = {
        'userObj':user_object,
        'profile':user_profile,
        'follows':followings,
        'resultImages':None
        
    }
    
    
    if request.method == "POST":
        search = request.POST['search']
        if search:
            result = User.objects.filter(Q(username__icontains=search) & Q(is_superuser=0) & Q(is_staff=0))
            
            profile_data['results'] = result
            
            for imageuser in result:
                
                resultImages.append(imageuser.id)
                
                
            for ids in resultImages:
                images = Profile.objects.filter(id_user=ids)
                results.append(images)
                
            profile_data['resultImages'] = list(chain(*results))
            
            
            return render(request,'search.html',profile_data)
        else:
            profile_data['results'] = ""
            return render(request,'search.html',profile_data) 
        
    else:
        profile_data['results'] = ""
        return render(request,'search.html',profile_data)


@login_required(login_url='signin')
def profile(request, pk):
    
    user_object = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user=user_object)
    posts = Post.objects.filter(user=pk)
    post_lent = len(posts)
    is_following = FollowersCount.objects.filter(follower=request.user.username, user=user_object).first()
    followers_count = FollowersCount.objects.filter(user=user_object)
    followers_lent = len(followers_count)
    following_count = FollowersCount.objects.filter(follower=user_object)
    following_lent = len(following_count)
    
    
    profile_data = {
        'profile':user_profile,
        'posts':posts,
        'userObj':user_object,
        'post_len':post_lent,
        'follow':is_following,
        'following_len':following_lent,
        'followers_len':followers_lent,
        'followers':followers_count,
        'following':following_count
    }
    
    return render(request,'profile.html',profile_data)


@login_required(login_url='signin')
def like_post(request):
    username = request.user.username
    post_id = request.GET.get('post_id')
    
    post = Post.objects.get(id=post_id)
    
    like_filter = LikePost.objects.filter(post_id=post_id, username=username).first()
    
    if like_filter == None:
        new_like = LikePost.objects.create(post_id=post_id, username=username)
        new_like.save()
        
        post.no_of_likes = post.no_of_likes+1
        post.save()
        
        return redirect('/')
    else:
        like_filter.delete()
        post.no_of_likes = post.no_of_likes-1
        post.save()
        return redirect('/')
    
        
    



def signup(request):
    
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        
        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, "Email is already in use")
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request, "Username is already in use")
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username, email=email,password=password)
                user.save()
                
                #log user in and redirect to settings page
                user_login = auth.authenticate(username=username, password=password)
                auth.login(request,user_login)
                
                #create a profile object for new user
                
                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
                new_profile.save()
                messages.info(request, "account created successfully")
                return redirect('settings')
                #return redirect('signup')
        else:
            messages.info(request, "Password did not match")
            return redirect('signup')
        
        
    else:
        return render(request,'signup.html')
    
    
def signin(request):
    
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        
        user = auth.authenticate(username=username, password=password)
        
        if user is not None:
            auth.login(request,user)
            return redirect('/')
            
        else:
            messages.info(request, "Invalid Credentials")
            return redirect('signin')
        
        
        
    else:
        return render(request,'signin.html')
    
    
@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('signin')


def pageError(request, exception):
    return render(request, '404.html', status=404)
    
