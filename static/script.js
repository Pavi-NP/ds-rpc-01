// ds-rpc-02/static/script.js - Enhanced Enterprise JavaScript

document.addEventListener('DOMContentLoaded', () => {
    // --- Enhanced Configuration ---
    const CONFIG = {
        API_BASE_URL: '/api',
        ENDPOINTS: {
            USER_INFO: '/api/user-info',
            CHAT: '/api/chat',
            HEALTH: '/api/health',
            METRICS: '/api/metrics'
        },
        RATE_LIMITS: {
            CHAT: 30, // per minute
            AUTH: 10  // per minute
        },
        TIMEOUTS: {
            DEFAULT: 30000,
            CHAT: 60000
        },
        RETRY: {
            MAX_ATTEMPTS: 3,
            DELAY: 1000
        }
    };

    // --- DOM Elements ---
    const loginScreen = document.getElementById('loginScreen');
    const dashboard = document.getElementById('dashboard');
    const loginForm = document.getElementById('loginForm');
    const username = document.getElementById('username');
    const passwordField = document.getElementById('passwordField');
    const password = document.getElementById('password');
    const loginError = document.getElementById('loginError');
    const chatForm = document.getElementById('chatForm');
    const queryInput = document.getElementById('queryInput');
    const chatContainer = document.getElementById('chatContainer');
    const userInfo = document.getElementById('userInfo');
    const roleInfo = document.getElementById('roleInfo');
    const logoutBtn = document.getElementById('logoutBtn');
    const permissionsContainer = document.getElementById('permissions');
    const quickQueriesContainer = document.getElementById('quickQueries');
    const availableFiles = document.getElementById('availableFiles');
    const statusIndicator = document.getElementById('statusIndicator');
    const sendBtn = document.getElementById('sendBtn');

    // --- Enhanced State Management ---
    class AppState {
        constructor() {
            this.user = null;
            this.credentials = null;
            this.isAuthenticated = false;
            this.isConnected = true;
            this.chatHistory = [];
            this.queryCount = 0;
            this.startTime = Date.now();
            this.lastActivity = Date.now();
            this.retryCount = 0;
        }

        setUser(userData, creds) {
            this.user = userData;
            this.credentials = creds;
            this.isAuthenticated = true;
            this.lastActivity = Date.now();
            window.currentCredentials = creds; // For connection monitoring
        }

        clearUser() {
            this.user = null;
            this.credentials = null;
            this.isAuthenticated = false;
            this.chatHistory = [];
            this.queryCount = 0;
            window.currentCredentials = null;
        }

        addChatMessage(message) {
            this.chatHistory.push({
                ...message,
                timestamp: Date.now()
            });
            this.lastActivity = Date.now();
        }

        incrementQueryCount() {
            this.queryCount++;
            this.lastActivity = Date.now();
        }
    }

    const appState = new AppState();

    // --- Enhanced Role Configuration ---
    const ROLE_CONFIG = {
        'engineering': {
            color: 'blue',
            icon: '⚙️',
            permissions: ['Technical Architecture', 'Development Processes', 'Operational Guidelines', 'System Documentation'],
            quickQueries: [
                "What technologies are used in the data layer and their roles?",
                "How does FinSolve ensure high availability for critical services?",
                "What data protection mechanisms are used for PII?",
                "What is the commit message convention used by engineers?",
                "How does FinSolve manage Kubernetes configurations?"
            ],
            files: ['engineering_master.pdf', 'system_architecture.md', 'dev_guidelines.md', 'operational_guide.pdf', 'tech_stack.yml']
        },
        'marketing': {
            color: 'green',
            icon: '📈',
            permissions: ['Campaign Performance', 'Customer Feedback', 'Sales Metrics', 'Market Analysis'],
            quickQueries: [
                "What was the overall ROI for marketing campaigns in 2024 across all quarters?",
                "What led to the slower-than-expected growth in Colombia during Q3 2024?",
                "What was the impact of loyalty programs on customer retention across 2024?",
                "How did spending on traditional media differ from digital advertising across 2024?",
                "How can marketing efforts be improved to enhance ROI in future campaigns?"
            ],
            files: ['q4_campaign_report.pdf', 'customer_feedback_2024.csv', 'sales_metrics.xlsx', 'market_analysis.pdf', 'competitor_analysis.pdf']
        },
        'finance': {
            color: 'yellow',
            icon: '💰',
            permissions: ['Financial Reports', 'Budget Analysis', 'Expense Tracking', 'Revenue Forecasting'],
            quickQueries: [
                "How did revenue growth progress across each quarter of 2024?",
                "How did net income change year-over-year in 2024?",
                "How does the company’s operating expense to revenue ratio compare to industry standards?",
                "How did increased software subscription costs affect overall profitability?",
                "What strategies were implemented to mitigate rising vendor costs?"
            ],
            files: ['q4_financial_report.pdf', 'budget_analysis.xlsx', 'expense_breakdown.csv', 'revenue_forecast.pdf', 'tax_documents.pdf']
        },
        'hr': {
            color: 'purple',
            icon: '👥',
            permissions: ['Employee Records', 'Performance Reviews', 'Payroll Data', 'HR Policies'],
            quickQueries: [
                "How many employees are currently in the company?",
                "Can you give me a breakdown of employee distribution by department?",
                "What’s the attrition rate across different departments?",
                "Are single employees more likely to leave than married ones?",
                "Which job roles have the highest job satisfaction?"
            ],
            files: ['employee_handbook.pdf', 'attendance_records.csv', 'performance_reviews.xlsx', 'hr_policies.md', 'benefits_guide.pdf']
        },
        'c-level': {
            color: 'red',
            icon: '👑',
            permissions: ['All Company Data', 'Executive Reports', 'Strategic Planning', 'Board Materials'],
            quickQueries: [
                "What is the resignation process?",
                "How do I raise payroll discrepancies?",
                "What compliance frameworks does FinSolve adhere to?",
                "What AI/ML capabilities are planned for the platform?",
                "How did increased software subscription costs affect overall profitability?"
            ],
            files: ['All departmental files', 'executive_dashboard.pdf', 'strategic_plan.pdf', 'board_materials.pptx', 'kpi_dashboard.xlsx']
        },
        'employee': {
            color: 'gray',
            icon: '👤',
            permissions: ['Company Policies', 'General Information', 'Events & News', 'Employee Benefits'],
            quickQueries: [
                "What types of leave am I entitled to?",
                "What are the standard working hours?",
                "What is the company’s stance on workplace harassment?",
                "What insurance and wellness programs are available?",
                "What training programs are available?"
            ],
            files: ['company_policies.pdf', 'employee_benefits.pdf', 'events_calendar.ics', 'code_of_conduct.md', 'faq.md']
        }
    };

    // --- Enhanced Utility Functions ---
    const utils = {
        // API request wrapper with retry logic
        async apiRequest(url, options = {}) {
            const defaultOptions = {
                timeout: CONFIG.TIMEOUTS.DEFAULT,
                headers: {
                    'Content-Type': 'application/json',
                    ...(appState.credentials && { 'Authorization': `Basic ${appState.credentials}` })
                }
            };

            const finalOptions = { ...defaultOptions, ...options };
            
            for (let attempt = 1; attempt <= CONFIG.RETRY.MAX_ATTEMPTS; attempt++) {
                try {
                    const controller = new AbortController();
                    const timeoutId = setTimeout(() => controller.abort(), finalOptions.timeout);
                    
                    const response = await fetch(url, {
                        ...finalOptions,
                        signal: controller.signal
                    });
                    
                    clearTimeout(timeoutId);
                    
                    if (!response.ok) {
                        if (response.status === 429) {
                            throw new Error('Rate limit exceeded. Please slow down.');
                        }
                        if (response.status === 401) {
                            appState.clearUser();
                            showLogin();
                            throw new Error('Authentication required');
                        }
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }
                    
                    appState.retryCount = 0; // Reset on success
                    return response;
                    
                } catch (error) {
                    console.warn(`API request attempt ${attempt} failed:`, error);
                    
                    if (attempt === CONFIG.RETRY.MAX_ATTEMPTS) {
                        appState.retryCount++;
                        throw error;
                    }
                    
                    await this.delay(CONFIG.RETRY.DELAY * attempt);
                }
            }
        },

        // Enhanced error handling
        handleError(error, context = '') {
            console.error(`Error in ${context}:`, error);
            
            let userMessage = 'An unexpected error occurred.';
            
            if (error.message.includes('Rate limit')) {
                userMessage = 'You\'re sending requests too quickly. Please wait a moment.';
            } else if (error.message.includes('timeout') || error.name === 'AbortError') {
                userMessage = 'Request timed out. Please check your connection and try again.';
            } else if (error.message.includes('Authentication')) {
                userMessage = 'Please log in again to continue.';
            } else if (error.message.includes('Network')) {
                userMessage = 'Network error. Please check your connection.';
                appState.isConnected = false;
                updateConnectionStatus(false);
            }
            
            this.showNotification(userMessage, 'error');
            return userMessage;
        },

        // Enhanced notification system
        showNotification(message, type = 'info', duration = 5000) {
            const notification = document.createElement('div');
            notification.className = `notification ${type} fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 max-w-sm transform translate-x-full transition-transform duration-300`;
            
            const icons = {
                success: '✅',
                error: '❌',
                warning: '⚠️',
                info: 'ℹ️'
            };
            
            notification.innerHTML = `
                <div class="flex items-center">
                    <span class="mr-2">${icons[type] || icons.info}</span>
                    <span class="flex-1">${message}</span>
                    <button class="ml-2 text-lg" onclick="this.parentElement.parentElement.remove()">×</button>
                </div>
            `;
            
            document.body.appendChild(notification);
            
            // Slide in
            setTimeout(() => {
                notification.style.transform = 'translateX(0)';
            }, 100);
            
            // Auto remove
            setTimeout(() => {
                notification.style.transform = 'translateX(full)';
                setTimeout(() => {
                    if (notification.parentElement) {
                        notification.remove();
                    }
                }, 300);
            }, duration);
        },

        // Utility functions
        delay: (ms) => new Promise(resolve => setTimeout(resolve, ms)),
        
        formatTimestamp: (timestamp) => {
            return new Date(timestamp).toLocaleTimeString([], { 
                hour: '2-digit', 
                minute: '2-digit' 
            });
        },

        sanitizeInput: (input) => {
            const div = document.createElement('div');
            div.textContent = input;
            return div.innerHTML;
        },

        debounce: (func, wait) => {
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
    };

    // --- Enhanced Authentication ---
    async function authenticateUser(username, password) {
        try {
            const credentials = btoa(`${username}:${password}`);
            
            const response = await utils.apiRequest(CONFIG.ENDPOINTS.USER_INFO, {
                headers: { 'Authorization': `Basic ${credentials}` }
            });
            
            const userData = await response.json();
            appState.setUser(userData, credentials);
            
            // Store in session storage for persistence
            sessionStorage.setItem('userCredentials', credentials);
            sessionStorage.setItem('userData', JSON.stringify(userData));
            
            return userData;
        } catch (error) {
            throw new Error('Invalid credentials or server error');
        }
    }

    // --- Enhanced UI Functions ---
    function showLogin() {
        dashboard.classList.add('hidden');
        loginScreen.classList.remove('hidden');
        loginScreen.classList.add('fade-in');
        
        // Reset form
        username.value = '';
        password.value = '';
        passwordField.classList.add('hidden');
        hideError();
        
        // Clear chat
        clearChat();
    }

    function showDashboard() {
        loginScreen.classList.add('hidden');
        dashboard.classList.remove('hidden');
        dashboard.classList.add('fade-in');
        
        updateSidebar();
        addWelcomeMessage();
        updateConnectionStatus(true);
    }

    function updateSidebar() {
        if (!appState.user || !ROLE_CONFIG[appState.user.role]) return;

        const config = ROLE_CONFIG[appState.user.role];
        
        // Update user info with enhanced display
        userInfo.textContent = appState.user.username;
        roleInfo.textContent = `${appState.user.title || appState.user.role} (${appState.user.role})`;
        
        // Update permissions with enhanced styling
        permissionsContainer.innerHTML = config.permissions.map((permission, index) => 
            `<span class="permission-tag ${config.color} inline-block text-xs font-medium px-2 py-1 rounded-full transition-all duration-200 animate-fade-in" style="animation-delay: ${index * 0.1}s">
                ${config.icon} ${permission}
            </span>`
        ).join('');

        // Update quick queries with enhanced interaction
        quickQueriesContainer.innerHTML = config.quickQueries.map((query, index) =>
            `<button class="quick-query-btn w-full text-left p-3 text-sm text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md transition-all duration-200 animate-slide-in-up" style="animation-delay: ${index * 0.1}s" data-query="${utils.sanitizeInput(query)}">
                <span class="block font-medium">${query}</span>
            </button>`
        ).join('');
        
        // Update available files with metadata
        availableFiles.innerHTML = config.files.map((file, index) => 
            `<div class="text-xs py-1 animate-fade-in" style="animation-delay: ${index * 0.05}s">
                <span class="text-primary">📄</span> ${file}
            </div>`
        ).join('');
    }

    function addWelcomeMessage() {
        const config = ROLE_CONFIG[appState.user.role];
        const welcomeMsg = `Welcome back, **${appState.user.username}**! 🎉

As a **${appState.user.title || appState.user.role}**, you have access to:
${config.permissions.map(p => `• ${p}`).join('\n')}

I'm your RAG-powered assistant with access to **${config.files.length} documents** in your scope. 

💡 **Quick tip**: Use the suggested queries on the left, or ask me anything about your department's data!

🔒 **Security**: All responses are tailored to your access level and include source references.`;
        
        addMessage('bot', welcomeMsg);
    }

    function addMessage(sender, text, sources = [], metadata = {}) {
        const messageWrapper = document.createElement('div');
        messageWrapper.classList.add('message-wrapper', 'fade-in');

        const timestamp = utils.formatTimestamp(Date.now());
        const messageId = `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

        if (sender === 'user') {
            messageWrapper.innerHTML = `
                <div class="flex justify-end w-full">
                    <div class="message-bubble user max-w-lg">
                        <p class="mb-2">${utils.sanitizeInput(text)}</p>
                        <div class="text-xs opacity-75">${timestamp}</div>
                    </div>
                    <div class="w-8 h-8 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center font-bold text-sm text-white flex-shrink-0 ml-3">
                        ${appState.user.username.charAt(0).toUpperCase()}
                    </div>
                </div>
            `;
        } else {
            const parsedText = marked.parse(text);
            
            let sourcesHtml = '';
            if (sources && sources.length > 0) {
                sourcesHtml = `
                    <div class="mt-4 space-y-2">
                        <div class="text-sm font-semibold text-gray-700 dark:text-gray-300 flex items-center">
                            📚 <span class="ml-1">Sources (${sources.length})</span>
                        </div>
                        ${sources.map((source, index) => `
                            <div class="source-ref animate-slide-in-up" style="animation-delay: ${index * 0.1}s">
                                <div class="source-filename">${source.filename}</div>
                                <div class="source-department">${source.department}</div>
                                <div class="source-summary">${source.summary}</div>
                                ${source.relevance_score ? `<div class="text-xs text-primary mt-1">Relevance: ${(source.relevance_score * 100).toFixed(1)}%</div>` : ''}
                            </div>
                        `).join('')}
                    </div>
                `;
            }

            let metadataHtml = '';
            if (metadata && Object.keys(metadata).length > 0) {
                metadataHtml = `
                    <div class="mt-3 p-2 bg-gray-50 dark:bg-gray-800 rounded text-xs text-gray-600 dark:text-gray-400">
                        ${metadata.processing_time_ms ? `⚡ ${metadata.processing_time_ms}ms` : ''}
                        ${metadata.rag_confidence ? ` • 🎯 ${(metadata.rag_confidence * 100).toFixed(1)}% confidence` : ''}
                        ${metadata.sources_found ? ` • 📖 ${metadata.sources_found} sources` : ''}
                    </div>
                `;
            }
            
            messageWrapper.innerHTML = `
                <div class="flex w-full">
                    <div class="w-8 h-8 rounded-full bg-gradient-to-r from-indigo-500 to-purple-600 flex items-center justify-center text-white font-bold text-sm flex-shrink-0 mr-3">
                        AI
                    </div>
                    <div class="message-bubble bot flex-1">
                        <div class="prose dark:prose-invert prose-sm max-w-none">
                            ${parsedText}
                        </div>
                        ${sourcesHtml}
                        ${metadataHtml}
                        <div class="text-xs opacity-75 mt-2">${timestamp}</div>
                    </div>
                </div>
            `;
        }
        
        chatContainer.appendChild(messageWrapper);
        chatContainer.scrollTop = chatContainer.scrollHeight;
        
        // Add to state
        appState.addChatMessage({
            id: messageId,
            sender,
            text,
            sources,
            metadata,
            timestamp: Date.now()
        });
    }

    function showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.id = 'typingIndicator';
        typingDiv.classList.add('flex', 'items-center', 'gap-3', 'justify-start', 'fade-in');
        typingDiv.innerHTML = `
            <div class="w-8 h-8 rounded-full bg-gradient-to-r from-indigo-500 to-purple-600 flex items-center justify-center text-white font-bold text-sm flex-shrink-0">AI</div>
            <div class="bg-white dark:bg-gray-700 p-3 rounded-lg flex items-center space-x-1">
                <span class="typing-indicator"></span>
                <span class="typing-indicator"></span>
                <span class="typing-indicator"></span>
                <span class="ml-2 text-sm text-gray-500">Thinking...</span>
            </div>
        `;
        chatContainer.appendChild(typingDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    function removeTypingIndicator() {
        const indicator = document.getElementById('typingIndicator');
        if (indicator) {
            indicator.style.opacity = '0';
            setTimeout(() => indicator.remove(), 200);
        }
    }

    function clearChat() {
        chatContainer.innerHTML = `
            <div class="text-center text-gray-500 dark:text-gray-400">
                <div class="inline-flex items-center justify-center w-12 h-12 bg-primary/10 rounded-full mb-4">
                    <svg class="w-6 h-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-4l-4 4z"></path>
                    </svg>
                </div>
                <p>Welcome! Ask me anything within your access permissions and I'll provide detailed insights with source references.</p>
            </div>
        `;
        appState.chatHistory = [];
    }

    function showError(message) {
        loginError.textContent = message;
        loginError.classList.remove('hidden');
        loginError.classList.add('animate-shake');
        setTimeout(() => loginError.classList.remove('animate-shake'), 500);
    }

    function hideError() {
        loginError.classList.add('hidden');
        loginError.textContent = '';
    }

    function updateConnectionStatus(connected) {
        appState.isConnected = connected;
        if (statusIndicator) {
            statusIndicator.className = connected 
                ? 'w-2 h-2 bg-green-500 rounded-full mr-2 status-indicator online'
                : 'w-2 h-2 bg-red-500 rounded-full mr-2 status-indicator offline';
        }
    }

    // --- Enhanced Event Listeners ---
    
    // Enhanced login form handling
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        hideError();
        
        const usernameValue = username.value;
        const passwordValue = password.value;
        
        if (!usernameValue || !passwordValue) {
            showError('Please enter both username and password.');
            return;
        }
        
        const submitBtn = loginForm.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="loading-spinner mr-2"></span>Authenticating...';
        
        try {
            await authenticateUser(usernameValue, passwordValue);
            utils.showNotification('Login successful! Welcome back.', 'success');
            showDashboard();
        } catch (error) {
            showError(utils.handleError(error, 'login'));
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalText;
        }
    });

    // Enhanced username selection
    username.addEventListener('change', (e) => {
        const passwordHelpers = {
            'Peter': 'pete123',
            'Tony': 'password123',
            'Bruce': 'securepass',
            'Sam': 'financepass',
            'Sid': 'sidpass123',
            'Natasha': 'hrpass123',
            'Alex': 'ceopass',
            'John': 'employeepass'
        };
        
        if (e.target.value) {
            passwordField.classList.remove('hidden');
            password.focus();
            
            if (passwordHelpers[e.target.value]) {
                password.placeholder = `Demo password: ${passwordHelpers[e.target.value]}`;
            }
        } else {
            passwordField.classList.add('hidden');
            password.value = '';
            password.placeholder = 'Enter your password';
        }
        hideError();
    });

    // Enhanced logout handling
    logoutBtn.addEventListener('click', () => {
        appState.clearUser();
        sessionStorage.removeItem('userCredentials');
        sessionStorage.removeItem('userData');
        utils.showNotification('Logged out successfully', 'info');
        showLogin();
    });

    // Enhanced chat form handling
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const message = queryInput.value.trim();
        if (!message || !appState.isAuthenticated) return;
        
        // Rate limiting check
        if (appState.queryCount >= CONFIG.RATE_LIMITS.CHAT) {
            utils.showNotification('Rate limit reached. Please wait before sending more messages.', 'warning');
            return;
        }
        
        addMessage('user', message);
        queryInput.value = '';
        appState.incrementQueryCount();
        
        // Update send button state
        sendBtn.disabled = true;
        sendBtn.innerHTML = '<span class="loading-spinner mr-2"></span>Sending...';
        
        showTypingIndicator();
        
        try {
            const detailedResponse = document.getElementById('detailedResponse')?.checked || false;
            const includeSummary = document.getElementById('includeSummary')?.checked || true;
            
            const requestBody = {
                message: message,
                options: {
                    include_sources: true,
                    detailed_response: detailedResponse,
                    max_sources: 3,
                    response_format: 'markdown'
                },
                context: {
                    user_role: appState.user.role,
                    session_id: appState.startTime
                }
            };
            
            const response = await utils.apiRequest(CONFIG.ENDPOINTS.CHAT, {
                method: 'POST',
                body: JSON.stringify(requestBody),
                timeout: CONFIG.TIMEOUTS.CHAT
            });
            
            const data = await response.json();
            
            removeTypingIndicator();
            addMessage('bot', data.response, data.sources || [], data.metadata || {});
            
        } catch (error) {
            removeTypingIndicator();
            addMessage('bot', utils.handleError(error, 'chat'));
        } finally {
            sendBtn.disabled = false;
            sendBtn.innerHTML = `
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path>
                </svg>
                Send
            `;
        }
    });

    // Enhanced quick query handling
    quickQueriesContainer.addEventListener('click', (e) => {
        const btn = e.target.closest('.quick-query-btn');
        if (btn) {
            const query = btn.dataset.query || btn.textContent.trim();
            queryInput.value = query;
            queryInput.focus();
            
            // Auto-submit after a brief delay for better UX
            setTimeout(() => {
                chatForm.dispatchEvent(new Event('submit'));
            }, 300);
        }
    });

    // Enhanced keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Focus on input when typing (if not already focused)
        if (appState.isAuthenticated && !e.ctrlKey && !e.metaKey && !e.altKey) {
            if (e.key.length === 1 && document.activeElement !== queryInput) {
                queryInput.focus();
            }
        }
        
        // Escape to focus on input
        if (e.key === 'Escape' && appState.isAuthenticated) {
            queryInput.focus();
            queryInput.select();
        }
    });

    // Auto-save draft
    const saveDraft = utils.debounce(() => {
        if (queryInput.value.trim()) {
            sessionStorage.setItem('chatDraft', queryInput.value);
        } else {
            sessionStorage.removeItem('chatDraft');
        }
    }, 1000);

    queryInput.addEventListener('input', saveDraft);

    // --- Health Monitoring ---
    async function monitorHealth() {
        try {
            await utils.apiRequest(CONFIG.ENDPOINTS.HEALTH);
            updateConnectionStatus(true);
        } catch (error) {
            console.warn('Health check failed:', error);
            updateConnectionStatus(false);
        }
    }

    // Regular health checks
    setInterval(monitorHealth, 30000);

    // --- Session Management ---
    function checkSession() {
        const savedCredentials = sessionStorage.getItem('userCredentials');
        const savedUserData = sessionStorage.getItem('userData');
        
        if (savedCredentials && savedUserData) {
            try {
                const userData = JSON.parse(savedUserData);
                appState.setUser(userData, savedCredentials);
                
                // Verify session is still valid
                utils.apiRequest(CONFIG.ENDPOINTS.USER_INFO)
                    .then(() => {
                        showDashboard();
                        
                        // Restore draft if exists
                        const draft = sessionStorage.getItem('chatDraft');
                        if (draft) {
                            queryInput.value = draft;
                        }
                    })
                    .catch(() => {
                        sessionStorage.removeItem('userCredentials');
                        sessionStorage.removeItem('userData');
                        showLogin();
                    });
            } catch (error) {
                console.error('Session restore failed:', error);
                showLogin();
            }
        } else {
            showLogin();
        }
    }

    // --- Activity Tracking ---
    function trackActivity() {
        appState.lastActivity = Date.now();
    }

    ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'].forEach(event => {
        document.addEventListener(event, trackActivity, { passive: true });
    });

    // Auto-logout after inactivity (30 minutes)
    setInterval(() => {
        if (appState.isAuthenticated && Date.now() - appState.lastActivity > 30 * 60 * 1000) {
            utils.showNotification('Session expired due to inactivity', 'warning');
            logoutBtn.click();
        }
    }, 60000);

    // --- Initialization ---
    console.log('🚀 Peter Pandey\'s RAG Assistant initialized');
    checkSession();
    
    // Initialize health monitoring
    monitorHealth();
    
    // Add some visual flair
    if (Math.random() < 0.1) { // 10% chance
        console.log(`
    ╭─────────────────────────────────╮
    │  🤖 RAG Assistant by Peter Pandey │
    │  Enterprise RBAC System v2.0    │
    ╰─────────────────────────────────╯
        `);
    }
});
