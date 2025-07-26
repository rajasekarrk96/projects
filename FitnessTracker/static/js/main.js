// Main JavaScript for Workout Sphere

// Function to format relative time
function formatRelativeTime(timestamp) {
    const now = new Date();
    const date = new Date(timestamp * 1000);
    const diffInSeconds = Math.floor((now - date) / 1000);

    if (diffInSeconds < 60) return 'just now';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} minutes ago`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)} hours ago`;
    if (diffInSeconds < 2592000) return `${Math.floor(diffInSeconds / 86400)} days ago`;
    if (diffInSeconds < 31536000) return `${Math.floor(diffInSeconds / 2592000)} months ago`;
    return `${Math.floor(diffInSeconds / 31536000)} years ago`;
}

// Function to update all timestamps
function updateTimestamps() {
    document.querySelectorAll('[data-timestamp]').forEach(element => {
        const timestamp = element.getAttribute('data-timestamp');
        element.textContent = formatRelativeTime(timestamp);
    });
}

document.addEventListener('DOMContentLoaded', function() {
    // Update timestamps initially and every minute
    updateTimestamps();
    setInterval(updateTimestamps, 60000);

    // Mobile menu toggle
    const mobileMenuButton = document.querySelector('.md\\:hidden');
    if (mobileMenuButton) {
        mobileMenuButton.addEventListener('click', function() {
            const mobileMenu = this.querySelector('div');
            if (mobileMenu) {
                mobileMenu.classList.toggle('hidden');
            }
        });
    }

    // Like button functionality
    document.querySelectorAll('.like-button').forEach(button => {
        button.addEventListener('click', async () => {
            const postId = button.dataset.id;
            const response = await fetch(`/api/feed/${postId}/like`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            const data = await response.json();
            if (data.success) {
                // Update like count
                const likeCount = button.querySelector('.like-count');
                likeCount.textContent = data.likes;
                
                // Toggle like button state
                button.classList.toggle('text-blue-500');
                const icon = button.querySelector('svg');
                if (button.classList.contains('text-blue-500')) {
                    icon.setAttribute('fill', 'currentColor');
                } else {
                    icon.setAttribute('fill', 'none');
                }
            }
        });
    });

    // Comment form functionality
    document.querySelectorAll('.comment-form').forEach(form => {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const postId = form.dataset.postId;
            const textarea = form.querySelector('textarea');
            const content = textarea.value.trim();
            
            if (!content) return;
            
            const response = await fetch(`/api/feed/${postId}/comments`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ content })
            });
            
            const data = await response.json();
            if (data.success) {
                // Update comments container
                const commentsContainer = document.querySelector(`.comments-container[data-post-id="${postId}"]`);
                const comment = data.comment;
                commentsContainer.insertAdjacentHTML('afterbegin', `
                    <div class="comment mb-3">
                        <div class="flex items-start">
                            ${comment.user.profile_image ? `
                                <img src="${comment.user.profile_image}" alt="${comment.user.name}" class="h-8 w-8 rounded-full mr-2">
                            ` : `
                                <div class="h-8 w-8 rounded-full bg-blue-500 flex items-center justify-center text-white font-bold mr-2">
                                    ${comment.user.name[0].toUpperCase()}
                                </div>
                            `}
                            <div class="flex-1">
                                <p class="text-sm font-medium">${comment.user.name}</p>
                                <p class="text-sm text-gray-600">${comment.content}</p>
                                <p class="text-xs text-gray-500" data-timestamp="${new Date(comment.created_at).getTime() / 1000}"></p>
                            </div>
                        </div>
                    </div>
                `);
                
                // Update comment count
                const commentButton = document.querySelector(`.comment-button[data-id="${postId}"]`);
                const commentCount = commentButton.querySelector('.comment-count');
                commentCount.textContent = parseInt(commentCount.textContent) + 1;
                
                // Clear textarea
                textarea.value = '';
            }
        });
    });

    // Workout page functionality
    setupWorkoutPage();

    // Routine page functionality
    setupRoutinePage();
});

