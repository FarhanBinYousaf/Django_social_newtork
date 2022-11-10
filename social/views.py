from django.shortcuts import render,redirect
from django.http import HttpResponseRedirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .models import Post,Comment, UserProfile,Notification
from .forms import PostForm, CommentForm
from django.views.generic.edit import UpdateView, DeleteView
from django.db.models import Q
from django.core.paginator import Paginator
# Create your views here

class PostListView(LoginRequiredMixin ,View):
    paginate_by = 2
    def get(self, request, *args, **kwargs):
        # On home page of logged_in user, if that logged_in user is following anyone user then posts created by that users will be shown there.
        # so, this below filter code is for that.
        logged_in_user = request.user
        posts = Post.objects.filter(
            # This code is for that purpose, only posts are created by followers are shown
            # author => is the author field in post table
            # profile => is the ralated_name in user in profile table
            # followers => is the related_name of followers in followers coloumn
            author__profile__followers__in=[logged_in_user.id]
            ).order_by('-created_on')
        
        # paginator = Paginator(posts,1)
        # page_number = request.GET.get('page')
        # PostsDataFinal = paginator.get_page(page_number)

        form = PostForm()
        context = {'posts_list':posts,'form':form}
        return render(request, 'social/posts_list.html',context)

    def post(self, request, *args, **kwargs):
        posts = Post.objects.all().order_by('-created_on')
        # paginator = Paginator(posts,1)
        # page_number = request.GET.get('page')
        # PostsDataFinal = paginator.get_page(page_number)

        form = PostForm(request.POST)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author = request.user
            new_post.save()

        

        context = {
        'posts_list':posts,
        'form':form,
        }
        return render(request, 'social/posts_list.html',context)


class PostDetailView(LoginRequiredMixin ,View):
    def get(self, request, pk, *args, **kwargs):
        post = Post.objects.get(pk=pk)
        form = CommentForm()
        comments = Comment.objects.filter(post=post).order_by('-created_on')
        context = {'post':post,'form':form,'comments':comments}
        return render(request, 'social/post_detail.html',context)

    def post(self, request, pk , *args, **kwargs):
        post = Post.objects.get(pk=pk)
        form = CommentForm(request.POST)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.author = request.user
            new_comment.post = post
            new_comment.save()
        notification = Notification.objects.create(notification_type=2,from_user=request.user,to_user=post.author,post=post)
        comments = Comment.objects.filter(post=post).order_by('-created_on')
        context = {'post':post,'form':form,'comments':comments}
        return render(request, 'social/post_detail.html',context)

class PostEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['body']
    template_name = 'social/post_edit.html'


# This below get_success_url() is the function which is the redirect url after post is edited. This name is the defualt name in django, we can't change this.
# Before this we have to import reverse_lazy() which redirects to the position.
# it takes self as peremeter, 
    def get_success_url(self):
        pk = self.kwargs['pk']   # Here, self.kwargs['pk'] is the primary key for post, 
        return reverse_lazy('post',kwargs={'pk':pk})     # redirect to post page with pk of specific.

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author
class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin,DeleteView):
    model = Post
    template_name = 'social/post_delete.html'
    success_url = reverse_lazy('post-list') 

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author
class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin,DeleteView):
    model = Comment
    template_name = 'social/comment_delete.html'

    def get_success_url(self):
        pk = self.kwargs['post_pk']  # this post_pk is the primary key for post which is on url page in specific view,since django does not support pk with same name on a same location that's why i used post_pk instead of pk for post , and pk for comment primary key
        # 
        return reverse_lazy('post',kwargs={'pk':pk})

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author

class UserProfileView(View):
    def get(self,request,pk, *args,**kwargs):
        follow = ""
        profile = UserProfile.objects.get(pk=pk)
        user = profile.user
        posts = Post.objects.filter(author=user).order_by('-created_on')

        followers = profile.followers.all()

        if len(followers) == 0:
            is_following = False

        for follower in followers:
            if follower == request.user:
                is_following = True
                break
            else:
                is_following = False

        number_of_followers = len(followers)

        context = {'profile':profile,'user':user,'posts':posts,'number_of_followers':number_of_followers,'is_following':is_following,'followers':followers,'follow':follow}

        return render(request,'social/user_profile.html',context)

class ProfileEditView(LoginRequiredMixin,UserPassesTestMixin,UpdateView):
    model = UserProfile
    fields = ['name','bio','birth_date','location','picture']
    template_name = 'social/edit_profile.html'

    def get_success_url(self):
        pk = self.kwargs['pk']
        return reverse_lazy('profile', kwargs={'pk': pk})


    def test_func(self):
        profile = self.get_object()
        return self.request.user == profile.user


