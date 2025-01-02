from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Post, Comment,Profile
from .forms import CommentForm, PostForm, RegistrationForm



@login_required
def profile(request):
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        # Create profile if it doesn't exist
        profile = Profile.objects.create(user=request.user)

    if request.method == 'POST':
        # Handle profile update
        if 'bio' in request.POST:
            profile.bio = request.POST['bio']
        
        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']

        profile.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')

    return render(request, 'social/profile.html', {'profile': profile})

@login_required
def edit_post(request, post_id):
    # Get the post by its ID
    post = get_object_or_404(Post, id=post_id, user=request.user)
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()  # Save the updated post
            return redirect('home')  # Redirect to the home page after editing
    else:
        form = PostForm(instance=post)  # Pre-fill the form with the existing post data

    return render(request, 'social/edit_post.html', {'form': form, 'post': post})

@login_required
def delete_post(request, post_id):
    # Get the post by its ID
    post = get_object_or_404(Post, id=post_id, user=request.user)
    
    # If the method is POST, delete the post
    if request.method == 'POST':
        post.delete()  # Delete the post from the database
        return redirect('home')  # Redirect to the home page after deletion
    
    return render(request, 'social/confirm_delete.html', {'post': post})


 # Registration view
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Get cleaned data from the form
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Create a new user but don't save it yet
            user = User(username=username, email=email)

            # Set the user's password securely using the set_password method
            user.set_password(password)

            # Save the user to the database
            user.save()

            # Now create the user's profile (if you are using a Profile model)
            # Profile.objects.create(user=user)

            messages.success(request, 'Account created successfully! You can now log in.')
            return redirect('login')  # Redirect to the login page after registration

    else:
        form = RegistrationForm()

    return render(request, 'social/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # Add some debugging logs
        print(f"Attempting login for user: {username}")

        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_active:
            print(f"User {username} authenticated successfully.")
            login(request, user)
            messages.success(request, 'Login successful!')
            # return redirect('home')
        else:
            print(f"Authentication failed for user: {username}")
            messages.error(request, 'Invalid credentials.')

    return render(request, 'social/login.html')


# Logout view
def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')

@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            # Associate the post with the logged-in user
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('home')  # Redirect to home after saving
    else:
        form = PostForm()

    return render(request, 'social/create_post.html', {'form': form})


def home(request):
    posts = Post.objects.all().order_by('-created_at')
    comments = Comment.objects.all().order_by('-created_at')
    form = CommentForm()

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            post_id = request.POST.get('post_id')  # Get the post ID from the form
            post = get_object_or_404(Post, id=post_id)  # Fetch the related Post
            comment = form.save(commit=False)
            comment.user = request.user
            comment.post = post
            comment.save()
            return redirect('home')  # Adjust if needed

    return render(request, 'social/home.html', {'posts': posts, 'comments': comments, 'form': form})
