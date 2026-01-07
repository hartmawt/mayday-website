// Blog functionality
document.addEventListener('DOMContentLoaded', function() {
    initializeBlogEditor();
    initializeBlogPosts();
    initializeImageUpload();
    initializeModal();
});

// Initialize blog editor functionality
function initializeBlogEditor() {
    const editorToolbar = document.querySelector('.editor-toolbar');
    const contentArea = document.querySelector('.content-area');
    const blogForm = document.getElementById('blogForm');
    const previewBtn = document.getElementById('previewBtn');

    if (!editorToolbar || !contentArea) return;

    // Editor toolbar functionality
    editorToolbar.addEventListener('click', function(e) {
        if (e.target.classList.contains('editor-btn') || e.target.closest('.editor-btn')) {
            e.preventDefault();
            const btn = e.target.classList.contains('editor-btn') ? e.target : e.target.closest('.editor-btn');
            const command = btn.dataset.command;
            
            if (command === 'createLink') {
                const url = prompt('Enter the URL:');
                if (url) {
                    document.execCommand(command, false, url);
                }
            } else {
                document.execCommand(command, false, null);
            }
            
            // Toggle active state
            btn.classList.toggle('active');
            contentArea.focus();
        }
    });

    // Handle form submission
    if (blogForm) {
        blogForm.addEventListener('submit', function(e) {
            e.preventDefault();
            publishBlogPost();
        });
    }

    // Handle preview
    if (previewBtn) {
        previewBtn.addEventListener('click', function(e) {
            e.preventDefault();
            previewBlogPost();
        });
    }
}

// Initialize image upload functionality
function initializeImageUpload() {
    const imageInput = document.getElementById('blogImage');
    const imagePreview = document.getElementById('imagePreview');
    const previewImg = document.getElementById('previewImg');
    const imageSizeSelect = document.getElementById('imageSize');
    const removeImageBtn = document.getElementById('removeImage');

    if (!imageInput) return;

    imageInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                previewImg.src = e.target.result;
                imagePreview.style.display = 'block';
                updateImageSize();
            };
            reader.readAsDataURL(file);
        }
    });

    if (imageSizeSelect) {
        imageSizeSelect.addEventListener('change', updateImageSize);
    }

    if (removeImageBtn) {
        removeImageBtn.addEventListener('click', function() {
            imageInput.value = '';
            imagePreview.style.display = 'none';
            previewImg.src = '';
        });
    }

    function updateImageSize() {
        const size = imageSizeSelect.value;
        previewImg.className = size;
        
        // Update preview image styling
        switch(size) {
            case 'small':
                previewImg.style.maxWidth = '300px';
                break;
            case 'medium':
                previewImg.style.maxWidth = '500px';
                break;
            case 'large':
                previewImg.style.maxWidth = '700px';
                break;
            case 'full':
                previewImg.style.maxWidth = '100%';
                break;
        }
    }
}

// Initialize blog posts functionality
function initializeBlogPosts() {
    const blogGrid = document.getElementById('blogGrid');
    const loadMoreBtn = document.getElementById('loadMoreBtn');

    if (!blogGrid) return;

    // Load existing blog posts
    loadBlogPosts();

    // Handle admin actions with high priority
    blogGrid.addEventListener('click', function(e) {
        // Check if this is a blog delete button specifically
        const deleteBtn = e.target.closest('.btn-delete');
        if (deleteBtn && e.target.closest('.blog-post-card')) {
            e.preventDefault();
            e.stopPropagation();
            e.stopImmediatePropagation(); // Stop all other listeners
            const postCard = e.target.closest('.blog-post-card');
            deleteBlogPost(postCard);
            return false;
        }
        
        if (e.target.closest('.btn-edit')) {
            e.preventDefault();
            e.stopPropagation();
            const postCard = e.target.closest('.blog-post-card');
            editBlogPost(postCard);
        } else if (e.target.closest('.read-more')) {
            e.preventDefault();
            const postCard = e.target.closest('.blog-post-card');
            openBlogPost(postCard);
        }
    }, true); // Use capture phase to run before other listeners

    // Load more posts
    if (loadMoreBtn) {
        loadMoreBtn.addEventListener('click', function() {
            loadMoreBlogPosts();
        });
    }
}