function setupWorkoutPage() {
    const addWorkoutBtn = document.getElementById('addWorkoutBtn');
    const emptyAddWorkoutBtn = document.getElementById('emptyAddWorkoutBtn');
    
    if (addWorkoutBtn) {
        addWorkoutBtn.addEventListener('click', function() {
            window.location.href = '/add-workout';
        });
    }
    
    if (emptyAddWorkoutBtn) {
        emptyAddWorkoutBtn.addEventListener('click', function() {
            window.location.href = '/add-workout';
        });
    }
    
    // Initialize timer variables
    let timerInterval;
    let seconds = 0;
    let currentSet = 1;
    let totalSets = 3;
    const setDuration = 120; // 2 minutes between sets
    
    // Timer functions
    function showWorkoutTimer(workoutId) {
        document.getElementById('timerModal').classList.remove('hidden');
        document.getElementById('setInfo').textContent = `Set ${currentSet} of ${totalSets}`;
    }
    
    function hideTimerModal() {
        document.getElementById('timerModal').classList.add('hidden');
        stopTimer();
    }
    
    function startTimer() {
        document.getElementById('startTimerBtn').classList.add('hidden');
        document.getElementById('pauseTimerBtn').classList.remove('hidden');
        
        timerInterval = setInterval(() => {
            seconds++;
            updateTimerDisplay();
            
            if (seconds >= setDuration) {
                currentSet++;
                if (currentSet > totalSets) {
                    stopTimer();
                    return;
                }
                seconds = 0;
                document.getElementById('setInfo').textContent = `Set ${currentSet} of ${totalSets}`;
            }
        }, 1000);
    }
    
    function pauseTimer() {
        clearInterval(timerInterval);
        document.getElementById('startTimerBtn').classList.remove('hidden');
        document.getElementById('pauseTimerBtn').classList.add('hidden');
    }
    
    function stopTimer() {
        clearInterval(timerInterval);
        seconds = 0;
        currentSet = 1;
        updateTimerDisplay();
        document.getElementById('startTimerBtn').classList.remove('hidden');
        document.getElementById('pauseTimerBtn').classList.add('hidden');
    }
    
    function updateTimerDisplay() {
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        document.getElementById('timerDisplay').textContent = 
            `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
    }

    // Setup workout view buttons
    const viewWorkoutBtns = document.querySelectorAll('.view-workout');
    viewWorkoutBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const workoutId = this.getAttribute('data-id');
            window.location.href = `/workout/${workoutId}`;
        });
    });

    // Setup workout edit buttons
    const editWorkoutBtns = document.querySelectorAll('.edit-workout');
    editWorkoutBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const workoutId = this.getAttribute('data-id');
            window.location.href = `/edit-workout/${workoutId}`;
        });
    });

    // Setup workout delete buttons
    const deleteWorkoutBtns = document.querySelectorAll('.delete-workout');
    deleteWorkoutBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const workoutId = this.getAttribute('data-id');
            if (confirm('Are you sure you want to delete this workout?')) {
                fetch(`/api/workouts/${workoutId}`, {
                    method: 'DELETE',
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        window.location.reload();
                    } else {
                        alert('Error deleting workout');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Error deleting workout');
                });
            }
        });
    });
}

function setupRoutinePage() {
    const addRoutineBtn = document.getElementById('addRoutineBtn');
    const emptyAddRoutineBtn = document.getElementById('emptyAddRoutineBtn');
    
    if (addRoutineBtn) {
        addRoutineBtn.addEventListener('click', function() {
            window.location.href = '/add-routine';
        });
    }
    
    if (emptyAddRoutineBtn) {
        emptyAddRoutineBtn.addEventListener('click', function() {
            window.location.href = '/add-routine';
        });
    }
}

// Utility function to format dates
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
}

// Utility function for AJAX requests
async function fetchAPI(url, options = {}) {
    try {
        const response = await fetch(url, options);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}