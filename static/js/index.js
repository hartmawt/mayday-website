// Modern JavaScript for enhanced user experience
console.log('🚀 JavaScript file loaded successfully');

class MaydayWebsite {
    constructor() {
        console.log('🏗️ MaydayWebsite constructor called');
        this.init();
        // Load async content after a short delay to ensure DOM is ready
        setTimeout(() => {
            this.loadAsyncContent();
        }, 1000);
    }

    init() {
        this.bindEvents();
        this.setupNavigation();
        this.setupScrollEffects();
        this.setupFAQSearch();
        this.setupFormHandling();
        this.setupNotifications();
        this.setupAdmin();
        this.setupAnimations();
        this.setupServiceManagement();
        this.setupFAQManagement();
    }

    bindEvents() {
        // DOM content loaded
        document.addEventListener('DOMContentLoaded', () => {
            this.handleInitialLoad();
        });

        // Window events
        window.addEventListener('scroll', this.throttle(() => {
            this.handleScroll();
        }, 16));

        window.addEventListener('resize', this.throttle(() => {
            this.handleResize();
        }, 100));

        // Hash change for navigation
        window.addEventListener('hashchange', () => {
            this.handleNavigation();
        });

        // Clean up intervals when page unloads
        window.addEventListener('beforeunload', () => {
            this.stopReviewRotation();
        });
    }

    handleInitialLoad() {
        // Handle initial navigation if there's a hash
        if (window.location.hash) {
            this.handleNavigation();
        }
        
        // Add loading animation completion
        setTimeout(() => {
            document.body.classList.add('loaded');
        }, 100);

        // Initialize intersection observer for animations
        this.setupIntersectionObserver();
    }

