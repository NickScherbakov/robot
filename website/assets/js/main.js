/**
 * Earning Robot Website - Main JavaScript
 * Interactive demo and UI functionality
 */

// Demo state
let demoState = {
    tasksCount: 0,
    revenue: 0,
    expenses: 0,
    messages: []
};

// Sample responses for demo
const sampleResponses = [
    "Artificial Intelligence (AI) refers to the simulation of human intelligence in machines programmed to think and learn. It encompasses various technologies including machine learning, natural language processing, and computer vision.",
    "Python is a high-level, interpreted programming language known for its simplicity and readability. It's widely used in web development, data science, AI, and automation.",
    "The capital of France is Paris, a beautiful city known for its art, culture, and history.",
    "Machine learning is a subset of AI that enables computers to learn from data without being explicitly programmed. It uses algorithms to identify patterns and make predictions.",
    "Blockchain is a distributed ledger technology that records transactions across multiple computers in a way that makes the records difficult to alter retroactively."
];

// Pricing constants
const TASK_PRICE = 0.50;
const AI_COST = 0.02;

/**
 * Initialize the demo when page loads
 */
document.addEventListener('DOMContentLoaded', function() {
    initDemo();
    initScrollEffects();
});

/**
 * Initialize the demo panel
 */
function initDemo() {
    const chatMessages = document.getElementById('chat-messages');
    if (!chatMessages) return;

    // Add welcome message
    addBotMessage("👋 Hello! I'm the Earning Robot. Ask me anything to see how I work!");
    
    // Add enter key support for chat input
    const chatInput = document.getElementById('chat-input');
    if (chatInput) {
        chatInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    }
}

/**
 * Send a message in the demo chat
 */
function sendMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Add user message
    addUserMessage(message);
    input.value = '';
    
    // Simulate processing
    setTimeout(() => {
        addBotMessage("🤔 Processing your request...");
        
        // Simulate AI response
        setTimeout(() => {
            removeLastBotMessage();
            const response = getRandomResponse();
            addBotMessage(response);
            
            // Update stats
            updateStats();
            addFlowItem('income', `Task completed: +$${TASK_PRICE.toFixed(2)}`);
            addFlowItem('expense', `AI API cost: -$${AI_COST.toFixed(2)}`);
        }, 1500);
    }, 500);
}

/**
 * Add user message to chat
 */
function addUserMessage(text) {
    const chatMessages = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'chat-message user';
    messageDiv.textContent = text;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

/**
 * Add bot message to chat
 */
function addBotMessage(text) {
    const chatMessages = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'chat-message bot';
    messageDiv.textContent = text;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

/**
 * Remove the last bot message
 */
function removeLastBotMessage() {
    const chatMessages = document.getElementById('chat-messages');
    const botMessages = chatMessages.querySelectorAll('.chat-message.bot');
    if (botMessages.length > 0) {
        botMessages[botMessages.length - 1].remove();
    }
}

/**
 * Get a random response for demo
 */
function getRandomResponse() {
    return sampleResponses[Math.floor(Math.random() * sampleResponses.length)];
}

/**
 * Update financial statistics
 */
function updateStats() {
    demoState.tasksCount++;
    demoState.revenue += TASK_PRICE;
    demoState.expenses += AI_COST;
    
    const profit = demoState.revenue - demoState.expenses;
    
    // Update DOM
    updateElement('tasks-count', demoState.tasksCount);
    updateElement('revenue', `$${demoState.revenue.toFixed(2)}`);
    updateElement('expenses', `$${demoState.expenses.toFixed(2)}`);
    updateElement('profit', `$${profit.toFixed(2)}`);
}

/**
 * Update element text content
 */
function updateElement(id, value) {
    const element = document.getElementById(id);
    if (element) {
        // Add animation
        element.style.transform = 'scale(1.1)';
        element.textContent = value;
        
        setTimeout(() => {
            element.style.transform = 'scale(1)';
        }, 200);
    }
}

/**
 * Add flow item to transaction flow
 */
function addFlowItem(type, text) {
    const flowChart = document.getElementById('flow-chart');
    if (!flowChart) return;
    
    // Remove empty message if present
    const emptyMsg = flowChart.querySelector('.flow-empty');
    if (emptyMsg) {
        emptyMsg.remove();
    }
    
    // Create flow item
    const flowItem = document.createElement('div');
    flowItem.className = `flow-item ${type}`;
    
    const timestamp = new Date().toLocaleTimeString();
    flowItem.innerHTML = `
        <span>${text}</span>
        <span style="font-size: 0.9rem; color: #666;">${timestamp}</span>
    `;
    
    flowChart.appendChild(flowItem);
    
    // Keep only last 5 items
    const items = flowChart.querySelectorAll('.flow-item');
    if (items.length > 5) {
        items[0].remove();
    }
}

/**
 * Toggle mobile menu
 */
function toggleMenu() {
    const navMenu = document.querySelector('.nav-menu');
    if (navMenu) {
        navMenu.classList.toggle('active');
    }
}

/**
 * Initialize scroll effects
 */
function initScrollEffects() {
    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href !== '#') {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                    
                    // Close mobile menu if open
                    const navMenu = document.querySelector('.nav-menu');
                    if (navMenu) {
                        navMenu.classList.remove('active');
                    }
                }
            }
        });
    });
    
    // Add scroll reveal animation
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);
    
    // Observe sections for scroll animation
    document.querySelectorAll('.section').forEach(section => {
        section.style.opacity = '0';
        section.style.transform = 'translateY(30px)';
        section.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(section);
    });
}

/**
 * Format currency
 */
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

/**
 * Copy text to clipboard
 */
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Copied to clipboard!');
    }).catch(err => {
        console.error('Failed to copy:', err);
    });
}

/**
 * Show notification
 */
function showNotification(message) {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #4CAF50;
        color: white;
        padding: 1rem 2rem;
        border-radius: 6px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.2);
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'fadeOut 0.3s ease';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}

// Export for use in other scripts if needed
window.earningRobot = {
    sendMessage,
    toggleMenu,
    copyToClipboard,
    showNotification
};
