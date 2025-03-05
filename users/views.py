from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Sum
from django.urls import reverse
from django.contrib.auth.hashers import make_password
from .forms import CustomUserCreationForm, ProfileUpdateForm, CreateAgentForm, SendTokensForm
from .models import CustomUser, UserProfile, Notification
from tokens.models import TokenRate
from transactions.models import Transaction
from django.contrib.auth import authenticate, login, logout
from community.models import Tweet  
from .utils import BadgeManager


@login_required
def dashboard(request):
    user = request.user
    context = {}
    
    try:
        profile = user.userprofile
    except UserProfile.DoesNotExist:
        # Create profile if it doesn't exist
        profile = UserProfile.objects.create(user=user)
        profile.profile_picture.save(
            f'{user.username}_profile.png',
            create_default_profile_picture(user.username)
        )
        profile.save()

    # Get current exchange rate
    current_rate = TokenRate.objects.last().rate if TokenRate.objects.exists() else 3800

    if user.is_superuser:
        # Superuser dashboard
        context.update({
            'total_users': CustomUser.objects.count(),
            'total_agents': CustomUser.objects.filter(is_agent=True).count(),
            'total_tokens': UserProfile.objects.aggregate(
                total=Sum('token_balance')
            )['total'] or 0,
            'recent_transactions': Transaction.objects.all()[:10],
            'send_tokens_url': reverse('users:send_tokens'),
            'current_rate': current_rate,
        })
    else:
        # Regular user/agent dashboard
        context.update({
            'profile': user.userprofile,
            'transactions': Transaction.objects.filter(user=user).order_by('-timestamp')[:5],  # Fetch user's transactions
            'token_balance': user.userprofile.token_balance,
            'ugx_balance': user.userprofile.get_ugx_balance(),  # Use dynamic UGX balance
            'request_withdrawal_url': reverse('transactions:request_withdrawal'),  # Updated URL
            'current_rate': current_rate,
        })
        
        if user.is_agent:
            context.update({
                'pending_withdrawals': Transaction.objects.filter(
                    agent=user, 
                    status='pending',
                    transaction_type='withdrawal'
                ),
                'process_withdrawal_url': reverse('transactions:process_withdrawal'),  # Updated URL
            })

    return render(request, 'users/dashboard.html', context)



@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.userprofile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('users:user_profile', username=request.user.username)
    else:
        form = ProfileUpdateForm(instance=request.user.userprofile)
    
    # Fetch the user's tweets
    tweets = Tweet.objects.filter(user=request.user).order_by('-created_at')
    
    return render(request, 'users/edit_profile.html', {
        'form': form,
        'tweets': tweets  # Pass tweets to the template
    })



def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')  # Redirect to home page after registration
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'users/login.html', {'error': 'Invalid credentials'})
    return render(request, 'users/login.html')

@login_required
def create_agent(request):
    if not request.user.is_superuser:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = CreateAgentForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            
            user = CustomUser.objects.create(
                email=email,
                password=make_password(password),
                is_agent=True
            )
            UserProfile.objects.create(user=user)
            messages.success(request, f"Agent {email} created successfully")
            return redirect('dashboard')
    else:
        form = CreateAgentForm()
    
    return render(request, 'users/create_agent.html', {'form': form})


@login_required
def admin_balances(request):
    if not request.user.is_superuser:
        return redirect('dashboard')
    
    # System-wide balances
    total_tokens = UserProfile.objects.aggregate(Sum('token_balance'))['token_balance__sum'] or 0
    token_rate = TokenRate.objects.last()
    total_ugx = total_tokens * token_rate.rate if token_rate else 0
    
    # User statistics
    user_count = CustomUser.objects.count()
    agent_count = CustomUser.objects.filter(is_agent=True).count()
    
    # Transaction ledger
    transactions = Transaction.objects.all().order_by('-timestamp')[:50]
    
    # Badge management
    users = CustomUser.objects.all().prefetch_related('userprofile')
    for user in users:
        user.recommended_badge = BadgeManager.calculate_badge(user.userprofile)

    context = {
        'total_tokens': total_tokens,
        'total_ugx': total_ugx,
        'current_rate': token_rate.rate if token_rate else None,
        'user_count': user_count,
        'agent_count': agent_count,
        'transactions': transactions,
        'users': users,
        'badge_choices': UserProfile.BADGE_CHOICES,
    }
    return render(request, 'users/admin_balances.html', context)
    
    

