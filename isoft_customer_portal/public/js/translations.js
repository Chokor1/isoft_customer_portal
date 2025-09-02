/**
 * Isoft Customer Portal Translation System
 * Supports Portuguese (pt) and English (en)
 */

(function() {
    'use strict';

    // Translation data
    const translations = {
        en: {
            // Navigation
            'Customer Portal': 'Customer Portal',
            'Dashboard': 'Dashboard',
            'Invoices': 'Invoices',
            'Sales Orders': 'Sales Orders',
            'Quotations': 'Quotations',
            'Delivery Notes': 'Delivery Notes',
            'Payments': 'Payments',
            'Ledger': 'Ledger',
            'Main': 'Main',
            'Customer': 'Customer',
            'Logout': 'Logout',
            
            // Dashboard
            'Welcome Back': 'Welcome Back',
            'Account Overview': 'Account Overview',
            'Total Outstanding': 'Total Outstanding',
            'Total Paid': 'Total Paid',
            'Recent Transactions': 'Recent Transactions',
            'Quick Actions': 'Quick Actions',
            'View All Invoices': 'View All Invoices',
            'View All Payments': 'View All Payments',
            'Download Statement': 'Download Statement',
            'Recent Activity': 'Recent Activity',
            'No recent activity': 'No recent activity',
            
            // Invoices
            'Invoice Number': 'Invoice Number',
            'Date': 'Date',
            'Due Date': 'Due Date',
            'Amount': 'Amount',
            'Status': 'Status',
            'Actions': 'Actions',
            'View': 'View',
            'Download': 'Download',
            'Print': 'Print',
            'Paid': 'Paid',
            'Unpaid': 'Unpaid',
            'Overdue': 'Overdue',
            'Partially Paid': 'Partially Paid',
            'Total Invoices': 'Total Invoices',
            'Total Amount': 'Total Amount',
            'Outstanding Amount': 'Outstanding Amount',
            'Paid Amount': 'Paid Amount',
            
            // Payments
            'Payment Number': 'Payment Number',
            'Payment Type': 'Payment Type',
            'Mode of Payment': 'Mode of Payment',
            'Reference No': 'Reference No',
            'Reference Date': 'Reference Date',
            'Total Entries': 'Total Entries',
            'Total Received': 'Total Received',
            'Total Allocated Amount': 'Total Allocated Amount',
            'Unallocated Amount': 'Unallocated Amount',
            'Receive': 'Receive',
            'Pay': 'Pay',
            
            // Sales Orders
            'Order Number': 'Order Number',
            'Order Date': 'Order Date',
            'Delivery Date': 'Delivery Date',
            'Total Orders': 'Total Orders',
            'Confirmed': 'Confirmed',
            'Draft': 'Draft',
            'To Deliver': 'To Deliver',
            'Delivered': 'Delivered',
            'Cancelled': 'Cancelled',
            
            // Quotations
            'Quotation Number': 'Quotation Number',
            'Quotation Date': 'Quotation Date',
            'Valid Till': 'Valid Till',
            'Total Quotations': 'Total Quotations',
            'Open': 'Open',
            'Submitted': 'Submitted',
            'Lost': 'Lost',
            'Expired': 'Expired',
            
            // Delivery Notes
            'Delivery Note': 'Delivery Note',
            'Delivery Date': 'Delivery Date',
            'Total Deliveries': 'Total Deliveries',
            
            // Ledger
            'Transaction Date': 'Transaction Date',
            'Voucher Type': 'Voucher Type',
            'Voucher No': 'Voucher No',
            'Debit': 'Debit',
            'Credit': 'Credit',
            'Balance': 'Balance',
            'Description': 'Description',
            'Opening Balance': 'Opening Balance',
            'Closing Balance': 'Closing Balance',
            
            // Common
            'Loading...': 'Loading...',
            'No data available': 'No data available',
            'Search': 'Search',
            'Filter': 'Filter',
            'Clear Filters': 'Clear Filters',
            'Apply Filters': 'Apply Filters',
            'Export': 'Export',
            'From Date': 'From Date',
            'To Date': 'To Date',
            'All': 'All',
            'Show': 'Show',
            'entries': 'entries',
            'Previous': 'Previous',
            'Next': 'Next',
            'First': 'First',
            'Last': 'Last',
            'Page': 'Page',
            'of': 'of',
            'Showing': 'Showing',
            'to': 'to',
            'entries out of': 'entries out of',
            'total': 'total',
            'Currency': 'Currency',
            
            // Login
            'Sign in to access your account': 'Sign in to access your account',
            'Email/Username': 'Email/Username',
            'Password': 'Password',
            'Sign In': 'Sign In',
            'Don\'t have an account? Contact your administrator.': 'Don\'t have an account? Contact your administrator.',
            
            // Messages
            'Welcome': 'Welcome',
            'Error': 'Error',
            'Success': 'Success',
            'Warning': 'Warning',
            'Info': 'Info',
            'Please wait...': 'Please wait...',
            'Operation completed successfully': 'Operation completed successfully',
            'An error occurred': 'An error occurred',
            'No records found': 'No records found',
            'Data loaded successfully': 'Data loaded successfully'
        },
        
        pt: {
            // Navigation
            'Customer Portal': 'Portal do Cliente',
            'Dashboard': 'Painel',
            'Invoices': 'Faturas',
            'Sales Orders': 'Pedidos de Venda',
            'Quotations': 'Cotações',
            'Delivery Notes': 'Notas de Entrega',
            'Payments': 'Pagamentos',
            'Ledger': 'Razão',
            'Main': 'Principal',
            'Customer': 'Cliente',
            'Logout': 'Sair',
            
            // Dashboard
            'Welcome Back': 'Bem-vindo de Volta',
            'Account Overview': 'Visão Geral da Conta',
            'Total Outstanding': 'Total em Aberto',
            'Total Paid': 'Total Pago',
            'Recent Transactions': 'Transações Recentes',
            'Quick Actions': 'Ações Rápidas',
            'View All Invoices': 'Ver Todas as Faturas',
            'View All Payments': 'Ver Todos os Pagamentos',
            'Download Statement': 'Baixar Extrato',
            'Recent Activity': 'Atividade Recente',
            'No recent activity': 'Nenhuma atividade recente',
            
            // Invoices
            'Invoice Number': 'Número da Fatura',
            'Date': 'Data',
            'Due Date': 'Data de Vencimento',
            'Amount': 'Valor',
            'Status': 'Status',
            'Actions': 'Ações',
            'View': 'Visualizar',
            'Download': 'Baixar',
            'Print': 'Imprimir',
            'Paid': 'Pago',
            'Unpaid': 'Não Pago',
            'Overdue': 'Vencido',
            'Partially Paid': 'Parcialmente Pago',
            'Total Invoices': 'Total de Faturas',
            'Total Amount': 'Valor Total',
            'Outstanding Amount': 'Valor em Aberto',
            'Paid Amount': 'Valor Pago',
            
            // Payments
            'Payment Number': 'Número do Pagamento',
            'Payment Type': 'Tipo de Pagamento',
            'Mode of Payment': 'Forma de Pagamento',
            'Reference No': 'Nº de Referência',
            'Reference Date': 'Data de Referência',
            'Total Entries': 'Total de Entradas',
            'Total Received': 'Total Recebido',
            'Total Allocated Amount': 'Valor Total Alocado',
            'Unallocated Amount': 'Valor Não Alocado',
            'Receive': 'Receber',
            'Pay': 'Pagar',
            
            // Sales Orders
            'Order Number': 'Número do Pedido',
            'Order Date': 'Data do Pedido',
            'Delivery Date': 'Data de Entrega',
            'Total Orders': 'Total de Pedidos',
            'Confirmed': 'Confirmado',
            'Draft': 'Rascunho',
            'To Deliver': 'Para Entregar',
            'Delivered': 'Entregue',
            'Cancelled': 'Cancelado',
            
            // Quotations
            'Quotation Number': 'Número da Cotação',
            'Quotation Date': 'Data da Cotação',
            'Valid Till': 'Válida Até',
            'Total Quotations': 'Total de Cotações',
            'Open': 'Aberto',
            'Submitted': 'Enviado',
            'Lost': 'Perdido',
            'Expired': 'Expirado',
            
            // Delivery Notes
            'Delivery Note': 'Nota de Entrega',
            'Delivery Date': 'Data de Entrega',
            'Total Deliveries': 'Total de Entregas',
            
            // Ledger
            'Transaction Date': 'Data da Transação',
            'Voucher Type': 'Tipo de Comprovante',
            'Voucher No': 'Nº do Comprovante',
            'Debit': 'Débito',
            'Credit': 'Crédito',
            'Balance': 'Saldo',
            'Description': 'Descrição',
            'Opening Balance': 'Saldo de Abertura',
            'Closing Balance': 'Saldo de Fechamento',
            
            // Common
            'Loading...': 'Carregando...',
            'No data available': 'Nenhum dado disponível',
            'Search': 'Pesquisar',
            'Filter': 'Filtrar',
            'Clear Filters': 'Limpar Filtros',
            'Apply Filters': 'Aplicar Filtros',
            'Export': 'Exportar',
            'From Date': 'Data Inicial',
            'To Date': 'Data Final',
            'All': 'Todos',
            'Show': 'Mostrar',
            'entries': 'entradas',
            'Previous': 'Anterior',
            'Next': 'Próximo',
            'First': 'Primeiro',
            'Last': 'Último',
            'Page': 'Página',
            'of': 'de',
            'Showing': 'Mostrando',
            'to': 'até',
            'entries out of': 'entradas de',
            'total': 'total',
            'Currency': 'Moeda',
            
            // Login
            'Sign in to access your account': 'Faça login para acessar sua conta',
            'Email/Username': 'Email/Nome de usuário',
            'Password': 'Senha',
            'Sign In': 'Entrar',
            'Don\'t have an account? Contact your administrator.': 'Não tem uma conta? Entre em contato com seu administrador.',
            
            // Messages
            'Welcome': 'Bem-vindo',
            'Error': 'Erro',
            'Success': 'Sucesso',
            'Warning': 'Aviso',
            'Info': 'Informação',
            'Please wait...': 'Por favor aguarde...',
            'Operation completed successfully': 'Operação concluída com sucesso',
            'An error occurred': 'Ocorreu um erro',
            'No records found': 'Nenhum registro encontrado',
            'Data loaded successfully': 'Dados carregados com sucesso'
        }
    };

    // Translation system
    window.IsoftTranslation = {
        currentLanguage: 'en',
        
        // Initialize the translation system
        init: function() {
            // Get language from ERPNext user preferences first, then localStorage, then default to English
            this.loadUserLanguage();
            
            // Set up observer for dynamic content changes
            this.setupMutationObserver();
        },

        // Set up mutation observer to detect dynamic content changes
        setupMutationObserver: function() {
            if (typeof MutationObserver !== 'undefined') {
                const self = this;
                const observer = new MutationObserver(function(mutations) {
                    let shouldRetranslate = false;
                    
                    mutations.forEach(function(mutation) {
                        if (mutation.type === 'childList') {
                            // Check if any summary cards were added or modified
                            const addedNodes = Array.from(mutation.addedNodes);
                            addedNodes.forEach(node => {
                                if (node.nodeType === Node.ELEMENT_NODE) {
                                    if (node.classList && (node.classList.contains('summary-card') || 
                                        node.classList.contains('summary-label') ||
                                        node.querySelector && node.querySelector('.summary-label'))) {
                                        shouldRetranslate = true;
                                    }
                                }
                            });
                        }
                    });
                    
                    if (shouldRetranslate) {
                        // Delay retranslation to allow DOM updates to complete
                        setTimeout(() => {
                            self.translateSummaryCards();
                        }, 50);
                    }
                });
                
                // Start observing
                observer.observe(document.body, {
                    childList: true,
                    subtree: true
                });
            }
        },

        // Load user language preference from ERPNext
        loadUserLanguage: function() {
            const self = this;
            
            // Check if frappe is available
            if (typeof frappe !== 'undefined' && frappe.call) {
                frappe.call({
                    method: 'isoft_customer_portal.api.get_user_language',
                    callback: function(r) {
                        if (r.message && r.message.language) {
                            self.currentLanguage = r.message.language;
                        } else {
                            // Fallback to localStorage or default
                            self.currentLanguage = localStorage.getItem('isoft_portal_language') || 'en';
                        }
                        self.translatePage();
                    },
                    error: function() {
                        // Fallback to localStorage or default
                        self.currentLanguage = localStorage.getItem('isoft_portal_language') || 'en';
                        self.translatePage();
                    }
                });
            } else {
                // Fallback if frappe is not available
                this.currentLanguage = localStorage.getItem('isoft_portal_language') || 'en';
                this.translatePage();
            }
        },
        
        // Get translation for a key
        t: function(key, lang = null) {
            const language = lang || this.currentLanguage;
            return translations[language] && translations[language][key] 
                ? translations[language][key] 
                : key;
        },
        
        // Set language and translate page
        setLanguage: function(lang) {
            if (translations[lang]) {
                this.currentLanguage = lang;
                localStorage.setItem('isoft_portal_language', lang);
                
                // Save to ERPNext user preferences
                this.saveUserLanguage(lang);
                
                this.translatePage();
                
                // Update HTML lang attribute
                document.documentElement.lang = lang;
                
                // Trigger custom event for other components to listen
                window.dispatchEvent(new CustomEvent('languageChanged', {
                    detail: { language: lang }
                }));
            }
        },

        // Save user language preference to ERPNext
        saveUserLanguage: function(lang) {
            if (typeof frappe !== 'undefined' && frappe.call) {
                frappe.call({
                    method: 'isoft_customer_portal.api.set_user_language',
                    args: {
                        language: lang
                    },
                    callback: function(r) {
                        if (r.message && r.message.success) {
                            console.log('Language preference saved to user profile');
                        }
                    },
                    error: function(err) {
                        console.error('Failed to save language preference:', err);
                    }
                });
            }
        },
        
        // Translate the entire page
        translatePage: function() {
            // Find all elements with data-translate attribute
            const elements = document.querySelectorAll('[data-translate]');
            elements.forEach(element => {
                const key = element.getAttribute('data-translate');
                const translation = this.t(key);
                
                if (element.tagName === 'INPUT' && (element.type === 'submit' || element.type === 'button')) {
                    element.value = translation;
                } else if (element.hasAttribute('placeholder')) {
                    element.placeholder = translation;
                } else if (element.hasAttribute('title')) {
                    element.title = translation;
                } else {
                    element.textContent = translation;
                }
            });
            
            // Also translate elements with specific IDs or classes that contain text
            this.translateCommonElements();
            
            // Translate dynamic content
            this.translateDynamicContent();
        },

        // Translate dynamic content that might be added via JavaScript
        translateDynamicContent: function() {
            // Translate summary card labels specifically
            this.translateSummaryCards();
            
            // Translate common table headers that might not have data-translate
            const commonTranslations = {
                'Payment Entry': this.t('Payment Number'),
                'Date': this.t('Date'),
                'Type': this.t('Payment Type'),
                'Mode of Payment': this.t('Mode of Payment'),
                'Amount': this.t('Amount'),
                'Reference No': this.t('Reference No'),
                'Status': this.t('Status'),
                'Actions': this.t('Actions'),
                'Print': this.t('Print'),
                'Loading...': this.t('Loading...'),
                'No data available': this.t('No data available'),
                'Apply Filters': this.t('Apply Filters'),
                'Clear Filters': this.t('Clear Filters'),
                'Export Excel': this.t('Export'),
                'Export PDF': this.t('Export'),
                'All Types': this.t('All'),
                'From Date:': this.t('From Date') + ':',
                'To Date:': this.t('To Date') + ':',
                'Type:': this.t('Payment Type') + ':'
            };

            // Apply translations to elements with specific text content
            Object.keys(commonTranslations).forEach(originalText => {
                const elements = document.querySelectorAll('*');
                elements.forEach(element => {
                    // Only translate text nodes, not nested elements
                    if (element.childNodes.length === 1 && 
                        element.childNodes[0].nodeType === Node.TEXT_NODE && 
                        element.childNodes[0].textContent.trim() === originalText) {
                        element.childNodes[0].textContent = commonTranslations[originalText];
                    }
                });
            });
        },

        // Specifically translate summary card labels
        translateSummaryCards: function() {
            // Force translate summary card labels
            const cardLabels = document.querySelectorAll('.summary-label[data-translate]');
            cardLabels.forEach(label => {
                const key = label.getAttribute('data-translate');
                const translation = this.t(key);
                label.textContent = translation;
            });

            // Also handle specific card labels by their content
            const cardTranslations = {
                'Total Entries': this.t('Total Entries'),
                'Total Received': this.t('Total Received'),
                'Total Allocated Amount': this.t('Total Allocated Amount'),
                'Unallocated Amount': this.t('Unallocated Amount'),
                'Total Invoices': this.t('Total Invoices'),
                'Total Amount': this.t('Total Amount'),
                'Outstanding Amount': this.t('Outstanding Amount'),
                'Paid Amount': this.t('Paid Amount')
            };

            Object.keys(cardTranslations).forEach(originalText => {
                const elements = document.querySelectorAll('.summary-label');
                elements.forEach(element => {
                    if (element.textContent.trim() === originalText) {
                        element.textContent = cardTranslations[originalText];
                    }
                });
            });
        },
        
        // Translate common elements that might not have data-translate attribute
        translateCommonElements: function() {
            // Translate navigation items
            const navItems = {
                '#nav-dashboard .nav-text': 'Dashboard',
                '#nav-invoices .nav-text': 'Invoices',
                '#nav-sales-orders .nav-text': 'Sales Orders',
                '#nav-quotations .nav-text': 'Quotations',
                '#nav-delivery-notes .nav-text': 'Delivery Notes',
                '#nav-payment-entries .nav-text': 'Payments',
                '#nav-ledger .nav-text': 'Ledger'
            };
            
            Object.keys(navItems).forEach(selector => {
                const element = document.querySelector(selector);
                if (element) {
                    element.textContent = this.t(navItems[selector]);
                }
            });
            
            // Translate brand text
            const brandText = document.querySelector('.brand-text');
            if (brandText) {
                brandText.textContent = this.t('Customer Portal');
            }
            
            // Translate nav section titles
            const navSectionTitles = document.querySelectorAll('.nav-section-title');
            navSectionTitles.forEach(title => {
                if (title.textContent.trim() === 'Main') {
                    title.textContent = this.t('Main');
                }
            });
        },
        
        // Get all available languages
        getAvailableLanguages: function() {
            return Object.keys(translations);
        },
        
        // Get current language
        getCurrentLanguage: function() {
            return this.currentLanguage;
        }
    };

    // Auto-initialize when DOM is ready
    document.addEventListener('DOMContentLoaded', function() {
        window.IsoftTranslation.init();
    });
    
    // Also initialize if DOM is already ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            window.IsoftTranslation.init();
        });
    } else {
        window.IsoftTranslation.init();
    }

})();