class AddFollower(LoginRequiredMixin,View):
    def post(self,request,pk,*args,**kwargs):
        profile = UserProfile.objects.get(pk=pk)
        profile.followers.add(request.user)

        notification = Notification.objects.create(notification_type=3,from_user=request.user,to_user=profile.user)


        return redirect('profile',pk=profile.pk)
class RemoveFollower(LoginRequiredMixin,View):
    def post(self,request,pk,*args,**kwargs):
        profile = UserProfile.objects.get(pk=pk)
        profile.followers.remove(request.user)

        return redirect('profile', pk=profile.pk)

class FollowersList(View):
    def get(self,request,pk,*args,**kwargs):
        profile = UserProfile.objects.get(pk=pk)
        followers = profile.followers.all()

        context = {'profile':profile,'followers':followers}
        return render(request,'social/followers_list.html',context)
class AddLike(LoginRequiredMixin,View):
    def post(self,request,pk,*args,**kwargs):
        post = Post.objects.get(pk=pk)

        disliked = False
        for dislike in post.dislikes.all():
            if dislike == request.user:
                disliked = True
                break
        if disliked:
            post.dislikes.remove(request.user)


        liked = False
        for like in post.likes.all():
            if like == request.user:
                liked = True
                break

        if not liked:
            post.likes.add(request.user)
            notification = Notification.objects.create(notification_type=1,from_user=request.user,to_user=post.author,post=post)

        if liked:
            post.likes.remove(request.user)

        next = request.POST.get('next','/')
        return HttpResponseRedirect(next)
class AddDislike(LoginRequiredMixin,View):
    def post(self,request,pk,*args,**kwargs):
        post = Post.objects.get(pk=pk)


        liked = False
        for like in post.likes.all():
            if like == request.user:
                liked = True
                break
        if liked:
            post.likes.remove(request.user)

        disliked = False
        for dislike in post.dislikes.all():
            if dislike == request.user:
                disliked = True
                break

        if not disliked:
            post.dislikes.add(request.user)
        if disliked:
            post.dislikes.remove(request.user)

        next = request.POST.get('next','/')
        return HttpResponseRedirect(next)

class AddCommentLike(LoginRequiredMixin,View):
    def post(self,request,pk,*args,**kwargs):
        comment = Comment.objects.get(pk=pk)

        disliked = False
        for dislike in comment.dislikes.all():
            if dislike == request.user:
                disliked = True
                break
        if disliked:
            comment.dislikes.remove(request.user)


        liked = False
        for like in comment.likes.all():
            if like == request.user:
                liked = True
                break

        if not liked:
            comment.likes.add(request.user)

            notification = Notification.objects.create(notification_type=1,from_user=request.user,to_user=comment.author,comment=comment)

        if liked:
            comment.likes.remove(request.user)

        next = request.POST.get('next','/')
        return HttpResponseRedirect(next)
class AddCommentDislike(LoginRequiredMixin,View):
    def post(self,request,pk,*args,**kwargs):
        comment = Comment.objects.get(pk=pk)


        liked = False
        for like in comment.likes.all():
            if like == request.user:
                liked = True
                break
        if liked:
            comment.likes.remove(request.user)

        disliked = False
        for dislike in comment.dislikes.all():
            if dislike == request.user:
                disliked = True
                break

        if not disliked:
            comment.dislikes.add(request.user)
        if disliked:
            comment.dislikes.remove(request.user)

        next = request.POST.get('next','/')
        return HttpResponseRedirect(next)
class UserSearch(View):
    def get(self,request,*args,**kwargs):
        query = self.request.GET.get('query')
        profile_list = UserProfile.objects.filter(
            Q(user__username__icontains=query)
        )

        context = {'profile_list':profile_list,}
        return render(request,'social/search.html',context)

class CommentReplyView(LoginRequiredMixin,View):
    def post(self,request,post_pk,pk,*args,**kwargs):
        post = Post.objects.get(pk=post_pk)
        parent_comment = Comment.objects.get(pk=pk)
        form = CommentForm(request.POST)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.author=request.user
            new_comment.post = post
            new_comment.parent = parent_comment
            new_comment.save()

        notification = Notification.objects.create(notification_type=2,from_user=request.user,to_user=parent_comment.author,comment=new_comment)

        return redirect('post',pk=post_pk)


class PostNotification(View):
    def get(self,request,notification_pk,post_pk,*args,**kwargs):
        notification = Notification.objects.get(pk=notification_pk)
        post = Post.objects.get(pk=post_pk)

        notification.user_has_seen = True
        notification.save()

        return redirect('post',pk=post_pk)


class FollowNotification(View):
    def get(self,request,notification_pk,profile_pk,*args,**kwargs):
        notification = Notification.objects.get(pk=notification_pk)
        profile = UserProfile.objects.get(pk=profile_pk)

        notification.user_has_seen = True
        notification.save()

        return redirect('profile',pk=profile_pk)