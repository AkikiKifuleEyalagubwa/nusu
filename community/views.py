from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Tweet,Media,Hashtag
from .forms import TweetForm
from django.views.decorators.http import require_POST
from users.models import Notification
from django.db.models import Max
from django.db.models import Q
from django.utils import timezone
from users.models import CustomUser
from django.db.models import Count, F


    

def feed(request):
    # Get trending hashtags (last 24 hours)
    trending_hashtags = Hashtag.objects.filter(
        last_activity__gte=timezone.now() - timezone.timedelta(hours=24)
    ).annotate(
        calculated_score=Count('related_tweets') + F('trend_score')  # Unique name
    ).order_by('-calculated_score')[:10]

    # Get tweets for the feed
    tweets = Tweet.objects.filter(
        parent=None,
        parent_tweet=None
    ).order_by('-created_at')

    return render(request, 'community/feed.html', {
        'tweets': tweets,
        'trending_hashtags': trending_hashtags
    })


@login_required
def tweet_detail(request, tweet_id):
    tweet = get_object_or_404(Tweet, id=tweet_id)
    if request.method == 'POST':
        form = TweetForm(request.POST, request.FILES)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.user = request.user
            reply.parent = tweet
            reply.save()
            return redirect('community:tweet_detail', tweet_id=tweet_id)
    else:
        form = TweetForm()
    
    replies = tweet.get_replies().order_by('-created_at')
    return render(request, 'community/tweet_detail.html', {
        'tweet': tweet,
        'replies': replies,
        'form': form
    })




    
@login_required
def create_tweet(request, tweet_id=None):
    parent_tweet = get_object_or_404(Tweet, id=tweet_id) if tweet_id else None
    is_thread = request.GET.get('thread', False)

    if request.method == 'POST':
        form = TweetForm(request.POST, request.FILES)
        if form.is_valid():
            tweet = form.save(commit=False)
            tweet.user = request.user
            
            if is_thread:
                # Get root tweet
                if parent_tweet:
                    root = parent_tweet.parent_tweet or parent_tweet
                    # Check if user is the thread author
                    if root.user != request.user:
                        return JsonResponse(
                            {"status": "error", "message": "Only the thread author can add to this thread."},
                            status=403
                        )
                    tweet.thread_position = root.thread.count() + 1
                else:
                    tweet.thread_position = 1
                    tweet.is_thread = True
                
                tweet.parent_tweet = root if parent_tweet else None

            tweet.save()
            for file in request.FILES.getlist('media'):
                Media.objects.create(
                    tweet=tweet,
                    file=file,
                    media_type='image' if file.content_type.startswith('image') else 'video'
                )

            if parent_tweet:
                return redirect('community:thread_detail', tweet_id=parent_tweet.id)
            return redirect('community:feed')
        else:
            # Return form with errors
            return render(request, 'community/compose.html', {
                'form': form,
                'parent_tweet': parent_tweet,
                'is_thread': is_thread
            })
    else:
        form = TweetForm()

    # Ensure we always return a response
    return render(request, 'community/compose.html', {
        'form': form,
        'parent_tweet': parent_tweet,
        'is_thread': is_thread
    })


def thread_detail(request, tweet_id):
    try:
        main_tweet = get_object_or_404(Tweet, id=tweet_id)
        
        # Get root tweet of the thread
        root_tweet = main_tweet.parent_tweet if main_tweet.parent_tweet else main_tweet
        
        # Get all tweets in the thread including root and replies
        thread_tweets = Tweet.objects.filter(
            Q(id=root_tweet.id) | 
            Q(parent_tweet=root_tweet)
        ).order_by('thread_position')

        return render(request, 'community/thread_detail.html', {
            'thread_tweets': thread_tweets,
            'root_tweet': root_tweet,
            'form': TweetForm()
        })
    
    except Exception as e:
        return HttpResponse(f"Error loading thread: {str(e)}", status=500)


@login_required
@require_POST
def retweet_tweet(request, tweet_id):
    original_tweet = get_object_or_404(Tweet, id=tweet_id)
    
    # Check if user already retweeted
    existing_retweet = Tweet.objects.filter(
        user=request.user, 
        retweet=original_tweet
    ).first()
    
    if existing_retweet:
        existing_retweet.delete()
        retweeted = False
    else:
        new_retweet = Tweet.objects.create(
            user=request.user,
            retweet=original_tweet
        )
        retweeted = True
        
        # Create notification
        Notification.objects.create(
            user=original_tweet.user,
            message=f"{request.user.username} retweeted your post"
        )
    
    return JsonResponse({
        'status': 'success',
        'retweeted': retweeted,
        'retweet_count': original_tweet.retweets.count(),
        'message': 'Retweet successful' if retweeted else 'Retweet removed'
    })



@login_required
@require_POST
def delete_tweet(request, tweet_id):
    tweet = get_object_or_404(Tweet, id=tweet_id)
    
    if request.user != tweet.user and not request.user.is_superuser:
        return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)
    
    tweet.delete()
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'message': 'Tweet deleted'})
    
    return redirect('community:feed')

