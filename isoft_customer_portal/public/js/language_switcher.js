/**
 * Language Switcher Component for Isoft Customer Portal
 */

(function() {
    'use strict';

    let languageSwitcher = {
        isInitialized: false,

        init: function() {
            if (this.isInitialized) return;
            
            this.bindEvents();
            this.updateCurrentLanguageDisplay();
            this.isInitialized = true;
        },

        bindEvents: function() {
            // Language button click
            $(document).on('click', '#languageBtn', function(e) {
                e.preventDefault();
                e.stopPropagation();
                languageSwitcher.toggleDropdown();
            });

            // Language option click
            $(document).on('click', '.language-option', function(e) {
                e.preventDefault();
                e.stopPropagation();
                const lang = $(this).data('lang');
                languageSwitcher.setLanguage(lang);
            });

            // Close dropdown when clicking outside
            $(document).on('click', function(e) {
                if (!$(e.target).closest('.language-switcher').length) {
                    languageSwitcher.closeDropdown();
                }
            });

            // Listen for language changes
            window.addEventListener('languageChanged', function(e) {
                languageSwitcher.updateCurrentLanguageDisplay();
                languageSwitcher.closeDropdown();
                
                // Force refresh all translations after a short delay
                setTimeout(function() {
                    languageSwitcher.refreshTranslations();
                }, 200);
            });
        },

        toggleDropdown: function() {
            const dropdown = $('#languageDropdown');
            dropdown.toggleClass('show');
        },

        closeDropdown: function() {
            const dropdown = $('#languageDropdown');
            dropdown.removeClass('show');
        },

        setLanguage: function(lang) {
            if (window.IsoftTranslation) {
                window.IsoftTranslation.setLanguage(lang);
            }
        },

        updateCurrentLanguageDisplay: function() {
            const currentLang = window.IsoftTranslation ? 
                window.IsoftTranslation.getCurrentLanguage() : 'en';
            
            const displayText = currentLang.toUpperCase();
            $('#currentLanguage').text(displayText);
            
            // Update active state in dropdown
            $('.language-option').removeClass('active');
            $(`.language-option[data-lang="${currentLang}"]`).addClass('active');
            
            // Ensure language button is visible
            $('#languageBtn').show();
            $('.language-switcher').show();
        },

        // Force refresh all translations
        refreshTranslations: function() {
            if (window.IsoftTranslation) {
                window.IsoftTranslation.translatePage();
                
                // Specifically translate summary cards
                window.IsoftTranslation.translateSummaryCards();
                
                // Also refresh any page-specific translations
                setTimeout(function() {
                    // Force another round of card translation after a delay
                    if (window.IsoftTranslation) {
                        window.IsoftTranslation.translateSummaryCards();
                    }
                    
                    // Trigger a custom event for page-specific translation updates
                    $(document).trigger('translationsRefreshed');
                }, 100);
            }
        }
    };

    // Initialize when DOM is ready - ensure jQuery is available
    function initializeWhenReady() {
        if (typeof $ !== 'undefined' && typeof jQuery !== 'undefined') {
            $(document).ready(function() {
                // Small delay to ensure translations are loaded first
                setTimeout(function() {
                    languageSwitcher.init();
                }, 100);
            });
        } else {
            // Wait for jQuery to be available
            setTimeout(initializeWhenReady, 50);
        }
    }
    
    // Start initialization
    initializeWhenReady();

    // Export for global access
    window.LanguageSwitcher = languageSwitcher;

})();
