// Fashion Store - Main JavaScript File

// Document Ready
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// Initialize Application
function initializeApp() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize shopping cart functionality
    initShoppingCart();
    
    // Initialize search functionality
    initSearch();
    
    // Initialize form validations
    initFormValidations();
    
    // Initialize lazy loading for images
    initLazyLoading();
    
    // Initialize notification system
    initNotifications();
}

// Shopping Cart Functions
function initShoppingCart() {
    // Update cart badge count
    updateCartBadge();
    
    // Cart item quantity handlers
    document.querySelectorAll('.cart-quantity-btn').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const action = this.dataset.action;
            const itemId = this.dataset.itemId;
            updateCartItemQuantity(itemId, action);
        });
    });
}

function updateCartBadge() {
    // This would typically fetch from backend or local storage
    const cartItems = getCartItemsCount();
    const badge = document.querySelector('.cart-badge');
    if (badge) {
        badge.textContent = cartItems;
        badge.style.display = cartItems > 0 ? 'inline' : 'none';
    }
}

function getCartItemsCount() {
    // Simulate cart items count - in real app would fetch from backend
    return 0;
}

function updateCartItemQuantity(itemId, action) {
    // Show loading state
    showLoadingSpinner();
    
    // Simulate API call
    setTimeout(() => {
        hideLoadingSpinner();
        updateCartBadge();
        showNotification('Cart updated successfully', 'success');
    }, 500);
}

// Search Functions
function initSearch() {
    const searchInput = document.querySelector('#searchInput');
    if (searchInput) {
        let searchTimeout;
        
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                performSearch(this.value);
            }, 300);
        });
    }
}

function performSearch(query) {
    if (query.length < 2) return;
    
    // Simulate search suggestions
    console.log('Searching for:', query);
    // In a real app, this would make an AJAX request to get search suggestions
}

// Form Validation Functions
function initFormValidations() {
    // Bootstrap form validation
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
    
    // Custom validations
    initPasswordConfirmation();
    initPhoneValidation();
}

function initPasswordConfirmation() {
    const passwordFields = document.querySelectorAll('input[type="password"]');
    const confirmPasswordField = document.querySelector('#confirm_password');
    
    if (confirmPasswordField) {
        confirmPasswordField.addEventListener('input', function() {
            const password = document.querySelector('#password').value;
            const confirmPassword = this.value;
            
            if (password !== confirmPassword) {
                this.setCustomValidity('Passwords do not match');
            } else {
                this.setCustomValidity('');
            }
        });
    }
}

function initPhoneValidation() {
    const phoneInputs = document.querySelectorAll('input[type="tel"]');
    
    phoneInputs.forEach(input => {
        input.addEventListener('input', function() {
            const phonePattern = /^[6-9]\d{9}$/;
            if (!phonePattern.test(this.value)) {
                this.setCustomValidity('Please enter a valid 10-digit Indian phone number');
            } else {
                this.setCustomValidity('');
            }
        });
    });
}

// Image Lazy Loading
function initLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');
    
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        images.forEach(img => imageObserver.observe(img));
    } else {
        // Fallback for older browsers
        images.forEach(img => {
            img.src = img.dataset.src;
        });
    }
}

// Notification System
function initNotifications() {
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    
    alerts.forEach(alert => {
        setTimeout(() => {
            if (alert.classList.contains('show')) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 5000);
    });
}

function showNotification(message, type = 'info') {
    const alertContainer = document.querySelector('.notification-container') || createNotificationContainer();
    
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    alertContainer.appendChild(alertDiv);
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        if (alertDiv.classList.contains('show')) {
            const bsAlert = new bootstrap.Alert(alertDiv);
            bsAlert.close();
        }
    }, 5000);
}

function createNotificationContainer() {
    const container = document.createElement('div');
    container.className = 'notification-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '1080';
    document.body.appendChild(container);
    return container;
}

// Loading Spinner Functions
function showLoadingSpinner() {
    const spinner = document.querySelector('#loadingSpinner') || createLoadingSpinner();
    spinner.style.display = 'flex';
}