    setupNavigation() {
        console.log('🔧 Setting up navigation...');
        const navToggle = document.querySelector('.nav-toggle');
        const navMenu = document.querySelector('.nav-menu');
        const navLinks = document.querySelectorAll('.nav-link');

        console.log('Navigation elements found:', {
            navToggle: !!navToggle,
            navMenu: !!navMenu,
            navLinks: navLinks.length,
            navToggleClasses: navToggle ? navToggle.className : 'not found',
            navMenuClasses: navMenu ? navMenu.className : 'not found'
        });

        // Mobile menu toggle with unified event handling
        if (navToggle && navMenu) {
            console.log('✅ Adding unified click listener to hamburger menu');

            // Check if already initialized to prevent duplicate listeners
            if (navToggle.hasAttribute('data-menu-initialized')) {
                console.log('⚠️ Menu already initialized, skipping...');
                return;
            }

            // Single click handler that works on both desktop and mobile
            const toggleMenu = (e) => {
                e.preventDefault();
                e.stopPropagation();

                console.log('🍔 Menu toggle triggered!', e.type);
                console.log('Before toggle - navMenu classes:', navMenu.className);
                console.log('Before toggle - navToggle classes:', navToggle.className);

                navMenu.classList.toggle('active');
                navToggle.classList.toggle('active');

                console.log('After toggle - navMenu classes:', navMenu.className);
                console.log('After toggle - navToggle classes:', navToggle.className);

                // Log computed styles to verify CSS is working
                const computedStyle = window.getComputedStyle(navMenu);
                console.log('Menu visibility:', computedStyle.visibility);
                console.log('Menu opacity:', computedStyle.opacity);
            };

            // Add click listener only to the main hamburger button
            navToggle.addEventListener('click', toggleMenu);

            // Make bars non-interactive to prevent double events
            const bars = navToggle.querySelectorAll('.bar');
            bars.forEach(bar => {
                bar.style.pointerEvents = 'none';
            });

            // Mark as initialized
            navToggle.setAttribute('data-menu-initialized', 'true');

        } else {
            console.error('❌ Navigation elements not found!');
        }

        // Close mobile menu when clicking on a link
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                if (navMenu) {
                    navMenu.classList.remove('active');
                }
                if (navToggle) {
                    navToggle.classList.remove('active');
                }
            });
        });

        // Close menu when clicking outside
        document.addEventListener('click', (e) => {
            if (navMenu && navToggle &&
                !navMenu.contains(e.target) &&
                !navToggle.contains(e.target) &&
                navMenu.classList.contains('active')) {

                console.log('🔒 Clicking outside menu, closing it');
                navMenu.classList.remove('active');
                navToggle.classList.remove('active');
            }
        });

        // Smooth scroll to sections
        navLinks.forEach(link => {
            if (link.getAttribute('href').startsWith('#')) {
                link.addEventListener('click', (e) => {
                    e.preventDefault();
                    const targetId = link.getAttribute('href').substring(1);
                    this.scrollToSection(targetId);
                    history.pushState(null, null, `#${targetId}`);
                });
            }
        });
    }

    handleNavigation() {
        const hash = window.location.hash.substring(1) || 'home';
        this.scrollToSection(hash);
        this.updateActiveNavLink(hash);
    }

    updateActiveNavLink(activeSection) {
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === `#${activeSection}`) {
                link.classList.add('active');
            }
        });
    }

    scrollToSection(sectionId) {
        const section = document.getElementById(sectionId);
        if (section) {
            const navbarHeight = document.querySelector('.navbar').offsetHeight;
            const sectionTop = section.offsetTop - navbarHeight;
            
            window.scrollTo({
                top: sectionTop,
                behavior: 'smooth'
            });
        }
    }

    setupScrollEffects() {
        const navbar = document.querySelector('.navbar');
        
        if (navbar) {
            // Navbar scroll effect
            const handleScroll = () => {
                if (window.scrollY > 50) {
                    navbar.classList.add('scrolled');
                } else {
                    navbar.classList.remove('scrolled');
                }
            };
            
            window.addEventListener('scroll', this.throttle(handleScroll, 16));
        }
    }

    setupIntersectionObserver() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        this.observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                }
            });
        }, observerOptions);

        // Initial observation
        this.observeAnimationElements();
        
        // Re-observe elements after a delay to catch any dynamically loaded content
        setTimeout(() => {
            this.observeAnimationElements();
        }, 2000);
    }
    
    observeAnimationElements() {
        // Observe elements for animation
        document.querySelectorAll('.service-card, .feature-box, .faq-item, .content-panel').forEach(el => {
            // Only observe if not already being observed
            if (!el.hasAttribute('data-observed')) {
                this.observer.observe(el);
                el.setAttribute('data-observed', 'true');
            }
        });
    }

    setupFAQSearch() {
        const searchInput = document.getElementById('search-field');
        if (searchInput) {
            searchInput.addEventListener('input', this.debounce(async (e) => {
                const searchTerm = e.target.value.trim();
                await this.searchFAQs(searchTerm);
            }, 300));
        }
        
        // Initial setup of FAQ accordion functionality
        this.setupFAQAccordion();
    }
    
    async searchFAQs(searchTerm) {
        const faqGrid = document.getElementById('faqGrid');
        const loadMoreContainer = document.querySelector('.faq-load-more');
        
        if (!faqGrid) return;
        
        try {
            if (searchTerm === '') {
                // Reset to initial state - load first 5 FAQs
                await this.resetFAQsToDefault();
                return;
            }
            
            // Search all FAQs
            const response = await fetch(`/api/faqs?search=${encodeURIComponent(searchTerm)}`);
            const data = await response.json();
            
            // Clear current FAQs (except add button)
            const faqItems = faqGrid.querySelectorAll('.faq-item:not(.add-faq-item)');
            faqItems.forEach(item => item.remove());
            
            // Hide load more button during search
            if (loadMoreContainer) {
                loadMoreContainer.style.display = 'none';
            }
            
            if (data.faqs && data.faqs.length > 0) {
                // Add search results
                data.faqs.forEach(faq => {
                    const faqItem = this.createFAQElement(faq);
                    // Insert before add button or at the end
                    const addButton = faqGrid.querySelector('.add-faq-item');
                    if (addButton) {
                        faqGrid.insertBefore(faqItem, addButton);
                    } else {
                        faqGrid.appendChild(faqItem);
                    }
                });
                
                // Trigger animation for new elements
                setTimeout(() => {
                    this.observeAnimationElements();
                }, 100);
            } else {
                // Show no results message
                const noResults = document.createElement('div');
                noResults.className = 'faq-item no-results';
                noResults.innerHTML = `
                    <h3>No FAQs found</h3>
                    <div class="faq-answer">
                        <p>No FAQs match your search term "${searchTerm}". Try different keywords.</p>
                    </div>
                `;
                
                const addButton = faqGrid.querySelector('.add-faq-item');
                if (addButton) {
                    faqGrid.insertBefore(noResults, addButton);
                } else {
                    faqGrid.appendChild(noResults);
                }
            }
        } catch (error) {
            console.error('Error searching FAQs:', error);
        }
    }
    
    async resetFAQsToDefault() {
        const faqGrid = document.getElementById('faqGrid');
        const loadMoreContainer = document.querySelector('.faq-load-more');
        
        if (!faqGrid) return;
        
        try {
            // Check if we're in admin mode
            const isAdmin = document.querySelector('.add-faq-item') !== null;
            const adminParam = isAdmin ? '&admin=true' : '';
            
            // Fetch first 5 FAQs
            const response = await fetch(`/api/faqs?limit=5&offset=0${adminParam}`);
            const data = await response.json();
            
            // Clear current FAQs (except add button and no-results)
            const faqItems = faqGrid.querySelectorAll('.faq-item:not(.add-faq-item)');
            faqItems.forEach(item => item.remove());
            
            // Reset pagination offset
            this.faqOffset = 5;
            
            if (data.faqs && data.faqs.length > 0) {
                // Add the first 5 FAQs
                data.faqs.forEach(faq => {
                    const faqItem = this.createFAQElement(faq);
                    // Insert before add button or load more button
                    const addButton = faqGrid.querySelector('.add-faq-item');
                    const insertBefore = addButton || loadMoreContainer;
                    if (insertBefore) {
                        faqGrid.insertBefore(faqItem, insertBefore);
                    } else {
                        faqGrid.appendChild(faqItem);
                    }
                });
                
                // Trigger animation for new elements
                setTimeout(() => {
                    this.observeAnimationElements();
                }, 100);
                
                // Show load more button if there might be more FAQs
                if (loadMoreContainer) {
                    // Check if there are potentially more FAQs (we loaded exactly 5)
                    if (data.faqs.length === 5) {
                        loadMoreContainer.style.display = 'block';
                        // Reset button state
                        const loadMoreBtn = document.getElementById('loadMoreFaqs');
                        if (loadMoreBtn) {
                            loadMoreBtn.innerHTML = '<i class="fas fa-chevron-down"></i> Load More FAQs';
                            loadMoreBtn.disabled = false;
                        }
                    } else {
                        loadMoreContainer.style.display = 'none';
                    }
                }
            }
        } catch (error) {
            console.error('Error resetting FAQs:', error);
        }
    }
    
    setupFAQAccordion() {
        // Use event delegation for dynamically added FAQ items
        const faqGrid = document.getElementById('faqGrid');
        if (faqGrid) {
            faqGrid.addEventListener('click', (e) => {
                const header = e.target.closest('.faq-item:not(.add-faq-item) h3');
                if (header) {
                    const faqItem = header.closest('.faq-item');
                    const isActive = faqItem.classList.contains('active');
                    
                    // Close all other FAQ items
                    document.querySelectorAll('.faq-item').forEach(otherItem => {
                        otherItem.classList.remove('active');
                    });
                    
                    // Toggle current item
                    if (!isActive) {
                        faqItem.classList.add('active');
                    }
                }
            });
        }
    }

    setupFormHandling() {
        const forms = document.querySelectorAll('form');
        
        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                this.handleFormSubmit(e);
            });
        });

        // Phone number formatting
        const phoneInputs = document.querySelectorAll('input[type="tel"], input[name*="phone"]');
        phoneInputs.forEach(input => {
            input.addEventListener('input', (e) => {
                this.formatPhoneNumber(e.target);
            });
        });
    }

    handleFormSubmit(e) {
        const form = e.target;
        const submitButton = form.querySelector('button[type="submit"]');
        
        // Don't show loading for forms that open in new tab
        if (form.target === '_blank') {
            return;
        }
        
        // Show loading state
        if (submitButton) {
            const originalText = submitButton.innerHTML;
            
            // For admin forms, use different loading text
            if (form.classList.contains('admin-form')) {
                submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Updating...';
                submitButton.classList.add('loading');
                
                // Also add loading state to the admin panel
                const adminPanel = form.closest('.admin-panel');
                if (adminPanel) {
                    adminPanel.classList.add('loading');
                }
            } else {
                submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';
            }
            
            submitButton.disabled = true;
            
            // Reset button after 3 seconds (in case of no redirect)
            setTimeout(() => {
                submitButton.innerHTML = originalText;
                submitButton.disabled = false;
                submitButton.classList.remove('loading');
                
                // Remove admin panel loading state
                const adminPanel = form.closest('.admin-panel');
                if (adminPanel) {
                    adminPanel.classList.remove('loading');
                }
            }, 3000);
        }

        // Show loading overlay for non-admin forms
        if (!form.classList.contains('admin-form')) {
            this.showLoadingOverlay();
        }
    }

    formatPhoneNumber(input) {
        let value = input.value.replace(/\D/g, '');
        if (value.length >= 6) {
            value = value.replace(/(\d{3})(\d{3})(\d{4})/, '($1) $2-$3');
        } else if (value.length >= 3) {
            value = value.replace(/(\d{3})(\d{3})/, '($1) $2');
        }
        input.value = value;
    }

    setupNotifications() {
        const notification = document.getElementById('notification');
        const closeButton = document.querySelector('.notification-close');

        if (notification && closeButton) {
            closeButton.addEventListener('click', () => {
                this.hideNotification();
            });

            // Auto-hide after 5 seconds
            setTimeout(() => {
                this.hideNotification();
            }, 5000);
        }
    }

    hideNotification() {
        const notification = document.getElementById('notification');
        if (notification) {
            notification.style.opacity = '0';
            notification.style.transform = 'translateY(-100%)';
            setTimeout(() => {
                notification.style.display = 'none';
            }, 300);
        }
    }

    setupAdmin() {
        console.log('=== setupAdmin() called ===');
        const sectionSelector = document.getElementById('section-selector');
        const descriptionText = document.getElementById('description-text');
        const descriptionGroup = document.getElementById('description-group');
        const deleteButtons = document.querySelectorAll('.admin-item .btn-delete, .staff-item .btn-delete');

        console.log('setupAdmin elements found:', {
            sectionSelector: !!sectionSelector,
            descriptionText: !!descriptionText,
            descriptionGroup: !!descriptionGroup,
            deleteButtons: deleteButtons.length
        });

        // Load content when selection changes
        if (sectionSelector) {
            sectionSelector.addEventListener('change', async (e) => {
                const sectionValue = e.target.value;

                if (!sectionValue) {
                    // Hide form group if no selection
                    if (descriptionGroup) descriptionGroup.style.display = 'none';
                    return;
                }

                // Show description group and load content
                if (descriptionGroup) descriptionGroup.style.display = 'block';

                // Show loading state
                const adminPanel = sectionSelector.closest('.admin-panel');
                if (adminPanel) {
                    adminPanel.classList.add('loading');
                }

                try {
                    const response = await fetch('/admin', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ section: sectionValue })
                    });

                    if (response.ok) {
                        const data = await response.json();
                        if (descriptionText) descriptionText.value = data.description || '';
                    } else {
                        console.error('Failed to load content:', response.status);
                        if (descriptionText) descriptionText.value = '';
                    }
                } catch (error) {
                    console.error('Error loading content:', error);
                    if (descriptionText) descriptionText.value = '';
                } finally {
                    // Hide loading state
                    if (adminPanel) {
                        adminPanel.classList.remove('loading');
                    }
                }
            });
        }

        // Use event delegation for admin/staff deletion to handle dynamically added elements
        const isOnBlogPage = window.location.pathname.includes('/blog');
        const blogGrid = document.querySelector('.blog-grid');

        console.log('Event delegation conditions:', {
            pathname: window.location.pathname,
            isOnBlogPage: isOnBlogPage,
            blogGridExists: !!blogGrid
        });

        if (!isOnBlogPage && !blogGrid) {
            console.log('✅ Setting up admin delete event delegation');

            // Debug: Check if admin items exist
            setTimeout(() => {
                const adminItems = document.querySelectorAll('.admin-item');
                const deleteButtons = document.querySelectorAll('.admin-item .btn-delete');
                console.log('Admin debug:', {
                    adminItems: adminItems.length,
                    deleteButtons: deleteButtons.length,
                    firstButtonAttrs: deleteButtons[0] ? {
                        id: deleteButtons[0].getAttribute('data-id'),
                        type: deleteButtons[0].getAttribute('data-type'),
                        classes: deleteButtons[0].className
                    } : null
                });
            }, 1000);

            // Event delegation - listen on document for delete button clicks
            document.addEventListener('click', async (e) => {
                // Test: Log ALL clicks to see if event delegation is working
                if (e.target.classList.contains('btn-delete')) {
                    console.log('🔴 CLICKED DELETE BUTTON:', e.target);
                }

                // Check if clicked element is a delete button in admin or staff list
                if (e.target.classList.contains('btn-delete')) {
                    console.log('Delete button clicked!');

                    const adminItem = e.target.closest('.admin-item');
                    const staffItem = e.target.closest('.staff-item');

                    console.log('Item context:', { adminItem: !!adminItem, staffItem: !!staffItem });

                    if (adminItem || staffItem) {
                        const itemId = e.target.getAttribute('data-id');
                        const itemType = e.target.getAttribute('data-type') || 'staff';

                        console.log('Delete attempt:', { itemId, itemType });

                        if (!itemId) {
                            console.log('No itemId found, cancelling delete');
                            return;
                        }

                        e.preventDefault();
                        e.stopPropagation();

                        const itemText = adminItem ? 'Website Administrator' : 'Staff Member';
                        console.log('Showing confirmation for:', itemText);

                        const confirmed = await showConfirmModal({
                            title: `Remove ${itemText}`,
                            message: `Are you sure you want to remove this ${itemText.toLowerCase()}? This action cannot be undone.`,
                            confirmText: 'Remove',
                            cancelText: 'Cancel',
                            type: 'warning',
                            confirmButtonType: 'danger'
                        });

                        console.log('User confirmed deletion:', confirmed);

                        if (confirmed) {
                            const targetItem = adminItem || staffItem;

                            try {
                                // Show loading state
                                targetItem.classList.add('admin-loading');

                                // Prepare request body based on item type
                                const requestBody = adminItem ? {
                                    'website-admin': itemId,
                                    action: 'delete'
                                } : {
                                    'staff-member': itemId,
                                    action: 'delete'
                                };

                                console.log('Sending delete request:', requestBody);

                                const response = await fetch('/admin', {
                                    method: 'POST',
                                    headers: {
                                        'Content-Type': 'application/json',
                                    },
                                    body: JSON.stringify(requestBody)
                                });

                                console.log('Server response:', response.status, response.ok);

                                if (response.ok) {
                                    console.log('Delete successful, removing element');
                                    targetItem.remove();
                                } else {
                                    console.error('Server returned error:', response.status);
                                    targetItem.classList.remove('admin-loading');
                                }
                            } catch (error) {
                                console.error(`Error deleting ${itemText.toLowerCase()}:`, error);
                                targetItem.classList.remove('admin-loading');
                            }
                        }
                    } else {
                        console.log('Delete button not in admin or staff item');
                    }
                } else {
                    // Reduce console spam - only log delete button clicks
                    if (e.target.classList.contains('btn-delete')) {
                        console.log('Not a delete button');
                    }
                }
            });
        }


        // Admin help modal functionality
        this.setupAdminHelpModal();
        
        // Image upload functionality
        this.setupImageUploads();
        
        // Drag and drop functionality
        this.setupDragAndDrop();

        // Font management functionality
        this.setupFontManagement();
    }

    setupImageUploads() {
        const uploadButtons = document.querySelectorAll('.image-upload-btn');
        const heroButton = document.querySelector('.hero-upload-btn');
        
        uploadButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                
                // Handle hero upload button differently since it's not in an image-container
                const imageKey = button.getAttribute('data-image-key');
                if (imageKey === 'hero') {
                    const heroUpload = button.closest('.hero-image-upload');
                    const fileInput = heroUpload.querySelector('.image-upload-input');
                    if (fileInput) {
                        fileInput.click();
                    }
                    return;
                }
                
                const container = button.closest('.image-container');
                const fileInput = container.querySelector('.image-upload-input');
                
                if (fileInput) {
                    fileInput.click();
                }
            });
        });

        const fileInputs = document.querySelectorAll('.image-upload-input');
        
        fileInputs.forEach(input => {
            input.addEventListener('change', async (e) => {
                const file = e.target.files[0];
                if (!file) return;

                // Get image key from container or hero upload button
                let container = input.closest('.image-container');
                let imageKey;
                
                if (container) {
                    imageKey = container.getAttribute('data-image-key');
                } else {
                    // Check if it's the hero upload
                    const heroUpload = input.closest('.hero-image-upload');
                    if (heroUpload) {
                        const heroButton = heroUpload.querySelector('.image-upload-btn[data-image-key]');
                        imageKey = heroButton ? heroButton.getAttribute('data-image-key') : null;
                        container = heroUpload; // Use hero upload as container for upload function
                    }
                }
                
                if (!imageKey) {
                    console.error('No image key found');
                    return;
                }

                // Validate file type
                const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
                if (!allowedTypes.includes(file.type)) {
                    alert('Please select a valid image file (JPEG, PNG, GIF, or WebP)');
                    return;
                }

                // Validate file size (max 5MB)
                if (file.size > 5 * 1024 * 1024) {
                    alert('File size must be less than 5MB');
                    return;
                }

                await this.uploadImage(container, imageKey, file);
                
                // Clear the input
                input.value = '';
            });
        });
    }

    async uploadImage(container, imageKey, file) {
        const img = container.querySelector('img');
        const originalSrc = img ? img.src : 'N/A (no img element)';
        
        try {
            // Add uploading class for visual feedback
            container.classList.add('image-uploading');
            
            // Create form data
            const formData = new FormData();
            formData.append('image', file);
            formData.append('image_key', imageKey);
            
            // Upload the image
            const response = await fetch('/api/upload-image', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (response.ok && result.success) {
                
                // Use server timestamp for more reliable cache busting
                const cacheBuster = result.timestamp || new Date().getTime();
                
                // Add a small delay to ensure file system is updated
                setTimeout(() => {
                    // Update all instances of this image on the page
                    this.updateImageInstances(imageKey, result.filename, cacheBuster);
                    
                    // Show success notification with cache clearing instructions
                    alert('Image updated successfully! If you don\'t see changes after refreshing, clear your browser cache (Ctrl+F5 or Cmd+Shift+R).');
                }, 100);
                
            } else {
                throw new Error(result.error || 'Upload failed');
            }
            
        } catch (error) {
            console.error('Error uploading image:', error);
            alert('Failed to upload image: ' + error.message);
            
        } finally {
            // Remove uploading class
            container.classList.remove('image-uploading');
        }
    }

    updateImageInstances(imageKey, filename, cacheBuster) {
        // Handle hero background image specially since it's CSS background
        if (imageKey === 'hero') {
            this.updateHeroBackground(filename, cacheBuster);
            return;
        }

        // Map of image keys to their possible selectors
        const imageSelectors = {
            'logo': [
                'img[src*="mayday-translucent"]',
                '.nav-logo img',
                '.footer-logo img'
            ],
            'headshot': [
                'img[src*="headshot"]',
                'img[alt*="Nathan"]'
            ],
            'family': [
                'img[src*="family"]',
                'img[alt*="Amanda"]'
            ],
            'benny': [
                'img[src*="benny"]',
                'img[alt*="Benny"]',
                '.admin-mascot'
            ],
            'about1': [
                'img[src*="headshot"]',
                'img[alt*="About Image 1"]',
                '.image-container[data-image-key="about1"] img'
            ],
            'about2': [
                'img[src*="family"]',
                'img[alt*="About Image 2"]',
                '.image-container[data-image-key="about2"] img'
            ],
            'about3': [
                'img[src*="benny"]',
                'img[alt*="About Image 3"]',
                '.image-container[data-image-key="about3"] img'
            ]
        };

        const selectors = imageSelectors[imageKey] || [`img[src*="${filename}"]`];
        
        selectors.forEach(selector => {
            const images = document.querySelectorAll(selector);
            images.forEach(img => {
                const currentSrc = img.src;
                const baseSrc = currentSrc.split('?')[0];
                const newSrc = `${baseSrc}?v=${cacheBuster}`;

                console.log(`Updating image: ${selector} from ${currentSrc} to ${newSrc}`);

                // Create new image element to ensure fresh load
                const newImg = new Image();
                newImg.onload = function() {
                    // Replace the src after the new image has loaded
                    img.src = newSrc;
                    console.log(`Successfully updated image: ${newSrc}`);
                };
                newImg.onerror = function() {
                    console.error(`Failed to load updated image: ${newSrc}`);
                };
                newImg.src = newSrc;
            });
        });
    }

    updateHeroBackground(filename, cacheBuster) {
        // Update the CSS background image for hero section
        const heroSection = document.querySelector('.hero-section');
        if (heroSection) {
            const newBackgroundUrl = `/static/img/${filename}?v=${cacheBuster}`;
            
            // Use setProperty with !important to override CSS
            heroSection.style.setProperty('background-image', `url('${newBackgroundUrl}')`, 'important');
            heroSection.style.setProperty('background-size', 'cover', 'important');
            heroSection.style.setProperty('background-position', 'center', 'important');
            heroSection.style.setProperty('background-repeat', 'no-repeat', 'important');
            heroSection.style.setProperty('background-attachment', 'scroll', 'important');
            
            
            // Preload the image to ensure it's loaded
            const img = new Image();
            img.onload = function() {
                // Force a repaint by temporarily changing a property
                heroSection.style.transform = 'translateZ(0)';
                setTimeout(() => {
                    heroSection.style.transform = '';
                }, 10);
            };
            img.onerror = function() {
                console.error(`Failed to load hero background: ${newBackgroundUrl}`);
            };
            img.src = newBackgroundUrl;
        } else {
            console.error('Hero section not found');
        }
    }

    setupServiceManagement() {
        // Service modal elements
        const serviceModal = document.getElementById('serviceModal');
        const serviceForm = document.getElementById('serviceForm');
        const addServiceItem = document.querySelector('.add-service-item');
        const serviceModalClose = document.getElementById('serviceModalClose');
        const saveServiceBtn = document.getElementById('saveService');
        const cancelServiceBtn = document.getElementById('cancelService');
        const selectedIcon = document.getElementById('selectedIcon');
        const iconGrid = document.getElementById('iconGrid');
        const serviceIconValue = document.getElementById('serviceIconValue');

        if (!serviceModal) return;

        // Add new service
        if (addServiceItem) {
            addServiceItem.addEventListener('click', () => {
                this.openServiceModal();
            });
        }

        // Edit service buttons
        document.addEventListener('click', (e) => {
            if (e.target.closest('.btn-edit-service')) {
                const serviceItem = e.target.closest('.service-list-item');
                const serviceId = serviceItem.dataset.serviceId;
                this.openServiceModal(serviceId);
            }
        });

        // Delete service buttons
        document.addEventListener('click', async (e) => {
            if (e.target.closest('.btn-delete-service')) {
                const serviceItem = e.target.closest('.service-list-item');
                const serviceId = serviceItem.dataset.serviceId;
                const serviceName = serviceItem.querySelector('h3').textContent;
                
                const confirmed = await showConfirmModal({
                    title: 'Delete Service',
                    message: `Are you sure you want to delete "${serviceName}"?`,
                    confirmText: 'Delete',
                    type: 'danger',
                    confirmButtonType: 'danger'
                });
                
                if (confirmed) {
                    // Show loading state on the service item
                    serviceItem.classList.add('admin-loading');
                    await this.deleteService(serviceId);
                }
            }
        });

        // Modal close events
        serviceModalClose?.addEventListener('click', () => this.closeServiceModal());
        cancelServiceBtn?.addEventListener('click', () => this.closeServiceModal());
        
        // Click outside modal to close
        serviceModal?.addEventListener('click', (e) => {
            if (e.target === serviceModal) {
                this.closeServiceModal();
            }
        });

        // Icon selector
        selectedIcon?.addEventListener('click', () => {
            iconGrid.style.display = iconGrid.style.display === 'none' ? 'grid' : 'none';
        });

        // Icon selection
        document.addEventListener('click', (e) => {
            if (e.target.closest('.icon-option')) {
                const iconOption = e.target.closest('.icon-option');
                const iconClass = iconOption.dataset.icon;
                const iconName = iconOption.querySelector('span').textContent;
                
                // Update selected icon display
                selectedIcon.querySelector('i').className = iconClass;
                selectedIcon.querySelector('span').textContent = iconName;
                
                // Update hidden input
                serviceIconValue.value = iconClass;
                
                // Hide icon grid
                iconGrid.style.display = 'none';
                
                // Update selection state
                document.querySelectorAll('.icon-option').forEach(opt => opt.classList.remove('selected'));
                iconOption.classList.add('selected');
            }
        });

        // Save service
        saveServiceBtn?.addEventListener('click', async () => {
            await this.saveService();
        });
    }

    async openServiceModal(serviceId = null) {
        const modal = document.getElementById('serviceModal');
        const form = document.getElementById('serviceForm');
        const title = document.getElementById('serviceModalTitle');
        
        // Reset form
        form.reset();
        document.getElementById('serviceIconValue').value = 'fas fa-search';
        document.getElementById('selectedIcon').querySelector('i').className = 'fas fa-search';
        document.getElementById('selectedIcon').querySelector('span').textContent = 'Click to select icon';
        
        if (serviceId) {
            // Edit mode
            title.textContent = 'Edit Service';
            await this.loadServiceData(serviceId);
        } else {
            // Add mode
            title.textContent = 'Add New Service';
        }
        
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }

    async loadServiceData(serviceId) {
        try {
            const response = await fetch('/api/services');
            const data = await response.json();
            const service = data.services.find(s => s.id == serviceId);
            
            if (service) {
                document.getElementById('serviceId').value = service.id;
                document.getElementById('serviceTitle').value = service.title;
                document.getElementById('serviceDescription').value = service.description;
                document.getElementById('serviceIconValue').value = service.icon;
                
                // Update icon display
                const selectedIcon = document.getElementById('selectedIcon');
                selectedIcon.querySelector('i').className = service.icon;
                const iconOption = document.querySelector(`[data-icon="${service.icon}"]`);
                if (iconOption) {
                    selectedIcon.querySelector('span').textContent = iconOption.querySelector('span').textContent;
                }
            }
        } catch (error) {
            console.error('Error loading service data:', error);
        }
    }

    closeServiceModal() {
        const modal = document.getElementById('serviceModal');
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
        document.getElementById('iconGrid').style.display = 'none';
    }

    async saveService() {
        const form = document.getElementById('serviceForm');
        const formData = new FormData(form);
        const serviceId = document.getElementById('serviceId').value;
        const saveButton = document.getElementById('saveService');
        
        const data = {
            action: serviceId ? 'update' : 'create',
            title: formData.get('serviceTitle'),
            description: formData.get('serviceDescription'),
            icon: formData.get('serviceIcon')
        };
        
        if (serviceId) {
            data.id = parseInt(serviceId);
        }
        
        try {
            // Show loading state
            saveButton.classList.add('loading');
            saveButton.disabled = true;
            
            const response = await fetch('/api/services', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            if (result.success) {
                this.closeServiceModal();
                location.reload(); // Refresh to show changes
            } else {
                alert('Error saving service');
            }
        } catch (error) {
            console.error('Error saving service:', error);
            alert('Error saving service');
        } finally {
            // Hide loading state
            saveButton.classList.remove('loading');
            saveButton.disabled = false;
        }
    }

    async deleteService(serviceId) {
        try {
            const response = await fetch('/api/services', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    action: 'delete',
                    id: parseInt(serviceId)
                })
            });
            
            const result = await response.json();
            if (result.success) {
                location.reload(); // Refresh to show changes
            } else {
                alert('Error deleting service');
            }
        } catch (error) {
            console.error('Error deleting service:', error);
            alert('Error deleting service');
        }
    }

    setupFAQManagement() {
        // FAQ modal elements
        const faqModal = document.getElementById('faqModal');
        const faqForm = document.getElementById('faqForm');
        const addFaqItem = document.querySelector('.add-faq-item');
        const faqModalClose = document.getElementById('faqModalClose');
        const saveFaqBtn = document.getElementById('saveFaq');
        const cancelFaqBtn = document.getElementById('cancelFaq');

        if (!faqModal) return;

        // Add new FAQ
        if (addFaqItem) {
            addFaqItem.addEventListener('click', () => {
                this.openFaqModal();
            });
        }

        // Edit FAQ buttons
        document.addEventListener('click', (e) => {
            if (e.target.closest('.btn-edit-faq')) {
                const faqItem = e.target.closest('.faq-item');
                const faqId = faqItem.dataset.faqId;
                this.openFaqModal(faqId);
            }
        });

        // Delete FAQ buttons
        document.addEventListener('click', async (e) => {
            if (e.target.closest('.btn-delete-faq')) {
                const faqItem = e.target.closest('.faq-item');
                const faqId = faqItem.dataset.faqId;
                const question = faqItem.querySelector('h3').textContent;
                
                const confirmed = await showConfirmModal({
                    title: 'Delete FAQ',
                    message: `Are you sure you want to delete "${question}"?`,
                    confirmText: 'Delete',
                    type: 'danger',
                    confirmButtonType: 'danger'
                });
                
                if (confirmed) {
                    // Show loading state on the FAQ item
                    faqItem.classList.add('admin-loading');
                    await this.deleteFaq(faqId);
                }
            }
        });

        // Modal close events
        faqModalClose?.addEventListener('click', () => this.closeFaqModal());
        cancelFaqBtn?.addEventListener('click', () => this.closeFaqModal());
        
        // Click outside modal to close
        faqModal?.addEventListener('click', (e) => {
            if (e.target === faqModal) {
                this.closeFaqModal();
            }
        });

        // Save FAQ
        saveFaqBtn?.addEventListener('click', async () => {
            await this.saveFaq();
        });
        
        // FAQ Pagination - Load More functionality
        this.setupFAQPagination();
    }
    
    setupFAQPagination() {
        const loadMoreBtn = document.getElementById('loadMoreFaqs');
        if (!loadMoreBtn) return;
        
        this.faqOffset = 5; // We already show first 5
        
        loadMoreBtn.addEventListener('click', async () => {
            await this.loadMoreFAQs();
        });
    }
    
    async loadMoreFAQs() {
        const loadMoreBtn = document.getElementById('loadMoreFaqs');
        const faqGrid = document.getElementById('faqGrid');
        
        if (!loadMoreBtn || !faqGrid) return;
        
        try {
            // Show loading state
            loadMoreBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
            loadMoreBtn.disabled = true;
            loadMoreBtn.classList.add('loading');
            
            // Check if we're in admin mode
            const isAdmin = document.querySelector('.add-faq-item') !== null;
            const adminParam = isAdmin ? '&admin=true' : '';
            
            // Fetch more FAQs
            const response = await fetch(`/api/faqs?limit=5&offset=${this.faqOffset}${adminParam}`);
            const data = await response.json();
            
            if (data.faqs && data.faqs.length > 0) {
                // Add new FAQs to the grid
                data.faqs.forEach(faq => {
                    const faqItem = this.createFAQElement(faq);
                    // Insert before the add button or load more button
                    const addButton = faqGrid.querySelector('.add-faq-item');
                    const loadMoreContainer = loadMoreBtn.closest('.faq-load-more');
                    const insertBefore = addButton || loadMoreContainer;
                    if (insertBefore) {
                        faqGrid.insertBefore(faqItem, insertBefore);
                    } else {
                        faqGrid.appendChild(faqItem);
                    }
                });
                
                // Trigger animation for new elements
                setTimeout(() => {
                    this.observeAnimationElements();
                }, 100);
                
                this.faqOffset += 5;
                
                // Check if there are more FAQs to load
                if (data.faqs.length < 5) {
                    // No more FAQs, hide the load more button
                    loadMoreBtn.closest('.faq-load-more').style.display = 'none';
                } else {
                    // Reset button state
                    loadMoreBtn.innerHTML = '<i class="fas fa-chevron-down"></i> Load More FAQs';
                    loadMoreBtn.disabled = false;
                    loadMoreBtn.classList.remove('loading');
                }
            } else {
                // No more FAQs, hide the load more button
                loadMoreBtn.closest('.faq-load-more').style.display = 'none';
            }
        } catch (error) {
            console.error('Error loading more FAQs:', error);
            loadMoreBtn.innerHTML = '<i class="fas fa-chevron-down"></i> Load More FAQs';
            loadMoreBtn.disabled = false;
            loadMoreBtn.classList.remove('loading');
        }
    }
    
    createFAQElement(faq) {
        const faqItem = document.createElement('div');
        faqItem.className = 'faq-item';
        faqItem.dataset.faqId = faq.id;
        
        const isAdmin = document.querySelector('.add-faq-item') !== null; // Check if admin tools are present
        
        if (isAdmin) {
            faqItem.draggable = true;
        }
        
        faqItem.innerHTML = `
            ${isAdmin ? `<div class="drag-handle"><i class="fas fa-grip-vertical"></i></div>` : ''}
            <h3>${faq.question}</h3>
            <div class="faq-answer">
                <p>${faq.answer}</p>
            </div>
            ${isAdmin ? `
            <div class="admin-actions">
                <button class="btn-edit-faq" title="Edit FAQ">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn-delete-faq" title="Delete FAQ">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
            ` : ''}
        `;
        
        // Add drag listeners if in admin mode - add to the element itself
        if (isAdmin) {
            faqItem.addEventListener('dragstart', (e) => {
                faqItem.classList.add('dragging');
                e.dataTransfer.effectAllowed = 'move';
            });
            
            faqItem.addEventListener('dragend', (e) => {
                faqItem.classList.remove('dragging');
            });
            
            faqItem.setAttribute('data-drag-listeners', 'true');
        }
        
        // No need to add individual click handlers - event delegation handles this
        return faqItem;
    }

    async openFaqModal(faqId = null) {
        const modal = document.getElementById('faqModal');
        const form = document.getElementById('faqForm');
        const title = document.getElementById('faqModalTitle');
        
        // Reset form
        form.reset();
        
        if (faqId) {
            // Edit mode
            title.textContent = 'Edit FAQ';
            await this.loadFaqData(faqId);
        } else {
            // Add mode
            title.textContent = 'Add New FAQ';
        }
        
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }

    async loadFaqData(faqId) {
        try {
            const response = await fetch('/api/faqs');
            const data = await response.json();
            const faq = data.faqs.find(f => f.id == faqId);
            
            if (faq) {
                document.getElementById('faqId').value = faq.id;
                document.getElementById('faqQuestion').value = faq.question;
                document.getElementById('faqAnswer').value = faq.answer;
            }
        } catch (error) {
            console.error('Error loading FAQ data:', error);
        }
    }

    closeFaqModal() {
        const modal = document.getElementById('faqModal');
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }

    async saveFaq() {
        const form = document.getElementById('faqForm');
        const formData = new FormData(form);
        const faqId = document.getElementById('faqId').value;
        const saveButton = document.getElementById('saveFaq');
        
        const data = {
            action: faqId ? 'update' : 'create',
            question: formData.get('faqQuestion'),
            answer: formData.get('faqAnswer')
        };
        
        if (faqId) {
            data.id = parseInt(faqId);
        }
        
        try {
            // Show loading state
            saveButton.classList.add('loading');
            saveButton.disabled = true;
            
            const response = await fetch('/api/faqs', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            if (result.success) {
                this.closeFaqModal();
                location.reload(); // Refresh to show changes
            } else {
                alert('Error saving FAQ');
            }
        } catch (error) {
            console.error('Error saving FAQ:', error);
            alert('Error saving FAQ');
        } finally {
            // Hide loading state
            saveButton.classList.remove('loading');
            saveButton.disabled = false;
        }
    }

    async deleteFaq(faqId) {
        try {
            const response = await fetch('/api/faqs', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    action: 'delete',
                    id: parseInt(faqId)
                })
            });
            
            const result = await response.json();
            if (result.success) {
                location.reload(); // Refresh to show changes
            } else {
                alert('Error deleting FAQ');
            }
        } catch (error) {
            console.error('Error deleting FAQ:', error);
            alert('Error deleting FAQ');
        }
    }

    setupAnimations() {
        // Add CSS for animations
        const style = document.createElement('style');
        style.textContent = `
            /* Elements are visible by default */
            .service-card,
            .feature-box,
            .faq-item,
            .content-panel {
                opacity: 1;
                transform: translateY(0);
                transition: opacity 0.6s ease, transform 0.6s ease;
            }
            
            /* Animation effect when coming into view */
            .service-card.animate-in,
            .feature-box.animate-in,
            .faq-item.animate-in,
            .content-panel.animate-in {
                animation: fadeInUp 0.6s ease-out;
            }
            
            .hero-content {
                animation: fadeInUp 1s ease-out;
            }
            
            @keyframes fadeInUp {
                from {
                    opacity: 0;
                    transform: translateY(30px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            
            .nav-menu.active {
                animation: slideIn 0.3s ease-out;
            }
            
            @keyframes slideIn {
                from {
                    opacity: 0;
                    transform: translateX(-100%);
                }
                to {
                    opacity: 1;
                    transform: translateX(0);
                }
            }
            
            /* Loading skeleton styles */
            .loading-placeholder {
                opacity: 1;
            }
            
            .faq-item-skeleton {
                margin-bottom: 1.5rem;
                padding: 1rem;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                background: #f9fafb;
            }
            
            .skeleton-title, .skeleton-content {
                background: #e5e7eb;
                border-radius: 4px;
                animation: pulse 1.5s ease-in-out infinite;
            }
            
            .skeleton-title {
                height: 24px;
                width: 70%;
                margin-bottom: 0.75rem;
            }
            
            .skeleton-content {
                height: 60px;
                width: 100%;
            }
            
            @keyframes pulse {
                0% {
                    opacity: 1;
                }
                50% {
                    opacity: 0.5;
                }
                100% {
                    opacity: 1;
                }
            }
            
            /* Image upload styling */
            .image-container {
                position: relative;
                display: inline-block;
            }
            
            .image-upload-btn {
                position: absolute;
                top: 8px;
                right: 8px;
                background: var(--secondary-color);
                color: white;
                border: none;
                border-radius: 50%;
                width: 36px;
                height: 36px;
                cursor: pointer;
                font-size: 14px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.2);
                transition: all 0.3s ease;
                z-index: 10;
            }
            
            .image-upload-btn:hover {
                background: var(--primary-color);
                transform: scale(1.1);
            }
            
            .image-upload-btn i {
                pointer-events: none;
            }
            
            /* Upload progress overlay */
            .image-uploading {
                position: relative;
            }
            
            .image-uploading::after {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0,0,0,0.7);
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: inherit;
            }
            
            .image-uploading::before {
                content: '\\f1ce';
                font-family: 'Font Awesome 6 Free';
                font-weight: 900;
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                color: white;
                font-size: 24px;
                z-index: 11;
                animation: spin 1s linear infinite;
            }
            
            @keyframes spin {
                0% { transform: translate(-50%, -50%) rotate(0deg); }
                100% { transform: translate(-50%, -50%) rotate(360deg); }
            }
            
            /* Hero image upload specific styling */
            .hero-image-upload {
                position: fixed !important;
                top: 80px !important;
                right: 20px !important;
                z-index: 1000 !important;
                pointer-events: auto !important;
            }
            
            .hero-upload-btn {
                background: rgba(255, 255, 255, 0.95) !important;
                color: var(--primary-color) !important;
                border: 3px solid var(--primary-color) !important;
                position: relative !important;
                z-index: 1001 !important;
                width: 48px !important;
                height: 48px !important;
                font-size: 18px !important;
                box-shadow: 0 6px 16px rgba(0, 0, 0, 0.4) !important;
                border-radius: 50% !important;
                cursor: pointer !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
            }
            
            .hero-upload-btn:hover {
                background: var(--primary-color) !important;
                color: white !important;
                transform: scale(1.1) !important;
            }
            
            /* Ensure hero overlay doesn't interfere */
            .hero-overlay {
                z-index: 1 !important;
            }
            
            .hero-content {
                z-index: 10 !important;
            }
        `;
        document.head.appendChild(style);
    }

    showLoadingOverlay() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.style.display = 'flex';
        }
    }

    hideLoadingOverlay() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.style.display = 'none';
        }
    }

    handleScroll() {
        // Update active navigation based on scroll position
        const sections = document.querySelectorAll('section[id]');
        const navbarHeight = document.querySelector('.navbar').offsetHeight;
        
        let currentSection = 'home';
        
        sections.forEach(section => {
            const rect = section.getBoundingClientRect();
            if (rect.top <= navbarHeight + 100 && rect.bottom >= navbarHeight + 100) {
                currentSection = section.id;
            }
        });
        
        this.updateActiveNavLink(currentSection);
    }

    handleResize() {
        // Handle responsive adjustments
        const navMenu = document.querySelector('.nav-menu');
        const navToggle = document.querySelector('.nav-toggle');
        if (window.innerWidth > 768) {
            if (navMenu) {
                navMenu.classList.remove('active');
            }
            if (navToggle) {
                navToggle.classList.remove('active');
            }
        }
    }

    // Utility functions
    throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        }
    }

    debounce(func, wait) {
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

    // Async content loading methods
    async loadAsyncContent() {
        // Load Google rating and reviews concurrently for better performance
        try {
            const [ratingResult, reviewsResult] = await Promise.allSettled([
                this.loadGoogleRating(),
                this.loadGoogleReviews()
            ]);
            
            // Log any failures for debugging
            if (ratingResult.status === 'rejected') {
                console.error('Google rating loading failed:', ratingResult.reason);
            }
            if (reviewsResult.status === 'rejected') {
                console.error('Google reviews loading failed:', reviewsResult.reason);
            }
        } catch (error) {
            console.error('Error in concurrent async content loading:', error);
        }
    }

    async loadGoogleRating() {
        try {
            const response = await fetch('/api/google-rating');
            if (response.ok) {
                const data = await response.json();
                // Cache the rating data for use in the reviews widget
                this.cachedGoogleRating = data;
                this.updateGoogleRating(data);
            } else {
                console.error('Failed to load Google rating:', response.status);
                this.showGoogleRatingError();
            }
        } catch (error) {
            console.error('Error loading Google rating:', error);
            this.showGoogleRatingError();
        }
    }

    updateGoogleRating(data) {
        const ratingElement = document.getElementById('google-rating');
        if (!ratingElement) return;

        if (data.rating) {
            const rating = data.rating;
            const fullStars = Math.floor(rating);
            const hasHalfStar = (rating - fullStars) >= 0.5;
            const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);

            let starsHTML = '';
            
            // Full stars
            for (let i = 0; i < fullStars; i++) {
                starsHTML += '<i class="fas fa-star"></i>';
            }
            
            // Half star
            if (hasHalfStar) {
                starsHTML += '<i class="fas fa-star-half-alt"></i>';
            }
            
            // Empty stars
            for (let i = 0; i < emptyStars; i++) {
                starsHTML += '<i class="far fa-star"></i>';
            }

            const reviewText = data.review_count > 0 
                ? `${rating.toFixed(1)} Google Reviews (${data.review_count})`
                : `${rating.toFixed(1)} Google Reviews`;

            const newHTML = starsHTML + `<span>${reviewText}</span>`;
            ratingElement.innerHTML = newHTML;
        } else {
            this.showGoogleRatingError();
        }
    }

    showGoogleRatingError() {
        const ratingElement = document.getElementById('google-rating');
        if (ratingElement) {
            ratingElement.innerHTML = `
                <i class="fas fa-star" style="color: #fbbf24;"></i>
                <i class="far fa-star"></i>
                <i class="far fa-star"></i>
                <i class="far fa-star"></i>
                <i class="far fa-star"></i>
                <span>Google Reviews</span>
            `;
        }
    }

    async loadGoogleReviews() {
        try {
            const response = await fetch('/api/google-reviews');
            if (response.ok) {
                const data = await response.json();
                this.initGoogleReviewsWidget(data);
            } else {
                console.error('Failed to load Google reviews:', response.status);
                this.showGoogleReviewsError();
            }
        } catch (error) {
            console.error('Error loading Google reviews:', error);
            this.showGoogleReviewsError();
        }
    }

    initGoogleReviewsWidget(data) {
        const reviews = data.reviews || [];
        if (reviews.length === 0) {
            this.showNoReviewsMessage();
            return;
        }

        // Store reviews for rotation
        this.reviews = reviews;
        this.currentReviewIndex = 0;
        
        // Use cached Google rating if available, otherwise load it
        if (this.cachedGoogleRating) {
            this.updateWidgetRatingSummary(this.cachedGoogleRating.rating, this.cachedGoogleRating.review_count);
        } else {
            this.loadGoogleRatingForWidget();
        }
        
        // Display first review
        this.displayReview(0);
        
        // Setup navigation
        this.setupReviewNavigation();
        
        // Start automatic rotation if we have multiple reviews
        if (reviews.length > 1) {
            this.startReviewRotation();
        }
    }

    async loadGoogleRatingForWidget() {
        try {
            const response = await fetch('/api/google-rating');
            if (response.ok) {
                const data = await response.json();
                if (data.rating && data.review_count) {
                    this.updateWidgetRatingSummary(data.rating, data.review_count);
                } else {
                    // Fallback to reviews-based calculation
                    this.updateWidgetRatingSummaryFromReviews();
                }
            } else {
                this.updateWidgetRatingSummaryFromReviews();
            }
        } catch (error) {
            console.error('Error loading Google rating for widget:', error);
            this.updateWidgetRatingSummaryFromReviews();
        }
    }

    updateWidgetRatingSummary(rating, reviewCount) {
        const widgetRatingStars = document.getElementById('widget-rating-stars');
        const widgetRatingText = document.getElementById('widget-rating-text');
        
        if (!widgetRatingStars || !widgetRatingText) return;

        // Generate stars HTML
        const fullStars = Math.floor(rating);
        const hasHalfStar = (rating - fullStars) >= 0.5;
        const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);

        let starsHTML = '';
        
        // Full stars
        for (let i = 0; i < fullStars; i++) {
            starsHTML += '<i class="fas fa-star"></i>';
        }
        
        // Half star
        if (hasHalfStar) {
            starsHTML += '<i class="fas fa-star-half-alt"></i>';
        }
        
        // Empty stars
        for (let i = 0; i < emptyStars; i++) {
            starsHTML += '<i class="far fa-star"></i>';
        }

        widgetRatingStars.innerHTML = starsHTML;
        widgetRatingText.textContent = `${rating.toFixed(1)} (${reviewCount} reviews)`;
    }

    updateWidgetRatingSummaryFromReviews() {
        if (!this.reviews || this.reviews.length === 0) return;
        
        const widgetRatingStars = document.getElementById('widget-rating-stars');
        const widgetRatingText = document.getElementById('widget-rating-text');
        
        if (!widgetRatingStars || !widgetRatingText) return;

        // Calculate average rating from available reviews (fallback)
        const totalRating = this.reviews.reduce((sum, review) => sum + review.rating, 0);
        const avgRating = totalRating / this.reviews.length;
        
        // Generate stars HTML
        const fullStars = Math.floor(avgRating);
        const hasHalfStar = (avgRating - fullStars) >= 0.5;
        const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);

        let starsHTML = '';
        
        // Full stars
        for (let i = 0; i < fullStars; i++) {
            starsHTML += '<i class="fas fa-star"></i>';
        }
        
        // Half star
        if (hasHalfStar) {
            starsHTML += '<i class="fas fa-star-half-alt"></i>';
        }
        
        // Empty stars
        for (let i = 0; i < emptyStars; i++) {
            starsHTML += '<i class="far fa-star"></i>';
        }

        widgetRatingStars.innerHTML = starsHTML;
        widgetRatingText.textContent = `${avgRating.toFixed(1)} (${this.reviews.length} reviews shown)`;
    }

    displayReview(index) {
        const currentReviewEl = document.getElementById('current-review');
        if (!currentReviewEl || !this.reviews || !this.reviews[index]) return;

        const review = this.reviews[index];
        this.currentReviewIndex = index;

        // Generate stars for this review
        let starsHTML = '';
        for (let i = 0; i < review.rating; i++) {
            starsHTML += '<i class="fas fa-star"></i>';
        }
        for (let i = review.rating; i < 5; i++) {
            starsHTML += '<i class="far fa-star"></i>';
        }

        // Get initials for avatar
        const initials = review.author.split(' ').map(name => name[0]).join('').toUpperCase();

        // Display review with smooth transition
        currentReviewEl.style.opacity = '0';
        
        setTimeout(() => {
            currentReviewEl.innerHTML = `
                <div class="review-header">
                    <div class="review-author">
                        <div class="review-avatar">${initials}</div>
                        <div class="review-author-info">
                            <p class="review-author-name">${review.author}</p>
                            <p class="review-time">${review.relative_time}</p>
                        </div>
                    </div>
                    <div class="review-rating">
                        ${starsHTML}
                    </div>
                </div>
                <p class="review-text">${review.text}</p>
            `;
            
            currentReviewEl.style.opacity = '1';
        }, 150);

        // Update indicators
        this.updateReviewIndicators();
        
        // Update navigation buttons
        this.updateNavigationButtons();
    }

    setupReviewNavigation() {
        const prevBtn = document.getElementById('prev-review');
        const nextBtn = document.getElementById('next-review');
        const indicatorsContainer = document.getElementById('review-indicators');

        if (!this.reviews || this.reviews.length <= 1) {
            // Hide navigation if only one review
            if (prevBtn) prevBtn.style.display = 'none';
            if (nextBtn) nextBtn.style.display = 'none';
            if (indicatorsContainer) indicatorsContainer.style.display = 'none';
            return;
        }

        // Create indicators
        if (indicatorsContainer) {
            indicatorsContainer.innerHTML = '';
            for (let i = 0; i < this.reviews.length; i++) {
                const indicator = document.createElement('div');
                indicator.className = `review-indicator ${i === 0 ? 'active' : ''}`;
                indicator.addEventListener('click', () => {
                    this.stopReviewRotation();
                    this.displayReview(i);
                    this.startReviewRotation();
                });
                indicatorsContainer.appendChild(indicator);
            }
        }

        // Previous button
        if (prevBtn) {
            prevBtn.addEventListener('click', () => {
                this.stopReviewRotation();
                const prevIndex = this.currentReviewIndex > 0 ? this.currentReviewIndex - 1 : this.reviews.length - 1;
                this.displayReview(prevIndex);
                this.startReviewRotation();
            });
        }

        // Next button
        if (nextBtn) {
            nextBtn.addEventListener('click', () => {
                this.stopReviewRotation();
                const nextIndex = this.currentReviewIndex < this.reviews.length - 1 ? this.currentReviewIndex + 1 : 0;
                this.displayReview(nextIndex);
                this.startReviewRotation();
            });
        }
    }

    updateReviewIndicators() {
        const indicators = document.querySelectorAll('.review-indicator');
        indicators.forEach((indicator, index) => {
            indicator.classList.toggle('active', index === this.currentReviewIndex);
        });
    }

    updateNavigationButtons() {
        const prevBtn = document.getElementById('prev-review');
        const nextBtn = document.getElementById('next-review');
        
        if (prevBtn) prevBtn.disabled = false;
        if (nextBtn) nextBtn.disabled = false;
    }

    startReviewRotation() {
        if (!this.reviews || this.reviews.length <= 1) return;
        
        this.stopReviewRotation(); // Clear any existing rotation
        
        this.reviewRotationInterval = setInterval(() => {
            const nextIndex = this.currentReviewIndex < this.reviews.length - 1 ? this.currentReviewIndex + 1 : 0;
            this.displayReview(nextIndex);
        }, 10000); // 10 seconds
    }

    stopReviewRotation() {
        if (this.reviewRotationInterval) {
            clearInterval(this.reviewRotationInterval);
            this.reviewRotationInterval = null;
        }
    }

    showNoReviewsMessage() {
        const currentReviewEl = document.getElementById('current-review');
        const widgetRatingText = document.getElementById('widget-rating-text');
        
        if (currentReviewEl) {
            currentReviewEl.innerHTML = `
                <div class="review-loading">
                    <i class="fas fa-info-circle"></i>
                    <span>No reviews available at this time</span>
                </div>
            `;
        }
        
        // Use cached Google rating if available, otherwise load it
        if (this.cachedGoogleRating) {
            this.updateWidgetRatingSummary(this.cachedGoogleRating.rating, this.cachedGoogleRating.review_count);
        } else {
            this.loadGoogleRatingForWidget();
        }
        
        // Hide navigation
        const navElements = ['prev-review', 'next-review', 'review-indicators'];
        navElements.forEach(id => {
            const element = document.getElementById(id);
            if (element) element.style.display = 'none';
        });
    }

    showGoogleReviewsError() {
        const currentReviewEl = document.getElementById('current-review');
        const widgetRatingText = document.getElementById('widget-rating-text');
        
        if (currentReviewEl) {
            currentReviewEl.innerHTML = `
                <div class="review-loading">
                    <i class="fas fa-exclamation-triangle"></i>
                    <span>Unable to load reviews at this time</span>
                </div>
            `;
        }
        
        if (widgetRatingText) {
            widgetRatingText.textContent = 'Reviews unavailable';
        }
        
        // Hide navigation
        const navElements = ['prev-review', 'next-review', 'review-indicators'];
        navElements.forEach(id => {
            const element = document.getElementById(id);
            if (element) element.style.display = 'none';
        });
    }

    setupDragAndDrop() {
        // Only setup drag and drop in admin mode
        if (!document.querySelector('.admin-actions')) return;
        
        this.setupServiceDragAndDrop();
        this.setupFAQDragAndDrop();
    }
    
    setupServiceDragAndDrop() {
        const servicesGrid = document.getElementById('servicesGrid');
        if (!servicesGrid) return;
        
        // Add event listeners to existing service items
        this.addServiceDragListeners(servicesGrid);
        
        let dragOverTimeout;
        let highlightedTarget = null; // Store which service is currently highlighted
        let dropPosition = null; // Store whether to drop 'before' or 'after' the highlighted target
        
        servicesGrid.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'move';
            
            const dragging = document.querySelector('.dragging');
            if (!dragging) {
                return;
            }
            
            
            // Simple approach: only move the element on drop, not during drag
            // Just provide visual feedback without constantly repositioning
            const services = [...servicesGrid.querySelectorAll('.service-list-item:not(.add-service-item):not(.dragging)')];
            
            // Clear previous indicators
            services.forEach(service => service.classList.remove('drag-over'));
            
            // Find closest service for visual feedback only
            let closest = null;
            let minDistance = Infinity;
            
            services.forEach((service, index) => {
                const rect = service.getBoundingClientRect();
                const centerX = rect.left + rect.width / 2;
                const centerY = rect.top + rect.height / 2;
                const distance = Math.sqrt(Math.pow(e.clientX - centerX, 2) + Math.pow(e.clientY - centerY, 2));
                
                
                if (distance < minDistance) {
                    minDistance = distance;
                    closest = service;
                }
            });
            
            // Add visual feedback to closest service - more generous range and immediate
            if (closest && minDistance < 250) { // Increased range for easier targeting
                const serviceTitle = closest.querySelector('h3')?.textContent || 'Unknown';
                
                closest.classList.add('drag-over');
                highlightedTarget = closest; // Store the highlighted target
                
                // Simple position swap - highlighted tile will be swapped with dragged tile
                const allServices = [...servicesGrid.querySelectorAll('.service-list-item:not(.add-service-item)')];
                const draggedIndex = allServices.indexOf(dragging);
                const targetIndex = allServices.indexOf(closest);
                
                
                // Store target for swap operation
                dropPosition = 'swap'; // Always swap positions
            } else {
                if (closest) {
                } else {
                }
                highlightedTarget = null; // Clear if no target is close enough
                dropPosition = null;
            }
        });
        
        servicesGrid.addEventListener('drop', async (e) => {
            e.preventDefault();
            
            const draggedElement = document.querySelector('.dragging');
            if (!draggedElement) {
                return;
            }
            
            const draggedTitle = draggedElement.querySelector('h3')?.textContent || 'Unknown';
            
            // Clean up visual indicators
            servicesGrid.querySelectorAll('.service-list-item').forEach(item => {
                item.classList.remove('drag-over');
            });
            
            const addButton = servicesGrid.querySelector('.add-service-item');
            
            // Check if we have stored target from dragover
            if (highlightedTarget) {
                const storedTitle = highlightedTarget.querySelector('h3')?.textContent || 'Unknown';
            } else {
            }
            
            // If we don't have a stored target (quick drop), calculate it immediately
            if (!highlightedTarget) {
                const services = [...servicesGrid.querySelectorAll('.service-list-item:not(.add-service-item):not(.dragging)')];
                
                let closest = null;
                let minDistance = Infinity;
                
                services.forEach((service, index) => {
                    const rect = service.getBoundingClientRect();
                    const centerX = rect.left + rect.width / 2;
                    const centerY = rect.top + rect.height / 2;
                    const distance = Math.sqrt(Math.pow(e.clientX - centerX, 2) + Math.pow(e.clientY - centerY, 2));
                    const serviceTitle = service.querySelector('h3')?.textContent || 'Unknown';
                    
                    
                    if (distance < minDistance) {
                        minDistance = distance;
                        closest = service;
                    }
                });
                
                if (closest && minDistance < 250) {
                    highlightedTarget = closest;
                    const rect = closest.getBoundingClientRect();
                    const centerX = rect.left + rect.width / 2;
                    dropPosition = e.clientX < centerX ? 'before' : 'after';
                    
                    const closestTitle = closest.querySelector('h3')?.textContent || 'Unknown';
                } else {
                }
            }
            
            // Use the target for position swapping
            if (highlightedTarget && dropPosition === 'swap') {
                const targetTitle = highlightedTarget.querySelector('h3')?.textContent || 'Unknown';
                
                // Get the next sibling of both elements to preserve their positions
                const draggedNextSibling = draggedElement.nextElementSibling;
                const targetNextSibling = highlightedTarget.nextElementSibling;
                
                
                // Temporarily remove both elements
                const draggedParent = draggedElement.parentNode;
                const targetParent = highlightedTarget.parentNode;
                
                // Insert dragged element where target was
                if (targetNextSibling) {
                    targetParent.insertBefore(draggedElement, targetNextSibling);
                } else {
                    targetParent.appendChild(draggedElement);
                }
                
                // Insert target element where dragged was
                if (draggedNextSibling) {
                    draggedParent.insertBefore(highlightedTarget, draggedNextSibling);
                } else {
                    draggedParent.appendChild(highlightedTarget);
                }
                
            } else {
                // No valid target - default to end position
                if (addButton) {
                    servicesGrid.insertBefore(draggedElement, addButton);
                } else {
                    servicesGrid.appendChild(draggedElement);
                }
            }
            
            // Clear the highlighted target and position
            highlightedTarget = null;
            dropPosition = null;
            
            draggedElement.classList.remove('dragging');
            await this.updateServiceOrder();
        });
        
        servicesGrid.addEventListener('dragleave', (e) => {
            // Only clear if we're actually leaving the container
            if (!servicesGrid.contains(e.relatedTarget)) {
                servicesGrid.querySelectorAll('.service-list-item').forEach(item => {
                    item.classList.remove('drag-over');
                });
                highlightedTarget = null; // Clear the highlighted target
                dropPosition = null;
            }
        });
    }
    
    setupFAQDragAndDrop() {
        const faqGrid = document.getElementById('faqGrid');
        if (!faqGrid) return;
        
        // Add event listeners to existing FAQ items
        this.addFAQDragListeners(faqGrid);
        
        faqGrid.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'move';
            
            const afterElement = this.getDragAfterElement(faqGrid, e.clientY, '.faq-item:not(.add-faq-item)');
            const dragging = document.querySelector('.dragging');
            
            // Remove existing drop indicators
            faqGrid.querySelectorAll('.drop-indicator').forEach(indicator => indicator.remove());
            
            if (afterElement == null) {
                const addButton = faqGrid.querySelector('.add-faq-item');
                const loadMore = faqGrid.querySelector('.faq-load-more');
                const insertBefore = addButton || loadMore;
                if (insertBefore) {
                    faqGrid.insertBefore(dragging, insertBefore);
                } else {
                    faqGrid.appendChild(dragging);
                }
            } else {
                faqGrid.insertBefore(dragging, afterElement);
            }
        });
        
        faqGrid.addEventListener('drop', async (e) => {
            e.preventDefault();
            const draggedElement = document.querySelector('.dragging');
            if (draggedElement) {
                draggedElement.classList.remove('dragging');
                await this.updateFAQOrder();
            }
        });
    }
    
    addServiceDragListeners(container) {
        const serviceItems = container.querySelectorAll('.service-list-item:not(.add-service-item)');
        serviceItems.forEach(item => {
            if (!item.hasAttribute('data-drag-listeners')) {
                item.addEventListener('dragstart', (e) => {
                    const serviceTitle = item.querySelector('h3')?.textContent || 'Unknown';
                    item.classList.add('dragging');
                    e.dataTransfer.effectAllowed = 'move';
                });
                
                item.addEventListener('dragend', (e) => {
                    const serviceTitle = item.querySelector('h3')?.textContent || 'Unknown';
                    item.classList.remove('dragging');
                });
                
                item.setAttribute('data-drag-listeners', 'true');
            }
        });
    }
    
    addFAQDragListeners(container) {
        const faqItems = container.querySelectorAll('.faq-item:not(.add-faq-item)');
        faqItems.forEach(item => {
            if (!item.hasAttribute('data-drag-listeners')) {
                item.addEventListener('dragstart', (e) => {
                    item.classList.add('dragging');
                    e.dataTransfer.effectAllowed = 'move';
                });
                
                item.addEventListener('dragend', (e) => {
                    item.classList.remove('dragging');
                });
                
                item.setAttribute('data-drag-listeners', 'true');
            }
        });
    }
    
    getDragAfterElement(container, y, selector, x = null) {
        const draggableElements = [...container.querySelectorAll(`${selector}:not(.dragging)`)];
        
        if (x !== null && draggableElements.length > 0) {
            // Sort elements by their visual position (top to bottom, left to right)
            const sortedElements = draggableElements.sort((a, b) => {
                const aBox = a.getBoundingClientRect();
                const bBox = b.getBoundingClientRect();
                
                // First sort by row (top position)
                const rowDiff = Math.floor(aBox.top / 100) - Math.floor(bBox.top / 100);
                if (rowDiff !== 0) return rowDiff;
                
                // Then sort by column (left position)
                return aBox.left - bBox.left;
            });
            
            // Find which element we're closest to
            let targetElement = null;
            let minDistance = Infinity;
            
            for (const element of sortedElements) {
                const box = element.getBoundingClientRect();
                
                // Expand the hit area to make it easier to target
                const expandedBox = {
                    left: box.left - 20,
                    right: box.right + 20,
                    top: box.top - 20,
                    bottom: box.bottom + 20
                };
                
                // Check if cursor is within the expanded bounds
                if (x >= expandedBox.left && x <= expandedBox.right && 
                    y >= expandedBox.top && y <= expandedBox.bottom) {
                    
                    const centerX = box.left + box.width / 2;
                    const centerY = box.top + box.height / 2;
                    const distance = Math.sqrt(Math.pow(x - centerX, 2) + Math.pow(y - centerY, 2));
                    
                    if (distance < minDistance) {
                        minDistance = distance;
                        targetElement = element;
                    }
                }
            }
            
            if (targetElement) {
                const box = targetElement.getBoundingClientRect();
                const centerX = box.left + box.width / 2;
                
                // For grid layouts, use left/right positioning
                if (x < centerX) {
                    return targetElement;
                } else {
                    return targetElement.nextElementSibling;
                }
            }
            
            // If not directly over an element, find the best insertion point
            // by looking at the overall position in the grid
            for (let i = 0; i < sortedElements.length; i++) {
                const element = sortedElements[i];
                const box = element.getBoundingClientRect();
                
                // If we're above this element, insert before it
                if (y < box.top + box.height / 2) {
                    return element;
                }
                
                // If we're in the same row but to the left
                if (Math.abs(y - (box.top + box.height / 2)) < 50 && x < box.left) {
                    return element;
                }
            }
        }
        
        // Fallback for single-coordinate positioning or when grid logic fails
        return draggableElements.reduce((closest, child) => {
            const box = child.getBoundingClientRect();
            const offset = y - box.top - box.height / 2;
            
            if (offset < 0 && offset > closest.offset) {
                return { offset: offset, element: child };
            } else {
                return closest;
            }
        }, { offset: Number.NEGATIVE_INFINITY }).element;
    }
    
    async updateServiceOrder() {
        const serviceItems = document.querySelectorAll('.service-list-item:not(.add-service-item)');
        const servicesGrid = document.getElementById('servicesGrid');
        const orderData = [];
        
        serviceItems.forEach((item, index) => {
            const serviceId = item.getAttribute('data-service-id');
            if (serviceId) {
                orderData.push({
                    id: parseInt(serviceId),
                    display_order: index + 1
                });
            }
        });
        
        try {
            // Show loading state on the services grid
            if (servicesGrid) {
                servicesGrid.classList.add('admin-loading');
            }
            
            const response = await fetch('/api/services/reorder', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ services: orderData })
            });
            
            if (!response.ok) {
                console.error('Failed to update service order');
            }
        } catch (error) {
            console.error('Error updating service order:', error);
        } finally {
            // Hide loading state
            if (servicesGrid) {
                servicesGrid.classList.remove('admin-loading');
            }
        }
    }
    
    async updateFAQOrder() {
        const faqItems = document.querySelectorAll('.faq-item:not(.add-faq-item)');
        const faqGrid = document.getElementById('faqGrid');
        const orderData = [];
        
        faqItems.forEach((item, index) => {
            const faqId = item.getAttribute('data-faq-id');
            if (faqId) {
                orderData.push({
                    id: parseInt(faqId),
                    display_order: index + 1
                });
            }
        });
        
        try {
            // Show loading state on the FAQ grid
            if (faqGrid) {
                faqGrid.classList.add('admin-loading');
            }
            
            const response = await fetch('/api/faqs/reorder', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ faqs: orderData })
            });
            
            if (!response.ok) {
                console.error('Failed to update FAQ order');
            }
        } catch (error) {
            console.error('Error updating FAQ order:', error);
        } finally {
            // Hide loading state
            if (faqGrid) {
                faqGrid.classList.remove('admin-loading');
            }
        }
    }
    
    setupAdminHelpModal() {
        const helpBtn = document.getElementById('adminHelpBtn');
        const helpModal = document.getElementById('adminHelpModal');
        const helpModalClose = document.getElementById('adminHelpModalClose');
        const helpModalFullscreen = document.getElementById('adminHelpModalFullscreen');
        const helpModalContent = document.getElementById('adminHelpModalContent');
        
        if (!helpBtn || !helpModal || !helpModalClose) return;
        
        // Open help modal
        helpBtn.addEventListener('click', () => {
            helpModal.style.display = 'flex';
            document.body.style.overflow = 'hidden';
            // Reset fullscreen state
            helpModalContent.classList.remove('fullscreen');
            this.updateAdminHelpFullscreenIcon(false);
        });
        
        // Setup fullscreen button
        if (helpModalFullscreen) {
            helpModalFullscreen.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.toggleAdminHelpFullscreen();
            });
        }
        
        // Close help modal
        const closeModal = () => {
            helpModal.style.display = 'none';
            document.body.style.overflow = '';
            // Reset fullscreen state
            helpModalContent.classList.remove('fullscreen');
            this.updateAdminHelpFullscreenIcon(false);
        };
        
        helpModalClose.addEventListener('click', closeModal);
        
        // Close on backdrop click
        helpModal.addEventListener('click', (e) => {
            if (e.target === helpModal) {
                closeModal();
            }
        });
        
        // Close on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && helpModal.style.display === 'flex') {
                if (helpModalContent && helpModalContent.classList.contains('fullscreen')) {
                    this.toggleAdminHelpFullscreen();
                } else {
                    closeModal();
                }
            }
        });
    }
    
    toggleAdminHelpFullscreen() {
        const helpModalContent = document.getElementById('adminHelpModalContent');
        if (!helpModalContent) return;
        
        const isFullscreen = helpModalContent.classList.contains('fullscreen');
        
        if (isFullscreen) {
            helpModalContent.classList.remove('fullscreen');
        } else {
            helpModalContent.classList.add('fullscreen');
        }
        
        this.updateAdminHelpFullscreenIcon(!isFullscreen);
    }
    
    updateAdminHelpFullscreenIcon(isFullscreen) {
        const fullscreenBtn = document.getElementById('adminHelpModalFullscreen');
        if (!fullscreenBtn) return;

        const icon = fullscreenBtn.querySelector('i');
        if (!icon) return;

        if (isFullscreen) {
            icon.className = 'fas fa-compress';
            fullscreenBtn.title = 'Exit Fullscreen';
        } else {
            icon.className = 'fas fa-expand';
            fullscreenBtn.title = 'Enter Fullscreen';
        }
    }

    setupFontManagement() {
        const fontManagementForm = document.getElementById('fontManagementForm');
        const headingFontSelect = document.getElementById('heading-font-select');
        const bodyFontSelect = document.getElementById('body-font-select');
        const customHeadingSection = document.getElementById('custom-heading-font-section');
        const customBodySection = document.getElementById('custom-body-font-section');
        const customHeadingName = document.getElementById('custom-heading-font-name');
        const customHeadingCss = document.getElementById('custom-heading-font-css');
        const customBodyName = document.getElementById('custom-body-font-name');
        const customBodyCss = document.getElementById('custom-body-font-css');
        const previewHeading = document.getElementById('preview-heading');
        const previewBody = document.getElementById('preview-body');
        const resetFontsBtn = document.getElementById('reset-fonts-btn');

        if (!fontManagementForm) return; // Not on a page with font management

        // Initialize font tracking
        this.loadedFonts = new Set();

        // Load current font settings on page load
        this.loadCurrentFontSettings();

        // Event listeners for font selection changes
        if (headingFontSelect) {
            headingFontSelect.addEventListener('change', () => this.handleFontChange());
        }

        if (bodyFontSelect) {
            bodyFontSelect.addEventListener('change', () => this.handleFontChange());
        }

        // Custom heading font handlers
        if (customHeadingName) {
            customHeadingName.addEventListener('input', () => this.handleFontChange());
        }

        if (customHeadingCss) {
            customHeadingCss.addEventListener('input', () => this.handleFontChange());
        }

        // Custom body font handlers
        if (customBodyName) {
            customBodyName.addEventListener('input', () => this.handleFontChange());
        }

        if (customBodyCss) {
            customBodyCss.addEventListener('input', () => this.handleFontChange());
        }

        // Font form submission
        if (fontManagementForm) {
            fontManagementForm.addEventListener('submit', async (e) => {
                await this.handleFontFormSubmit(e);
            });
        }

        // Reset fonts functionality
        if (resetFontsBtn) {
            resetFontsBtn.addEventListener('click', async () => {
                await this.handleResetFonts();
            });
        }
    }

    async loadCurrentFontSettings() {
        try {
            const response = await fetch('/api/fonts');
            const data = await response.json();

            if (data.success) {
                const settings = data.settings;

                // Update current font display
                const currentHeadingFont = document.getElementById('current-heading-font');
                const currentBodyFont = document.getElementById('current-body-font');

                if (currentHeadingFont) currentHeadingFont.textContent = settings.heading_font;
                if (currentBodyFont) currentBodyFont.textContent = settings.body_font;

                // Update preview with current fonts
                this.updatePreviewFonts(settings.heading_font, settings.body_font, settings.custom_css);

                // Set select values
                this.setSelectValue(document.getElementById('heading-font-select'), settings.heading_font);
                this.setSelectValue(document.getElementById('body-font-select'), settings.body_font);

                // If custom CSS exists, show it in the new fields
                // Note: This will show the combined CSS as a placeholder - users may need to separate it manually
                if (settings.custom_css) {
                    const customHeadingCss = document.getElementById('custom-heading-font-css');
                    const customBodyCss = document.getElementById('custom-body-font-css');

                    // For now, show the existing custom CSS in heading font CSS as a starting point
                    // Users can manually separate or reorganize as needed
                    if (customHeadingCss) {
                        customHeadingCss.value = settings.custom_css;
                        customHeadingCss.placeholder = "Existing custom CSS loaded here - you may reorganize as needed";
                    }
                }
            }
        } catch (error) {
            console.error('Error loading font settings:', error);
        }
    }

    setSelectValue(selectElement, value) {
        if (!selectElement) return;

        // Check if the value exists in the options
        let optionFound = false;
        for (let option of selectElement.options) {
            if (option.value === value) {
                option.selected = true;
                optionFound = true;
                break;
            }
        }

        // If the value is not found and it's not empty or "custom", it's likely a custom font
        if (!optionFound && value && value !== 'custom') {
            // Check if this is a predefined Google Font that might be missing
            const predefinedFonts = ['Space Grotesk', 'Manrope', 'Inter', 'Roboto', 'Open Sans', 'Lato', 'Montserrat', 'Poppins', 'Source Sans Pro', 'Raleway', 'Nunito', 'Playfair Display', 'Merriweather', 'PT Sans', 'Noto Sans'];

            if (!predefinedFonts.includes(value)) {
                // This is a custom font - add it to the dropdown and select it
                this.addCustomFontToDropdown(selectElement, value);

                // Now select the newly added option
                for (let option of selectElement.options) {
                    if (option.value === value) {
                        option.selected = true;
                        break;
                    }
                }
            }
        }
    }

    addCustomFontToDropdown(selectElement, fontName) {
        // Check if this custom font already exists in the dropdown
        for (let option of selectElement.options) {
            if (option.value === fontName) {
                return; // Already exists, no need to add
            }
        }

        // Create a new option for the custom font
        const newOption = document.createElement('option');
        newOption.value = fontName;
        newOption.textContent = `${fontName} (Custom)`;

        // Find the "Google Fonts (Standard)" optgroup to add the custom font there
        const standardOptgroup = selectElement.querySelector('optgroup[label="Google Fonts (Standard)"]');
        if (standardOptgroup) {
            // Add to the end of the standard fonts optgroup
            standardOptgroup.appendChild(newOption);
        } else {
            // Fallback: if no optgroup exists, add directly to select
            selectElement.appendChild(newOption);
        }

        console.log(`Added custom font "${fontName}" to dropdown`);
    }

    handleFontChange() {
        const headingFontSelect = document.getElementById('heading-font-select');
        const bodyFontSelect = document.getElementById('body-font-select');
        const customHeadingSection = document.getElementById('custom-heading-font-section');
        const customBodySection = document.getElementById('custom-body-font-section');
        const customHeadingName = document.getElementById('custom-heading-font-name');
        const customHeadingCss = document.getElementById('custom-heading-font-css');
        const customBodyName = document.getElementById('custom-body-font-name');
        const customBodyCss = document.getElementById('custom-body-font-css');

        if (!headingFontSelect || !bodyFontSelect) return;

        const headingFont = headingFontSelect.value;
        const bodyFont = bodyFontSelect.value;

        // Show/hide custom font sections
        const showCustomHeadingSection = headingFont === 'custom';
        const showCustomBodySection = bodyFont === 'custom';

        if (customHeadingSection) {
            customHeadingSection.style.display = showCustomHeadingSection ? 'block' : 'none';
        }
        if (customBodySection) {
            customBodySection.style.display = showCustomBodySection ? 'block' : 'none';
        }

        // Prepare fonts for preview
        let finalHeadingFont = headingFont;
        let finalBodyFont = bodyFont;
        let combinedCustomCss = '';

        // Handle custom heading font
        if (headingFont === 'custom' && customHeadingName && customHeadingName.value) {
            finalHeadingFont = customHeadingName.value;
            if (customHeadingCss && customHeadingCss.value) {
                combinedCustomCss += customHeadingCss.value + '\n\n';
            }
        }

        // Handle custom body font
        if (bodyFont === 'custom' && customBodyName && customBodyName.value) {
            finalBodyFont = customBodyName.value;
            if (customBodyCss && customBodyCss.value) {
                combinedCustomCss += customBodyCss.value + '\n\n';
            }
        }

        // Update font preview
        if (finalHeadingFont && finalBodyFont &&
            finalHeadingFont !== 'custom' && finalBodyFont !== 'custom') {
            this.loadAndPreviewFonts(finalHeadingFont, finalBodyFont, combinedCustomCss.trim());
        }
    }

    async loadAndPreviewFonts(headingFont, bodyFont, customCss = '') {
        try {
            // Load fonts that aren't already loaded
            const fontsToLoad = [headingFont, bodyFont].filter(font =>
                font && !this.loadedFonts.has(font) && !this.isSystemFont(font)
            );

            if (customCss) {
                // If custom CSS is provided, load it
                this.loadCustomCSS(customCss);
            } else {
                // Load Google Fonts
                for (const font of fontsToLoad) {
                    await this.loadGoogleFont(font);
                    this.loadedFonts.add(font);
                }
            }

            // Update preview
            this.updatePreviewFonts(headingFont, bodyFont, customCss);

        } catch (error) {
            console.error('Error loading fonts:', error);
        }
    }

    isSystemFont(fontName) {
        const systemFonts = ['Arial', 'Helvetica', 'Times New Roman', 'Georgia', 'Verdana', 'Courier New'];
        return systemFonts.includes(fontName);
    }

    async loadGoogleFont(fontName) {
        return new Promise((resolve, reject) => {
            if (this.loadedFonts.has(fontName)) {
                resolve();
                return;
            }

            const link = document.createElement('link');
            link.href = `https://fonts.googleapis.com/css2?family=${encodeURIComponent(fontName)}:wght@300;400;500;600;700&display=swap`;
            link.rel = 'stylesheet';

            link.onload = () => resolve();
            link.onerror = () => reject(new Error(`Failed to load font: ${fontName}`));

            document.head.appendChild(link);
        });
    }

    loadCustomCSS(cssText) {
        // Remove any existing custom font style element
        const existingStyle = document.getElementById('custom-font-style');
        if (existingStyle) {
            existingStyle.remove();
        }

        // Create new style element
        const style = document.createElement('style');
        style.id = 'custom-font-style';
        style.textContent = cssText;
        document.head.appendChild(style);
    }

    updatePreviewFonts(headingFont, bodyFont, customCss = '') {
        const previewHeading = document.getElementById('preview-heading');
        const previewBody = document.getElementById('preview-body');

        if (previewHeading) {
            previewHeading.style.fontFamily = `"${headingFont}", sans-serif`;
        }
        if (previewBody) {
            previewBody.style.fontFamily = `"${bodyFont}", sans-serif`;
        }

        // Also update the current font preview texts
        const headingPreview = document.querySelector('.heading-font-preview');
        const bodyPreview = document.querySelector('.body-font-preview');

        if (headingPreview) {
            headingPreview.style.fontFamily = `"${headingFont}", sans-serif`;
        }
        if (bodyPreview) {
            bodyPreview.style.fontFamily = `"${bodyFont}", sans-serif`;
        }
    }

    async handleFontFormSubmit(e) {
        e.preventDefault();

        const headingFontSelect = document.getElementById('heading-font-select');
        const bodyFontSelect = document.getElementById('body-font-select');
        const customHeadingName = document.getElementById('custom-heading-font-name');
        const customHeadingCss = document.getElementById('custom-heading-font-css');
        const customBodyName = document.getElementById('custom-body-font-name');
        const customBodyCss = document.getElementById('custom-body-font-css');

        // Determine final font names
        let headingFont = headingFontSelect.value;
        let bodyFont = bodyFontSelect.value;
        let combinedCustomCss = '';

        // Handle custom heading font
        if (headingFontSelect.value === 'custom') {
            if (!customHeadingName || !customHeadingName.value.trim()) {
                alert('Please provide a name for your custom heading font.');
                return;
            }
            if (!customHeadingCss || !customHeadingCss.value.trim()) {
                alert('Please provide CSS for your custom heading font.');
                return;
            }
            headingFont = customHeadingName.value.trim();
            combinedCustomCss += customHeadingCss.value.trim() + '\n\n';
        }

        // Handle custom body font
        if (bodyFontSelect.value === 'custom') {
            if (!customBodyName || !customBodyName.value.trim()) {
                alert('Please provide a name for your custom body font.');
                return;
            }
            if (!customBodyCss || !customBodyCss.value.trim()) {
                alert('Please provide CSS for your custom body font.');
                return;
            }
            bodyFont = customBodyName.value.trim();
            combinedCustomCss += customBodyCss.value.trim() + '\n\n';
        }

        if (!headingFont || !bodyFont) {
            alert('Please select both heading and body fonts.');
            return;
        }

        try {
            const response = await fetch('/api/fonts', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    heading_font: headingFont,
                    body_font: bodyFont,
                    custom_css: combinedCustomCss.trim()
                })
            });

            const result = await response.json();

            if (result.success) {
                // Update the page fonts
                this.applyFontsToPage(headingFont, bodyFont, combinedCustomCss.trim());

                // Update current font display
                const currentHeadingFont = document.getElementById('current-heading-font');
                const currentBodyFont = document.getElementById('current-body-font');

                if (currentHeadingFont) currentHeadingFont.textContent = headingFont;
                if (currentBodyFont) currentBodyFont.textContent = bodyFont;

                alert('Font settings updated successfully!');
            } else {
                alert('Error updating fonts: ' + result.error);
            }
        } catch (error) {
            console.error('Error updating fonts:', error);
            alert('Error updating fonts. Please try again.');
        }
    }

    async handleResetFonts() {
        if (confirm('Are you sure you want to reset fonts to default (Space Grotesk for headings, Manrope for body)?')) {
            try {
                const response = await fetch('/api/fonts/reset', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                });

                const result = await response.json();

                if (result.success) {
                    // Reset selects to default
                    this.setSelectValue(document.getElementById('heading-font-select'), 'Space Grotesk');
                    this.setSelectValue(document.getElementById('body-font-select'), 'Manrope');

                    // Clear custom fields
                    const customHeadingName = document.getElementById('custom-heading-font-name');
                    const customHeadingCss = document.getElementById('custom-heading-font-css');
                    const customHeadingSection = document.getElementById('custom-heading-font-section');
                    const customBodyName = document.getElementById('custom-body-font-name');
                    const customBodyCss = document.getElementById('custom-body-font-css');
                    const customBodySection = document.getElementById('custom-body-font-section');

                    if (customHeadingName) customHeadingName.value = '';
                    if (customHeadingCss) customHeadingCss.value = '';
                    if (customHeadingSection) customHeadingSection.style.display = 'none';
                    if (customBodyName) customBodyName.value = '';
                    if (customBodyCss) customBodyCss.value = '';
                    if (customBodySection) customBodySection.style.display = 'none';

                    // Apply default fonts
                    this.applyFontsToPage('Space Grotesk', 'Manrope', '');

                    // Update current font display
                    const currentHeadingFont = document.getElementById('current-heading-font');
                    const currentBodyFont = document.getElementById('current-body-font');

                    if (currentHeadingFont) currentHeadingFont.textContent = 'Space Grotesk';
                    if (currentBodyFont) currentBodyFont.textContent = 'Manrope';

                    alert('Fonts reset to default successfully!');
                } else {
                    alert('Error resetting fonts: ' + result.error);
                }
            } catch (error) {
                console.error('Error resetting fonts:', error);
                alert('Error resetting fonts. Please try again.');
            }
        }
    }

    applyFontsToPage(headingFont, bodyFont, customCss = '') {
        // Apply custom CSS if provided
        if (customCss) {
            this.loadCustomCSS(customCss);
        }

        // Update CSS custom properties for fonts
        const style = document.createElement('style');
        style.id = 'live-font-update';

        // Remove existing live update style
        const existingLiveStyle = document.getElementById('live-font-update');
        if (existingLiveStyle) {
            existingLiveStyle.remove();
        }

        style.textContent = `
            :root {
                --heading-font: "${headingFont}", sans-serif;
                --body-font: "${bodyFont}", sans-serif;
            }

            h1, h2, h3, h4, h5, h6, .hero-title, .section-header h2 {
                font-family: var(--heading-font) !important;
            }

            body, p, div, span, .hero-subtitle, .service-content, .faq-answer, .contact-form {
                font-family: var(--body-font) !important;
            }
        `;

        document.head.appendChild(style);
    }

}