@login_required
@require_POST
def undo_retweet(request, tweet_id):
    try:
        original_tweet = Tweet.objects.get(id=tweet_id)
        retweet = Tweet.objects.get(
            user=request.user,
            retweet=original_tweet
        )
        retweet.delete()
        return JsonResponse({
            'status': 'success',
            'retweet_count': original_tweet.retweet_count(),
            'message': 'Retweet removed successfully.'
        })
    except Tweet.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Retweet not found.'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


    
    
  

@login_required
@require_POST
def toggle_like(request, tweet_id):
    tweet = get_object_or_404(Tweet, id=tweet_id)
    if request.user in tweet.likes.all():
        tweet.likes.remove(request.user)
        liked = False
        # Remove like notification
        Notification.objects.filter(
            user=tweet.user,
            message=f"{request.user.username} unliked your tweet."
        ).delete()
    else:
        tweet.likes.add(request.user)
        liked = True
        # Add like notification
        Notification.objects.create(
            user=tweet.user,
            message=f"{request.user.username} liked your tweet."
        )
    return JsonResponse({
        'success': True,
        'liked': liked,
        'like_count': tweet.likes.count(),
        'message':f"{request.user.username} liked your tweet",
    })



@login_required
def reply_tweet(request, tweet_id):
    parent_tweet = get_object_or_404(Tweet, id=tweet_id)
    
    if request.method == 'POST':
        form = TweetForm(request.POST, request.FILES)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.user = request.user
            reply.parent = parent_tweet
            reply.save()
            
            # Handle media files
            for file in request.FILES.getlist('media'):
                Media.objects.create(
                    tweet=reply,
                    file=file,
                    media_type='image' if file.content_type.startswith('image') else 'video'
                )
            
            Notification.objects.create(
                user=parent_tweet.user,
                message=f"{request.user.username} replied to your tweet."
            )
            return redirect('community:tweet_detail', tweet_id=parent_tweet.id)
    
    form = TweetForm()
    return render(request, 'community/compose.html', {
        'parent_tweet': parent_tweet,
        'form': form
    })


@login_required
def quote_retweet(request, tweet_id):
    original_tweet = get_object_or_404(Tweet, id=tweet_id)
    
    if request.method == 'POST':
        form = TweetForm(request.POST, request.FILES)
        if form.is_valid():
            quote_tweet = form.save(commit=False)
            quote_tweet.user = request.user
            quote_tweet.quote = original_tweet  # Use quote field instead of retweet
            quote_tweet.save()
            
            # Handle media files
            for file in request.FILES.getlist('media'):
                Media.objects.create(
                    tweet=quote_tweet,
                    file=file,
                    media_type='image' if file.content_type.startswith('image') else 'video'
                )
            
            Notification.objects.create(
                user=original_tweet.user,
                message=f"{request.user.username} quoted your tweet."
            )
            return redirect('community:tweet_detail', tweet_id=quote_tweet.id)
    
    form = TweetForm()
    return render(request, 'community/quote_retweet.html', {
        'original_tweet': original_tweet,
        'form': form
    })

def search_autocomplete(request):
    query = request.GET.get('q', '').strip()
    context = {'users': [], 'hashtags': []}
    
    if query:
        # User search
        if query.startswith('@'):
            username = query[1:]
            context['users'] = CustomUser.objects.filter(
                Q(username__icontains=username) |
                Q(first_name__icontains=username)
            )[:5]

        # Hashtag search
        elif query.startswith('#'):
            tag_name = query[1:]
            context['hashtags'] = Hashtag.objects.filter(name__icontains=tag_name)[:5]

        # General search
        else:
            context['users'] = CustomUser.objects.filter(
                Q(username__icontains=query) |
                Q(first_name__icontains=query)
            )[:3]
            context['hashtags'] = Hashtag.objects.filter(name__icontains=query)[:3]

    return render(request, 'community/autocomplete_results.html', context)



def search_results(request):
    query = request.GET.get('q', '')
    context = {'query': query}
    
    if query.startswith('@'):
        username = query[1:]
        context['users'] = CustomUser.objects.filter(
            Q(username__icontains=username) |
            Q(first_name__icontains=username) |
            Q(last_name__icontains=username)
        )
    elif query.startswith('#'):
        tag_name = query[1:].lower()
        try:
            hashtag = Hashtag.objects.get(name=tag_name)
            context['tweets'] = hashtag.related_tweets.all().order_by('-created_at')
            context['hashtag'] = hashtag
        except Hashtag.DoesNotExist:
            context['tweets'] = []
    elif query.startswith('$'):
        context['stocks'] = []
    else:
        context['users'] = CustomUser.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )[:10]
        context['hashtags'] = Hashtag.objects.filter(name__icontains=query)[:10]
    
    return render(request, 'community/search_results.html', context)

def trending(request):
    # Get trending hashtags (last 24 hours)
    trending_hashtags = Hashtag.objects.filter(
        last_activity__gte=timezone.now() - timezone.timedelta(hours=24)
    ).annotate(
        calculated_score=Count('related_tweets') + F('trend_score')  # Unique name
    ).order_by('-calculated_score')[:20]

    return render(request, 'community/trending.html', {
        'trending_hashtags': trending_hashtags
    })