function hideLoadingSpinner() {
    const spinner = document.querySelector('#loadingSpinner');
    if (spinner) {
        spinner.style.display = 'none';
    }
}

function createLoadingSpinner() {
    const spinner = document.createElement('div');
    spinner.id = 'loadingSpinner';
    spinner.className = 'position-fixed top-0 start-0 w-100 h-100 d-flex justify-content-center align-items-center';
    spinner.style.backgroundColor = 'rgba(0,0,0,0.5)';
    spinner.style.zIndex = '2000';
    spinner.style.display = 'none';
    
    spinner.innerHTML = `
        <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
        </div>
    `;
    
    document.body.appendChild(spinner);
    return spinner;
}

// Utility Functions
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR'
    }).format(amount);
}

function formatDate(date) {
    return new Intl.DateTimeFormat('en-IN', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    }).format(new Date(date));
}

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

// Product Functions
function addToWishlist(productId) {
    showLoadingSpinner();
    
    fetch(`/add_to_wishlist/${productId}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => {
        if (response.redirected) {
            window.location.href = response.url;
        }
        return response.text();
    })
    .then(data => {
        hideLoadingSpinner();
        // Handle response - could show success message or update UI
        window.location.reload();
    })
    .catch(error => {
        hideLoadingSpinner();
        console.error('Error:', error);
        showNotification('Failed to add to wishlist', 'danger');
    });
}

function quickAddToCart(productId, size = 'M') {
    const formData = new FormData();
    formData.append('product_id', productId);
    formData.append('size', size);
    formData.append('quantity', '1');
    
    showLoadingSpinner();
    
    fetch('/add_to_cart', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (response.redirected) {
            window.location.href = response.url;
        }
        return response.text();
    })
    .then(data => {
        hideLoadingSpinner();
        updateCartBadge();
        showNotification('Item added to cart!', 'success');
    })
    .catch(error => {
        hideLoadingSpinner();
        console.error('Error:', error);
        showNotification('Failed to add to cart', 'danger');
    });
}

// Admin Functions
function confirmAction(message) {
    return confirm(message);
}

function exportTableToCSV(tableId, filename) {
    const table = document.getElementById(tableId);
    if (!table) return;
    
    let csv = [];
    const rows = table.querySelectorAll('tr');
    
    for (let i = 0; i < rows.length; i++) {
        const row = [];
        const cols = rows[i].querySelectorAll('td, th');
        
        for (let j = 0; j < cols.length; j++) {
            row.push(cols[j].innerText);
        }
        
        csv.push(row.join(','));
    }
    
    downloadCSV(csv.join('\n'), filename);
}

function downloadCSV(csv, filename) {
    const csvFile = new Blob([csv], { type: 'text/csv' });
    const downloadLink = document.createElement('a');
    
    downloadLink.download = filename;
    downloadLink.href = window.URL.createObjectURL(csvFile);
    downloadLink.style.display = 'none';
    
    document.body.appendChild(downloadLink);
    downloadLink.click();
    document.body.removeChild(downloadLink);
}

// Image Preview Function
function previewImage(input, previewId) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            document.getElementById(previewId).src = e.target.result;
        };
        
        reader.readAsDataURL(input.files[0]);
    }
}

// Local Storage Helpers
function setLocalStorage(key, value) {
    try {
        localStorage.setItem(key, JSON.stringify(value));
    } catch (e) {
        console.error('Error saving to localStorage:', e);
    }
}

function getLocalStorage(key) {
    try {
        const item = localStorage.getItem(key);
        return item ? JSON.parse(item) : null;
    } catch (e) {
        console.error('Error reading from localStorage:', e);
        return null;
    }
}

// Analytics Helper
function trackEvent(eventName, eventData = {}) {
    // This would integrate with analytics service like Google Analytics
    console.log('Event tracked:', eventName, eventData);
}

// Page-specific functions can be added here
window.FashionStore = {
    addToWishlist,
    quickAddToCart,
    showNotification,
    showLoadingSpinner,
    hideLoadingSpinner,
    formatCurrency,
    formatDate,
    confirmAction,
    exportTableToCSV,
    trackEvent
};