// Initialize the website functionality
let website;

// Ensure only one instance is created
function initializeWebsite() {
    if (!website) {
        console.log('🚀 Initializing MaydayWebsite...');
        website = new MaydayWebsite();
    } else {
        console.log('⚠️ MaydayWebsite already initialized, skipping...');
    }
}

// Wait for DOM to be ready
document.addEventListener('DOMContentLoaded', initializeWebsite);

// If DOM is already ready, initialize immediately
if (document.readyState !== 'loading') {
    initializeWebsite();
}

// Additional legacy support for existing functionality
document.addEventListener('DOMContentLoaded', function() {
    // Handle notification close buttons (legacy support)
    const closeButtons = document.querySelectorAll('.close-notification');
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const notification = this.closest('.notification');
            if (notification) {
                notification.style.display = 'none';
            }
        });
    });

    // Service booking button functionality
    const bookingButtons = document.querySelectorAll('.service-booking');
    bookingButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Use HCPWidget.openModal() like in v1 app
            if (typeof HCPWidget !== 'undefined' && HCPWidget.openModal) {
                HCPWidget.openModal();
            } else {
                // Fallback: redirect to HouseCall Pro booking page
                window.open('https://client.housecallpro.com/customer_portal/request-link?token=e57304ab4e974b93a5b90c2084ba3d1a', '_blank');
            }
            
            // Add analytics tracking
            if (typeof gtag !== 'undefined') {
                gtag('event', 'click', {
                    event_category: 'engagement',
                    event_label: 'service_booking'
                });
            }
        });
    });

    // Enhanced form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input[required], textarea[required]');
        
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                this.classList.remove('error');
                
                if (!this.value.trim()) {
                    this.classList.add('error');
                }
                
                // Email validation
                if (this.type === 'email' && this.value) {
                    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                    if (!emailRegex.test(this.value)) {
                        this.classList.add('error');
                    }
                }
            });
        });
    });
});

