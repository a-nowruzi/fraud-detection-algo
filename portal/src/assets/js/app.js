// Minia Template JavaScript
(function() {
    'use strict';

    // Hide preloader when page is loaded
    function hidePreloader() {
        const preloader = document.getElementById('preloader');
        if (preloader) {
            // Add fade-out class for animation
            preloader.classList.add('fade-out');
            
            // Hide after animation completes
            setTimeout(() => {
                preloader.style.display = 'none';
            }, 500);
        }
    }

    // Toggle sidebar on mobile
    function initSidebarToggle() {
        const sidebarToggle = document.getElementById('vertical-menu-btn');
        const sidebar = document.querySelector('.vertical-menu');
        const mainContent = document.querySelector('.main-content');
        const isRTL = document.documentElement.dir === 'rtl';
        
        if (sidebarToggle && sidebar) {
            sidebarToggle.addEventListener('click', function() {
                sidebar.classList.toggle('show');
                
                // Toggle main content margin for mobile
                if (window.innerWidth <= 991.98) {
                    if (sidebar.classList.contains('show')) {
                        mainContent.style.marginRight = '0';
                        mainContent.style.marginLeft = '0';
                    } else {
                        mainContent.style.marginRight = '';
                        mainContent.style.marginLeft = '';
                    }
                }
            });
        }
    }

    // Initialize tooltips
    function initTooltips() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    // Initialize popovers
    function initPopovers() {
        const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        popoverTriggerList.map(function (popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl);
        });
    }

    // Initialize dropdowns
    function initDropdowns() {
        const dropdownElementList = [].slice.call(document.querySelectorAll('.dropdown-toggle'));
        dropdownElementList.map(function (dropdownToggleEl) {
            return new bootstrap.Dropdown(dropdownToggleEl);
        });
        
        // Fix dropdown transform issues
        fixDropdownTransform();
    }
    
    // Fix dropdown transform styles
    function fixDropdownTransform() {
        // Remove transform from all dropdown menus
        const dropdownMenus = document.querySelectorAll('.dropdown-menu');
        dropdownMenus.forEach(menu => {
            menu.style.transform = 'none';
        });
        
        // Listen for dropdown show events
        document.addEventListener('show.bs.dropdown', function (event) {
            const dropdownMenu = event.target.querySelector('.dropdown-menu');
            if (dropdownMenu) {
                // Remove transform after a short delay to ensure Bootstrap has applied it
                setTimeout(() => {
                    dropdownMenu.style.transform = 'none';
                }, 10);
            }
        });
        
        // Also fix on click events
        document.addEventListener('click', function (event) {
            if (event.target.closest('.dropdown-toggle')) {
                setTimeout(() => {
                    const dropdownMenu = event.target.closest('.dropdown').querySelector('.dropdown-menu');
                    if (dropdownMenu) {
                        dropdownMenu.style.transform = 'none';
                    }
                }, 10);
            }
        });
    }

    // Theme switcher
    function initThemeSwitcher() {
        const themeToggle = document.getElementById('mode-setting-btn');
        const body = document.body;
        
        if (themeToggle) {
            themeToggle.addEventListener('click', function() {
                if (body.classList.contains('dark-mode')) {
                    body.classList.remove('dark-mode');
                    localStorage.setItem('theme', 'light');
                } else {
                    body.classList.add('dark-mode');
                    localStorage.setItem('theme', 'dark');
                }
            });
        }

        // Load saved theme
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme === 'dark') {
            body.classList.add('dark-mode');
        }
    }

    // Right sidebar toggle
    function initRightSidebar() {
        const rightSidebarToggle = document.querySelector('.right-bar-toggle');
        const rightSidebar = document.querySelector('.right-bar');
        const rightSidebarOverlay = document.querySelector('.rightbar-overlay');
        
        if (rightSidebarToggle && rightSidebar) {
            rightSidebarToggle.addEventListener('click', function() {
                rightSidebar.classList.toggle('show');
                if (rightSidebarOverlay) {
                    rightSidebarOverlay.classList.toggle('show');
                }
            });
        }

        if (rightSidebarOverlay) {
            rightSidebarOverlay.addEventListener('click', function() {
                rightSidebar.classList.remove('show');
                rightSidebarOverlay.classList.remove('show');
            });
        }
    }

    // Layout switcher
    function initLayoutSwitcher() {
        const layoutRadios = document.querySelectorAll('input[name="layout"]');
        const body = document.body;
        
        layoutRadios.forEach(radio => {
            radio.addEventListener('change', function() {
                if (this.value === 'horizontal') {
                    body.setAttribute('data-layout', 'horizontal');
                } else {
                    body.setAttribute('data-layout', 'vertical');
                }
            });
        });
    }

    // Initialize all functions
    function init() {
        // Hide preloader first
        hidePreloader();
        
        initSidebarToggle();
        initThemeSwitcher();
        initRightSidebar();
        initLayoutSwitcher();
        
        // Initialize Bootstrap components if available
        if (typeof bootstrap !== 'undefined') {
            initTooltips();
            initPopovers();
            initDropdowns();
        }
    }

    // Run initialization when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Also hide preloader when window is fully loaded
    window.addEventListener('load', hidePreloader);

    // Hide preloader after a delay as fallback
    setTimeout(hidePreloader, 3000);

    // Export functions for global use
    window.MiniaApp = {
        init: init,
        hidePreloader: hidePreloader,
        initSidebarToggle: initSidebarToggle,
        initThemeSwitcher: initThemeSwitcher,
        initRightSidebar: initRightSidebar,
        initLayoutSwitcher: initLayoutSwitcher
    };

})();
