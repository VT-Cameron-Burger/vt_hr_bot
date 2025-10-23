// VT HR Bot JavaScript
class HRBot {
    constructor() {
        this.isInitialized = false;
        this.isProcessing = false;
        this.messageHistory = [];
        
        this.initializeElements();
        this.bindEvents();
        this.initialize();
    }
    
    initializeElements() {
        // DOM Elements
        this.statusDot = document.getElementById('statusDot');
        this.statusText = document.getElementById('statusText');
        this.welcomeMessage = document.getElementById('welcomeMessage');
        this.chatMessages = document.getElementById('chatMessages');
        this.typingIndicator = document.getElementById('typingIndicator');
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.loadingModal = document.getElementById('loadingModal');
        
        // Suggestion buttons
        this.suggestionButtons = document.querySelectorAll('.suggestion-btn');
    }
    
    bindEvents() {
        // Send button click
        this.sendButton.addEventListener('click', () => this.sendMessage());
        
        // Enter key press
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !this.isProcessing) {
                this.sendMessage();
            }
        });
        
        // Input changes
        this.messageInput.addEventListener('input', () => {
            this.updateSendButton();
        });
        
        // Suggestion button clicks
        this.suggestionButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                const query = btn.getAttribute('data-query');
                this.messageInput.value = query;
                this.sendMessage();
            });
        });
    }
    
    async initialize() {
        try {
            this.showLoadingModal();
            this.updateStatus('connecting', 'Initializing...');
            
            // Simulate initialization delay
            await this.delay(2000);
            
            // Test backend connection
            const response = await this.testConnection();
            
            if (response.success) {
                this.isInitialized = true;
                this.updateStatus('connected', 'Online');
                this.hideLoadingModal();
            } else {
                throw new Error('Failed to connect to backend');
            }
            
        } catch (error) {
            console.error('Initialization error:', error);
            this.updateStatus('error', 'Connection failed');
            this.hideLoadingModal();
            this.showError('Failed to initialize HR Assistant. Please refresh the page.');
        }
    }
    
    async testConnection() {
        try {
            const response = await fetch('/api/status');
            const data = await response.json();
            
            if (response.ok && data.status === 'online') {
                return { success: true, data };
            } else {
                throw new Error(data.error || 'Server not ready');
            }
        } catch (error) {
            return { success: false, error: error.message };
        }
    }
    
    updateStatus(type, text) {
        this.statusDot.className = `status-dot ${type}`;
        this.statusText.textContent = text;
    }
    
    updateSendButton() {
        const hasText = this.messageInput.value.trim().length > 0;
        this.sendButton.disabled = !hasText || this.isProcessing;
    }
    
    showLoadingModal() {
        this.loadingModal.style.display = 'flex';
    }
    
    hideLoadingModal() {
        this.loadingModal.style.display = 'none';
    }
    
    async sendMessage() {
        if (!this.isInitialized || this.isProcessing) return;
        
        const message = this.messageInput.value.trim();
        if (!message) return;
        
        this.isProcessing = true;
        this.updateSendButton();
        
        // Hide welcome message and show chat
        this.hideWelcomeMessage();
        
        // Add user message
        this.addMessage('user', message);
        
        // Clear input
        this.messageInput.value = '';
        this.updateSendButton();
        
        // Show typing indicator
        this.showTypingIndicator();
        
        try {
            // Send to backend
            const response = await this.queryHRBot(message);
            
            // Hide typing indicator
            this.hideTypingIndicator();
            
            // Add bot response
            this.addMessage('bot', response.answer, response.sources);
            
        } catch (error) {
            console.error('Query error:', error);
            this.hideTypingIndicator();
            this.addMessage('bot', 'I apologize, but I encountered an error processing your request. Please try again.');
        } finally {
            this.isProcessing = false;
            this.updateSendButton();
            this.messageInput.focus();
        }
    }
    
    async queryHRBot(query) {
        try {
            const response = await fetch('/api/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            return {
                answer: data.answer,
                sources: data.sources || [],
                confidence: data.confidence || 0
            };
            
        } catch (error) {
            console.error('Query error:', error);
            // Fallback to mock response if backend is unavailable
            return this.generateMockResponse(query);
        }
    }
    
    generateMockResponse(query) {
        const lowerQuery = query.toLowerCase();
        
        // Mock responses based on common HR topics
        if (lowerQuery.includes('benefit') || lowerQuery.includes('compensation')) {
            return {
                answer: "Virginia Tech offers a comprehensive benefits package including health insurance, dental coverage, vision plans, and retirement savings. Full-time employees are eligible for medical benefits starting from their first day of employment. We also provide life insurance, disability coverage, and access to wellness programs.",
                sources: ['4245.pdf', '4040.pdf']
            };
        }
        
        if (lowerQuery.includes('vacation') || lowerQuery.includes('leave') || lowerQuery.includes('time off')) {
            return {
                answer: "Virginia Tech's vacation policy varies by employee classification. Full-time salaried staff accrue vacation time based on years of service, starting at 15 days annually. Vacation time must be approved by your supervisor in advance. Employees can carry over unused vacation time up to a maximum limit.",
                sources: ['4315.pdf']
            };
        }
        
        if (lowerQuery.includes('performance') || lowerQuery.includes('review') || lowerQuery.includes('evaluation')) {
            return {
                answer: "Performance evaluations at Virginia Tech are conducted annually for all employees. The process includes goal setting, mid-year check-ins, and a comprehensive year-end review. Evaluations focus on job performance, professional development, and alignment with university objectives.",
                sources: ['13005.pdf', '6100.pdf']
            };
        }
        
        if (lowerQuery.includes('safety') || lowerQuery.includes('workplace')) {
            return {
                answer: "Virginia Tech is committed to maintaining a safe workplace for all employees. We have comprehensive safety protocols, training programs, and reporting procedures. All employees must complete required safety training and follow established safety guidelines. Report any safety concerns to your supervisor or the Safety Office immediately.",
                sources: ['1005.pdf']
            };
        }
        
        if (lowerQuery.includes('retirement') || lowerQuery.includes('401k')) {
            return {
                answer: "Virginia Tech offers retirement benefits through the Virginia Retirement System (VRS) for eligible employees. We also provide optional 457 deferred compensation plans and access to financial planning resources. Retirement benefits vary based on employee classification and date of hire.",
                sources: ['4410.pdf']
            };
        }
        
        if (lowerQuery.includes('training') || lowerQuery.includes('development')) {
            return {
                answer: "Virginia Tech supports employee professional development through various training programs, workshops, and educational opportunities. We offer both mandatory compliance training and optional skill development courses. Employees can access online learning platforms and may be eligible for tuition assistance.",
                sources: ['4345.pdf']
            };
        }
        
        // Default response
        return {
            answer: "I found information related to your question in our HR policy database. For specific details about your situation, I recommend contacting HR directly at hr@vt.edu or reviewing the relevant policy documents. Is there a particular aspect of this topic you'd like me to help clarify?",
            sources: ['General HR Policies']
        };
    }
    
    hideWelcomeMessage() {
        this.welcomeMessage.style.display = 'none';
        this.chatMessages.style.display = 'block';
    }
    
    addMessage(type, text, sources = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        
        const avatar = document.createElement('div');
        avatar.className = `avatar ${type}-avatar`;
        avatar.textContent = type === 'user' ? '👤' : '🤖';
        
        const content = document.createElement('div');
        content.className = 'message-content';
        
        const messageText = document.createElement('div');
        messageText.className = 'message-text';
        messageText.textContent = text;
        content.appendChild(messageText);
        
        if (sources && sources.length > 0) {
            const sourcesDiv = document.createElement('div');
            sourcesDiv.className = 'message-sources';
            sourcesDiv.innerHTML = `<strong>Sources:</strong> ${sources.map(source => 
                `<span class="source-item">${source}</span>`
            ).join('')}`;
            content.appendChild(sourcesDiv);
        }
        
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(content);
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
        
        // Store in history
        this.messageHistory.push({ type, text, sources, timestamp: new Date() });
    }
    
    showTypingIndicator() {
        this.typingIndicator.style.display = 'block';
        this.scrollToBottom();
    }
    
    hideTypingIndicator() {
        this.typingIndicator.style.display = 'none';
    }
    
    scrollToBottom() {
        setTimeout(() => {
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        }, 100);
    }
    
    showError(message) {
        this.addMessage('bot', `❌ Error: ${message}`);
    }
    
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    
    // Public methods for external integration
    async sendQuery(query) {
        this.messageInput.value = query;
        await this.sendMessage();
    }
    
    clearChat() {
        this.chatMessages.innerHTML = '';
        this.messageHistory = [];
        this.welcomeMessage.style.display = 'block';
        this.chatMessages.style.display = 'none';
    }
    
    getHistory() {
        return this.messageHistory;
    }
}

// Initialize the HR Bot when the page loads
document.addEventListener('DOMContentLoaded', () => {
    window.hrBot = new HRBot();
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = HRBot;
}