// Add error styles for form validation
const errorStyles = document.createElement('style');
errorStyles.textContent = `
    .form-group input.error,
    .form-group textarea.error {
        border-color: #ef4444;
        background-color: #fef2f2;
    }
    
    .form-group input.error:focus,
    .form-group textarea.error:focus {
        border-color: #dc2626;
        box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
    }
`;
document.head.appendChild(errorStyles);

// Custom Confirmation Modal
window.showConfirmModal = function(options = {}) {
    return new Promise((resolve) => {
        const {
            title = 'Confirm Action',
            message = 'Are you sure you want to proceed?',
            confirmText = 'Confirm',
            cancelText = 'Cancel',
            type = 'info', // 'info', 'warning', 'danger'
            confirmButtonType = '' // 'danger', 'warning', or ''
        } = options;

        const modal = document.getElementById('confirmModal');
        const modalTitle = document.getElementById('confirmModalTitle');
        const modalMessage = document.getElementById('confirmModalMessage');
        const modalIcon = document.getElementById('confirmModalIcon');
        const confirmBtn = document.getElementById('confirmModalConfirm');
        const cancelBtn = document.getElementById('confirmModalCancel');

        if (!modal) {
            console.error('Confirmation modal not found');
            resolve(false);
            return;
        }

        // Set content
        modalTitle.textContent = title;
        modalMessage.textContent = message;
        confirmBtn.textContent = confirmText;
        cancelBtn.textContent = cancelText;

        // Set icon based on type
        const iconElement = modalIcon.querySelector('i');
        modalIcon.className = `confirm-modal-icon ${type}`;
        
        switch(type) {
            case 'warning':
                iconElement.className = 'fas fa-exclamation-triangle';
                break;
            case 'danger':
                iconElement.className = 'fas fa-exclamation-circle';
                break;
            default:
                iconElement.className = 'fas fa-question-circle';
        }

        // Set confirm button style
        confirmBtn.className = `confirm-btn confirm-btn-confirm ${confirmButtonType}`;

        // Event handlers
        const handleConfirm = () => {
            cleanup();
            resolve(true);
        };

        const handleCancel = () => {
            cleanup();
            resolve(false);
        };

        const handleEscape = (e) => {
            if (e.key === 'Escape') {
                handleCancel();
            }
        };

        const handleBackdrop = (e) => {
            if (e.target === modal) {
                handleCancel();
            }
        };

        const cleanup = () => {
            modal.style.display = 'none';
            document.body.style.overflow = 'auto';
            confirmBtn.removeEventListener('click', handleConfirm);
            cancelBtn.removeEventListener('click', handleCancel);
            document.removeEventListener('keydown', handleEscape);
            modal.removeEventListener('click', handleBackdrop);
        };

        // Add event listeners
        confirmBtn.addEventListener('click', handleConfirm);
        cancelBtn.addEventListener('click', handleCancel);
        document.addEventListener('keydown', handleEscape);
        modal.addEventListener('click', handleBackdrop);

        // Show modal
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
        
        // Focus the cancel button by default for better UX
        setTimeout(() => cancelBtn.focus(), 100);
    });
};

// Note: Website initialization is handled above to prevent duplicate instances