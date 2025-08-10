// Minia Template JavaScript
(function() {
    'use strict';

    // Toggle sidebar on mobile
    function initSidebarToggle() {
        const sidebarToggle = document.getElementById('vertical-menu-btn');
        const sidebar = document.querySelector('.vertical-menu');
        
        if (sidebarToggle && sidebar) {
            sidebarToggle.addEventListener('click', function() {
                sidebar.classList.toggle('show');
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

    // Export functions for global use
    window.MiniaApp = {
        init: init,
        initSidebarToggle: initSidebarToggle,
        initThemeSwitcher: initThemeSwitcher,
        initRightSidebar: initRightSidebar,
        initLayoutSwitcher: initLayoutSwitcher
    };

})();