@login_required
def assign_badge(request):
    if not request.user.is_superuser:
        return redirect('dashboard')
    
    if request.method == 'POST':
        badge = request.POST.get('badge')
        users = request.POST.getlist('users')
        
        if not users:
            messages.error(request, "No users selected")
            return redirect('users:admin_balances')
        
        count = 0
        for username in users:
            try:
                user = CustomUser.objects.get(username=username)
                profile = user.userprofile
                profile.badge = badge
                profile.save()
                count += 1
            except CustomUser.DoesNotExist:
                continue
        
        messages.success(request, f"Assigned {badge} badge to {count} users")
        return redirect('users:admin_balances')
    
    return redirect('users:admin_balances')

# users/views.py
@login_required
def send_tokens(request):
    if not request.user.is_superuser:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = SendTokensForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            amount = form.cleaned_data['amount']
            
            try:
                user = CustomUser.objects.get(username=username)
                profile = user.userprofile
                profile.token_balance += amount
                profile.save()
                
                # Create transaction record
                transaction = Transaction.objects.create(
                    user=user,
                    agent=request.user,
                    amount=amount,
                    transaction_type='deposit'
                )
                
                # Create notifications
                Notification.objects.create(
                    user=user,
                    message=f"You received {amount} tokens from {request.user.username}.",
                    transaction=transaction
                )
                Notification.objects.create(
                    user=request.user,
                    message=f"You sent {amount} tokens to {user.username}.",
                    transaction=transaction
                )
                
                messages.success(request, f"Sent {amount} tokens to {username}")
                return redirect('transactions:transaction_receipt', pk=transaction.id)  # Redirect to receipt
            except CustomUser.DoesNotExist:
                messages.error(request, "User not found")
    else:
        form = SendTokensForm()
    
    return render(request, 'users/send_tokens.html', {'form': form})

@login_required
def transaction_receipt(request, tx_id):
    transaction = get_object_or_404(Transaction, id=tx_id, user=request.user)
    return render(request, 'users/receipt.html', {'transaction': transaction})

def user_logout(request):
    logout(request)
    return redirect('home')
    
# users/views.py
@login_required
def notifications(request):
    all_notifications = request.user.notifications.order_by('-created_at')
    return render(request, 'users/notifications.html', {
        'notifications': all_notifications
    })

@login_required
def delete_notification(request, notification_id):
    notification = get_object_or_404(
        Notification, 
        id=notification_id,
        user=request.user
    )
    notification.delete()
    messages.success(request, "Notification deleted successfully")
    return redirect('users:notifications')

@login_required
def mark_notification_as_read(request, notification_id):
    notification = get_object_or_404(
        Notification, 
        id=notification_id,
        user=request.user
    )
    notification.is_read = True
    notification.save()
    messages.success(request, "Notification marked as read")
    return redirect('users:notifications')
    
# For likes

# For follow
@login_required
@require_POST
def follow_user(request, username):
    user_to_follow = get_object_or_404(CustomUser, username=username)
    profile = user_to_follow.userprofile
    current_profile = request.user.userprofile
    
    if request.user != user_to_follow:
        if profile in current_profile.following.all():
            current_profile.following.remove(profile)
            is_following = False
        else:
            current_profile.following.add(profile)
            is_following = True
            
        return JsonResponse({
            'status': 'success',
            'is_following': is_following,
            'follower_count': profile.followers.count()
        })
    
    return JsonResponse({'status': 'error'}, status=400)
  
  
    


@login_required
@require_POST
def unfollow_user(request, username):
    user_to_unfollow = get_object_or_404(CustomUser, username=username)
    profile = user_to_unfollow.userprofile
    current_profile = request.user.userprofile
    
    if request.user != user_to_unfollow:
        current_profile.following.remove(profile)
        return JsonResponse({
            'status': 'success',
            'is_following': False,
            'follower_count': profile.followers.count(),
            'message': f'You have unfollowed {username}'
        })
    return JsonResponse({'status': 'error', 'message': 'Cannot unfollow yourself'})


    
def user_profile(request, username):
    user = get_object_or_404(CustomUser, username=username)
    is_owner = (request.user == user)
    
    is_following = False
    if request.user.is_authenticated:
        is_following = user.userprofile.followers.filter(id=request.user.userprofile.id).exists()
    
    context = {
        'profile_user': user,
        'tweets': Tweet.objects.filter(user=user),
        'is_owner': is_owner,
        'is_following': is_following,
    }
    return render(request, 'users/profile.html', context)
