// ProConnect Main JavaScript File

// Global variables
let socket = null;

// Initialize Socket.IO connection
function initializeSocket() {
    if (typeof io !== 'undefined') {
        socket = io();
        
        socket.on('connect', function() {
            console.log('Connected to server');
        });
        
        socket.on('disconnect', function() {
            console.log('Disconnected from server');
        });
        
        socket.on('notification', function(data) {
            showNotification(data.message, data.type || 'info');
        });
    }
}

// Show notification function
function showNotification(message, type = 'info') {
    const alertClass = `alert-${type === 'error' ? 'danger' : type}`;
    const alertHtml = `
        <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    // Insert at the top of the main container
    const mainContainer = document.querySelector('main .container');
    if (mainContainer) {
        mainContainer.insertAdjacentHTML('afterbegin', alertHtml);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            const alert = document.querySelector('.alert');
            if (alert) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 5000);
    }
}

// Format date function
function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 1) {
        return 'Today';
    } else if (diffDays === 2) {
        return 'Yesterday';
    } else if (diffDays < 7) {
        return `${diffDays - 1} days ago`;
    } else {
        return date.toLocaleDateString();
    }
}

// Format number with commas
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// Validate email function
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Validate URL function
function isValidUrl(string) {
    try {
        new URL(string);
        return true;
    } catch (_) {
        return false;
    }
}

// File validation function
function validateFile(file, allowedTypes, maxSizeMB) {
    if (!file) return { valid: false, message: 'No file selected' };
    
    // Check file size
    const fileSizeMB = file.size / (1024 * 1024);
    if (fileSizeMB > maxSizeMB) {
        return { valid: false, message: `File size must be less than ${maxSizeMB}MB` };
    }
    
    // Check file type
    if (allowedTypes && !allowedTypes.includes(file.type)) {
        return { valid: false, message: 'Invalid file type' };
    }
    
    return { valid: true };
}

// Show loading state
function showLoading(element) {
    element.classList.add('loading');
    element.disabled = true;
}

// Hide loading state
function hideLoading(element) {
    element.classList.remove('loading');
    element.disabled = false;
}

// Debounce function
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Throttle function
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Copy to clipboard function
function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showNotification('Copied to clipboard!', 'success');
        }).catch(() => {
            showNotification('Failed to copy to clipboard', 'error');
        });
    } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        try {
            document.execCommand('copy');
            showNotification('Copied to clipboard!', 'success');
        } catch (err) {
            showNotification('Failed to copy to clipboard', 'error');
        }
        document.body.removeChild(textArea);
    }
}

// Smooth scroll to element
function smoothScrollTo(element, offset = 0) {
    const targetPosition = element.offsetTop - offset;
    window.scrollTo({
        top: targetPosition,
        behavior: 'smooth'
    });
}

// Auto-resize textarea
function autoResizeTextarea(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = textarea.scrollHeight + 'px';
}

// Initialize tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Initialize popovers
function initializePopovers() {
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

// Initialize lightbox functionality
function initializeLightbox() {
    const lightbox = document.getElementById('imageLightbox');
    const lightboxImage = document.getElementById('lightboxImage');
    const closeBtn = document.getElementById('closeLightbox');
    
    // Add click event to all post images
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('post-image') || e.target.closest('.post-image')) {
            const img = e.target.tagName === 'IMG' ? e.target : e.target.querySelector('img');
            if (img && img.src) {
                lightboxImage.src = img.src;
                lightbox.style.display = 'flex';
                document.body.style.overflow = 'hidden';
            }
        }
    });
    
    // Close lightbox
    function closeLightbox() {
        lightbox.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
    
    closeBtn.addEventListener('click', closeLightbox);
    lightbox.addEventListener('click', function(e) {
        if (e.target === lightbox) {
            closeLightbox();
        }
    });
    
    // Close on escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && lightbox.style.display === 'flex') {
            closeLightbox();
        }
    });
}

// Handle form submissions
function handleFormSubmission(form, successCallback = null, errorCallback = null) {
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        
        showLoading(submitBtn);
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Processing...';
        
        const formData = new FormData(form);
        
        fetch(form.action, {
            method: form.method || 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success || data.message) {
                if (successCallback) {
                    successCallback(data);
                } else {
                    showNotification(data.message || 'Success!', 'success');
                }
            } else {
                throw new Error(data.error || 'An error occurred');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            if (errorCallback) {
                errorCallback(error);
            } else {
                showNotification(error.message || 'An error occurred', 'error');
            }
        })
        .finally(() => {
            hideLoading(submitBtn);
            submitBtn.innerHTML = originalText;
        });
    });
}

// Handle AJAX requests
function makeRequest(url, options = {}) {
    const defaultOptions = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    };
    
    const requestOptions = { ...defaultOptions, ...options };
    
    return fetch(url, requestOptions)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        });
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Socket.IO
    initializeSocket();
    
    // Initialize Bootstrap components
    initializeTooltips();
    initializePopovers();
    
    // Initialize lightbox
    initializeLightbox();
    
    // Auto-resize textareas
    document.querySelectorAll('textarea').forEach(textarea => {
        textarea.addEventListener('input', function() {
            autoResizeTextarea(this);
        });
    });
    
    // Handle password toggle
    document.querySelectorAll('.password-toggle').forEach(toggle => {
        toggle.addEventListener('click', function() {
            const input = this.previousElementSibling;
            const icon = this.querySelector('i');
            
            if (input.type === 'password') {
                input.type = 'text';
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
            } else {
                input.type = 'password';
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            }
        });
    });
    
    // Handle file input preview
    document.querySelectorAll('input[type="file"]').forEach(input => {
        input.addEventListener('change', function() {
            const file = this.files[0];
            const preview = this.parentElement.querySelector('.file-preview');
            
            if (file && preview) {
                if (file.type.startsWith('image/')) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        preview.innerHTML = `<img src="${e.target.result}" class="img-thumbnail" style="max-height: 100px;">`;
                    };
                    reader.readAsDataURL(file);
                } else {
                    preview.innerHTML = `<span class="badge bg-primary">${file.name}</span>`;
                }
            }
        });
    });
    
    // Handle search functionality
    const searchInput = document.querySelector('#searchInput');
    if (searchInput) {
        const debouncedSearch = debounce(function(query) {
            // Implement search functionality here
            console.log('Searching for:', query);
        }, 300);
        
        searchInput.addEventListener('input', function() {
            debouncedSearch(this.value);
        });
    }
    
    // Handle infinite scroll for posts
    let page = 1;
    let loading = false;
    
    function loadMorePosts() {
        if (loading) return;
        
        loading = true;
        const postsContainer = document.querySelector('#postsFeed');
        
        if (postsContainer) {
            fetch(`/api/posts?page=${page}`)
                .then(response => response.json())
                .then(data => {
                    if (data.posts && data.posts.length > 0) {
                        // Append new posts to container
                        data.posts.forEach(post => {
                            // Create post HTML and append
                            // This would be implemented based on your post structure
                        });
                        page++;
                    }
                })
                .catch(error => {
                    console.error('Error loading posts:', error);
                })
                .finally(() => {
                    loading = false;
                });
        }
    }
    
    // Infinite scroll
    window.addEventListener('scroll', throttle(function() {
        if ((window.innerHeight + window.scrollY) >= document.body.offsetHeight - 1000) {
            loadMorePosts();
        }
    }, 100));
    
    // Handle connection requests
    document.querySelectorAll('.connect-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const userId = this.dataset.userId;
            
            makeRequest(`/connect/${userId}`, {
                method: 'POST'
            })
            .then(data => {
                if (data.message) {
                    this.innerHTML = '<i class="fas fa-check me-1"></i>Request Sent';
                    this.classList.remove('btn-primary');
                    this.classList.add('btn-success');
                    this.disabled = true;
                    showNotification('Connection request sent successfully!', 'success');
                }
            })
            .catch(error => {
                showNotification(error.message || 'Error sending connection request', 'error');
            });
        });
    });
});

// Export functions for use in other scripts
window.ProConnect = {
    showNotification,
    formatDate,
    formatNumber,
    isValidEmail,
    isValidUrl,
    validateFile,
    showLoading,
    hideLoading,
    debounce,
    throttle,
    copyToClipboard,
    smoothScrollTo,
    makeRequest,
    handleFormSubmission
}; 