// Initialize modal functionality
function initializeModal() {
    const modal = document.getElementById('blogModal');
    const closeBtn = document.getElementById('blogModalClose');
    const fullscreenBtn = document.getElementById('blogModalFullscreen');
    const modalContent = document.getElementById('blogModalContent');

    if (!modal) return;

    // Close modal
    if (closeBtn) {
        closeBtn.addEventListener('click', function() {
            closeModal();
        });
    }

    // Toggle fullscreen
    if (fullscreenBtn) {
        fullscreenBtn.addEventListener('click', function() {
            toggleFullscreen();
        });
    }

    // Close modal on backdrop click
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            closeModal();
        }
    });

    // Close modal on escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && modal.style.display !== 'none') {
            if (modalContent && modalContent.classList.contains('fullscreen')) {
                toggleFullscreen();
            } else {
                closeModal();
            }
        }
    });
}

// Publish blog post
async function publishBlogPost() {
    const form = document.getElementById('blogForm');
    const formData = new FormData(form);
    const contentArea = document.querySelector('.content-area');
    
    // Add content from editor
    formData.append('content', contentArea.innerHTML);
    
    // Check if we're editing an existing post
    const editingPostId = form.dataset.editingPostId;
    if (editingPostId) {
        formData.append('id', editingPostId);
        
        // If editing and no new image uploaded, preserve existing image
        const imageInput = document.getElementById('blogImage');
        const imagePreview = document.getElementById('imagePreview');
        if (!imageInput.files.length && imagePreview.style.display !== 'none') {
            const previewImg = document.getElementById('previewImg');
            if (previewImg.src && !previewImg.src.startsWith('blob:')) {
                formData.append('existing_image', previewImg.src);
            }
        }
    }
    
    // Show loading
    showLoading();
    
    try {
        const response = await fetch('/api/blog-posts', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Reset form
            form.reset();
            contentArea.innerHTML = '';
            document.getElementById('imagePreview').style.display = 'none';
            delete form.dataset.editingPostId;
            
            // Reset button text
            const submitBtn = form.querySelector('button[type="submit"]');
            submitBtn.innerHTML = '<i class="fas fa-save"></i> Publish Post';
            
            showNotification(result.message, 'success');
            
            // Reload the page to show the updated posts
            window.location.reload();
        } else {
            showNotification(result.error || 'Failed to save blog post', 'error');
        }
    } catch (error) {
        console.error('Error saving blog post:', error);
        showNotification('Failed to save blog post', 'error');
    } finally {
        hideLoading();
    }
}

// Preview blog post
function previewBlogPost() {
    const title = document.getElementById('blogTitle').value;
    const author = document.getElementById('blogAuthor').value;
    const content = document.querySelector('.content-area').innerHTML;
    const imagePreview = document.getElementById('imagePreview');
    
    if (!title || !content) {
        showNotification('Please fill in the title and content fields.', 'warning');
        return;
    }
    
    const previewContent = `
        <article class="blog-preview">
            <header class="blog-preview-header">
                <h1>${title}</h1>
                <div class="blog-preview-meta">
                    <span class="blog-date">${new Date().toLocaleDateString('en-US', { 
                        year: 'numeric', 
                        month: 'long', 
                        day: 'numeric' 
                    })}</span>
                    <span class="blog-author">${author || 'Mayday Plumbing Team'}</span>
                </div>
            </header>
            ${imagePreview.style.display !== 'none' ? 
                `<img src="${document.getElementById('previewImg').src}" 
                     class="${document.getElementById('imageSize').value}" 
                     alt="Featured image">` : ''}
            <div class="blog-preview-content">
                ${content}
            </div>
        </article>
    `;
    
    openModal(previewContent, title);
}

