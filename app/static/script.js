// ds-rpc-01/app/static/script.js

document.addEventListener('DOMContentLoaded', () => {
    // --- DOM Elements ---
    const loginScreen = document.getElementById('loginScreen');
    const dashboard = document.getElementById('dashboard');
    const loginForm = document.getElementById('loginForm');
    const loginError = document.getElementById('loginError');
    const chatForm = document.getElementById('chatForm');
    const queryInput = document.getElementById('queryInput');
    const chatContainer = document.getElementById('chatContainer');
    const userInfo = document.getElementById('userInfo');
    const logoutBtn = document.getElementById('logoutBtn');
    const permissionsContainer = document.getElementById('permissions');
    const quickQueriesContainer = document.getElementById('quickQueries');

    // --- State ---
    let user = null;
    let credentials = null; // To store 'username:password' for Basic Auth

    // --- Role-based configurations ---
    const ROLE_CONFIG = {
        'engineering': {
            color: 'blue',
            permissions: ['Financial Reports', 'Marketing Expenses', 'Tech Architecture'],
            quickQueries: [
                "Summarize the engineering master doc.",
                "What are the operational guidelines?"
            ]
        },
        'marketing': {
            color: 'green',
            permissions: ['Campaign Performance', 'Customer Feedback', 'Sales Metrics'],
            quickQueries: [
                "What was the campaign performance for Q4 2024?",
                "Summarize the latest market report."
            ]
        },
        'finance': {
            color: 'yellow',
            permissions: ['Financial Reports', 'Marketing Expenses', 'Reimbursements'],
            quickQueries: [
                "Give me the key points from the financial summary.",
                "What's in the quarterly financial report?"
            ]
        },
        'hr': {
            color: 'purple',
            permissions: ['Employee Data', 'Attendance Records', 'Payroll'],
            quickQueries: [
                "What does the employee handbook say about vacation?",
                "Summarize the HR data."
            ]
        },
        'c-level': {
            color: 'red',
            permissions: ['All Company Data'],
            quickQueries: [
                "Summarize the financial report and the marketing performance for Q4 2024.",
                "What are the key takeaways from the engineering master doc?"
            ]
        },
        'employee': {
            color: 'gray',
            permissions: ['General Policies', 'Company Events', 'FAQs'],
            quickQueries: [
                "What is the company's work-from-home policy?",
                "Tell me about upcoming company events."
            ]
        }
    };

    // --- Functions ---

    const showDashboard = () => {
        loginScreen.classList.add('hidden');
        dashboard.classList.remove('hidden');
        dashboard.classList.add('fade-in');
        updateSidebar();
        addMessage('bot', `Welcome, ${user.username}! As a member of the ${user.role.charAt(0).toUpperCase() + user.role.slice(1)} team, you can ask me questions based on your access permissions. How can I help you today?`);
    };

    const showLogin = () => {
        dashboard.classList.add('hidden');
        loginScreen.classList.remove('hidden');
        loginScreen.classList.add('fade-in');
        user = null;
        credentials = null;
        sessionStorage.removeItem('userCredentials');
        queryInput.value = '';
        chatContainer.innerHTML = '';
    };

    const updateSidebar = () => {
        if (!user || !ROLE_CONFIG[user.role]) return;

        const config = ROLE_CONFIG[user.role];
        userInfo.textContent = `${user.username} (${user.role})`;
        
        // Render permissions
        permissionsContainer.innerHTML = config.permissions.map(p => 
            `<span class="inline-block bg-${config.color}-100 text-${config.color}-800 text-xs font-medium mr-2 px-2.5 py-1.5 rounded-full dark:bg-${config.color}-900 dark:text-${config.color}-300">${p}</span>`
        ).join('');

        // Render quick queries
        quickQueriesContainer.innerHTML = config.quickQueries.map(q =>
            `<button class="quick-query-btn w-full text-left p-2 text-sm text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md">${q}</button>`
        ).join('');
    };
    
    const addMessage = (sender, text) => {
        const messageWrapper = document.createElement('div');
        messageWrapper.classList.add('flex', 'items-start', 'gap-3', 'fade-in');

        if (sender === 'user') {
            messageWrapper.classList.add('justify-end');
            messageWrapper.innerHTML = `
                <div class="bg-indigo-600 text-white p-3 rounded-lg max-w-lg">
                    <p>${text}</p>
                </div>
                <div class="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center font-bold text-sm text-gray-600 flex-shrink-0">
                    ${user.username.charAt(0).toUpperCase()}
                </div>
            `;
        } else {
            messageWrapper.classList.add('justify-start');
            // Use marked.js to parse Markdown content from the bot
            const parsedText = marked.parse(text);
            messageWrapper.innerHTML = `
                <div class="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center text-white font-bold text-sm flex-shrink-0">
                    AI
                </div>
                <div class="bg-white dark:bg-gray-700 p-3 rounded-lg max-w-lg prose dark:prose-invert prose-sm">
                    ${parsedText}
                </div>
            `;
        }
        chatContainer.appendChild(messageWrapper);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    };

    const showTypingIndicator = () => {
        const typingDiv = document.createElement('div');
        typingDiv.id = 'typingIndicator';
        typingDiv.classList.add('flex', 'items-center', 'gap-3', 'justify-start');
        typingDiv.innerHTML = `
            <div class="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center text-white font-bold text-sm flex-shrink-0">AI</div>
            <div class="bg-white dark:bg-gray-700 p-3 rounded-lg flex items-center space-x-1.5">
                <span class="typing-indicator"></span>
                <span class="typing-indicator"></span>
                <span class="typing-indicator"></span>
            </div>
        `;
        chatContainer.appendChild(typingDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    };

    const removeTypingIndicator = () => {
        const indicator = document.getElementById('typingIndicator');
        if (indicator) {
            indicator.remove();
        }
    };

    // --- Event Listeners ---

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        loginError.textContent = '';
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        if (!username || !password) {
            loginError.textContent = 'Please enter both username and password.';
            return;
        }

        credentials = btoa(`${username}:${password}`); // Base64 encode for Basic Auth

        try {
            const response = await fetch('/api/user-info', {
                headers: { 'Authorization': `Basic ${credentials}` }
            });

            if (response.ok) {
                user = await response.json();
                sessionStorage.setItem('userCredentials', credentials);
                showDashboard();
            } else {
                loginError.textContent = 'Invalid username or password.';
                credentials = null;
            }
        } catch (error) {
            loginError.textContent = 'Could not connect to the server.';
            console.error('Login error:', error);
        }
    });

    logoutBtn.addEventListener('click', showLogin);

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const message = queryInput.value.trim();
        if (!message) return;

        addMessage('user', message);
        queryInput.value = '';
        showTypingIndicator();

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Basic ${credentials}`
                },
                body: JSON.stringify({ message: message })
            });
            
            removeTypingIndicator();

            if (response.ok) {
                const data = await response.json();
                addMessage('bot', data.response);
            } else {
                addMessage('bot', 'Sorry, I encountered an error. Please try again.');
            }
        } catch (error) {
            removeTypingIndicator();
            addMessage('bot', 'Could not connect to the server.');
            console.error('Chat error:', error);
        }
    });
    
    quickQueriesContainer.addEventListener('click', (e) => {
        if (e.target.classList.contains('quick-query-btn')) {
            const query = e.target.textContent;
            queryInput.value = query;
            chatForm.dispatchEvent(new Event('submit'));
        }
    });

    // --- Initialization ---
    const savedCredentials = sessionStorage.getItem('userCredentials');
    if (savedCredentials) {
        credentials = savedCredentials;
        fetch('/api/user-info', { headers: { 'Authorization': `Basic ${credentials}` } })
            .then(response => {
                if (response.ok) return response.json();
                throw new Error('Session expired');
            })
            .then(userData => {
                user = userData;
                showDashboard();
            })
            .catch(() => {
                showLogin();
            });
    }
});