// Load blog posts from storage/API
function loadBlogPosts() {
    // This would typically load from your backend
    // For now, we'll just show the welcome post
}

// Load more blog posts
function loadMoreBlogPosts() {
    showLoading();
    
    // Simulate loading more posts
    setTimeout(() => {
        hideLoading();
        // Hide load more button if no more posts
        document.getElementById('loadMoreBtn').style.display = 'none';
    }, 1000);
}

// Add new post to grid
function addNewPostToGrid(postData) {
    const blogGrid = document.getElementById('blogGrid');
    const isAdmin = document.querySelector('.admin-blog-section') !== null;
    
    const postCard = document.createElement('div');
    postCard.className = 'blog-post-card';
    
    postCard.innerHTML = `
        ${postData.image ? `
            <div class="blog-post-image">
                <img src="${postData.image}" alt="${postData.title}">
            </div>
        ` : ''}
        <div class="blog-post-content">
            <div class="blog-post-meta">
                <span class="blog-date">${postData.date}</span>
                <span class="blog-author">${postData.author}</span>
            </div>
            <h3>${postData.title}</h3>
            <p>${stripHtml(postData.content).substring(0, 150)}...</p>
            <a href="#" class="read-more">Read More <i class="fas fa-arrow-right"></i></a>
            ${isAdmin ? `
                <div class="admin-actions">
                    <button class="btn-edit" title="Edit Post">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn-delete" title="Delete Post">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            ` : ''}
        </div>
    `;
    
    // Store post data for later retrieval
    postCard.dataset.postData = JSON.stringify(postData);
    
    // Add to beginning of grid
    blogGrid.insertBefore(postCard, blogGrid.firstChild);
}

// Edit blog post
function editBlogPost(postCard) {
    const postData = JSON.parse(postCard.dataset.postData);
    
    // Store the post ID for updating
    const form = document.getElementById('blogForm');
    form.dataset.editingPostId = postData.id;
    
    // Populate form with existing data
    document.getElementById('blogTitle').value = postData.title;
    document.getElementById('blogAuthor').value = postData.author;
    document.querySelector('.content-area').innerHTML = decodeHtmlEntities(postData.content);
    
    // Handle image if present
    if (postData.image) {
        const imagePreview = document.getElementById('imagePreview');
        const previewImg = document.getElementById('previewImg');
        const imageSizeSelect = document.getElementById('imageSize');
        
        previewImg.src = postData.image;
        imageSizeSelect.value = postData.imageSize || 'medium';
        imagePreview.style.display = 'block';
        updateImageSize();
    }
    
    // Update form button text
    const submitBtn = form.querySelector('button[type="submit"]');
    submitBtn.innerHTML = '<i class="fas fa-save"></i> Update Post';
    
    // Scroll to form
    document.querySelector('.admin-blog-section').scrollIntoView({ 
        behavior: 'smooth' 
    });
    
    showNotification('Post loaded for editing', 'info');
}

// Delete blog post
async function deleteBlogPost(postCard) {
    const confirmed = await showConfirmModal({
        title: 'Delete Blog Post',
        message: 'Are you sure you want to delete this blog post? This action cannot be undone.',
        confirmText: 'Delete',
        cancelText: 'Cancel',
        type: 'danger',
        confirmButtonType: 'danger'
    });
    
    if (!confirmed) {
        return;
    }
    
    const postData = JSON.parse(postCard.dataset.postData);
    
    try {
        showLoading();
        
        
        const response = await fetch(`/api/blog-posts/${postData.id}`, {
            method: 'DELETE'
        });
        
        
        const result = await response.json();
        
        if (result.success) {
            postCard.remove();
            showNotification(result.message, 'success');
        } else {
            showNotification(result.error || 'Failed to delete blog post', 'error');
        }
    } catch (error) {
        console.error('Error deleting blog post:', error);
        showNotification('Failed to delete blog post', 'error');
    } finally {
        hideLoading();
    }
}

// Open blog post in modal
function openBlogPost(postCard) {
    console.log('Raw postData:', postCard.dataset.postData);
    let postData;
    try {
        postData = JSON.parse(postCard.dataset.postData);
    } catch (error) {
        console.error('JSON parsing error:', error);
        console.error('Problematic JSON:', postCard.dataset.postData);
        console.error('First 200 chars:', postCard.dataset.postData.substring(0, 200));
        return;
    }
    
    // Decode HTML entities
    const decodedContent = decodeHtmlEntities(postData.content);
    
    const modalContent = `
        <article class="blog-full-post">
            <div class="blog-post-meta" style="margin-bottom: 1rem;">
                <span class="blog-date">${postData.date}</span>
                <span class="blog-author">${postData.author}</span>
            </div>
            ${postData.image ? 
                `<img src="${postData.image}" 
                     class="${postData.imageSize || 'medium'}" 
                     alt="${postData.title}" 
                     style="margin-bottom: 1.5rem;">` : ''}
            <div class="blog-post-body">
                ${decodedContent}
            </div>
        </article>
    `;
    
    openModal(modalContent, postData.title);
}

// Modal functions
function openModal(content, title = '') {
    const modal = document.getElementById('blogModal');
    const modalBody = document.getElementById('blogModalBody');
    const modalTitle = document.getElementById('blogModalTitle');
    const modalContent = document.getElementById('blogModalContent');
    
    modalBody.innerHTML = content;
    modalTitle.textContent = title;
    
    // Reset fullscreen state
    modalContent.classList.remove('fullscreen');
    updateFullscreenIcon(false);
    
    modal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

function closeModal() {
    const modal = document.getElementById('blogModal');
    const modalContent = document.getElementById('blogModalContent');
    
    // Reset fullscreen state
    modalContent.classList.remove('fullscreen');
    updateFullscreenIcon(false);
    
    modal.style.display = 'none';
    document.body.style.overflow = 'auto';
}

function toggleFullscreen() {
    const modalContent = document.getElementById('blogModalContent');
    const isFullscreen = modalContent.classList.contains('fullscreen');
    
    if (isFullscreen) {
        modalContent.classList.remove('fullscreen');
    } else {
        modalContent.classList.add('fullscreen');
    }
    
    updateFullscreenIcon(!isFullscreen);
}

function updateFullscreenIcon(isFullscreen) {
    const fullscreenBtn = document.getElementById('blogModalFullscreen');
    const icon = fullscreenBtn.querySelector('i');
    
    if (isFullscreen) {
        icon.className = 'fas fa-compress';
        fullscreenBtn.title = 'Exit Fullscreen';
    } else {
        icon.className = 'fas fa-expand';
        fullscreenBtn.title = 'Enter Fullscreen';
    }
}

// Utility functions
function stripHtml(html) {
    const temp = document.createElement('div');
    temp.innerHTML = html;
    return temp.textContent || temp.innerText || '';
}

function decodeHtmlEntities(html) {
    const temp = document.createElement('div');
    temp.innerHTML = html;
    return temp.innerHTML;
}

function showLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.style.display = 'flex';
    }
}

function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.style.display = 'none';
    }
}

function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existingNotification = document.querySelector('.notification');
    if (existingNotification) {
        existingNotification.remove();
    }
    
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        ${message}
        <button class="notification-close">&times;</button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
    
    // Handle close button
    notification.querySelector('.notification-close').addEventListener('click', () => {
        notification.remove();
    });
}

// Navigation active state
function updateActiveNavLink() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
}

// Initialize navigation on page load
updateActiveNavLink();