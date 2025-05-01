// Main JavaScript file for Ppang - Carbon Footprint Tracker

function refreshCharts() {
    fetch(window.location.href)
        .then(response => response.text())
        .then(html => {
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');

            // Update each chart if it exists
            if (doc.getElementById('emissions-category-chart')) {
                const newChartData = JSON.parse(doc.getElementById('emissions-category-chart').getAttribute('data-chart'));
                Plotly.newPlot('emissions-category-chart', newChartData.data, newChartData.layout, {responsive: true});
            }

            if (doc.getElementById('waste-composition-chart')) {
                const newWasteData = JSON.parse(doc.getElementById('waste-composition-chart').getAttribute('data-chart'));
                Plotly.newPlot('waste-composition-chart', newWasteData.data, newWasteData.layout, {responsive: true});
            }
        });
}

// Refresh charts every 30 seconds
setInterval(refreshCharts, 30000);

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-dismiss alerts after 5 seconds
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Initialize Plotly charts if they exist
    initCharts();
});

// Initialize Plotly charts
function initCharts() {
    const chartElements = document.querySelectorAll('.chart-container[data-chart]');

    chartElements.forEach(function(element) {
        try {
            const chartData = JSON.parse(element.getAttribute('data-chart'));
            Plotly.newPlot(element.id, chartData.data, chartData.layout, {responsive: true});
        } catch (e) {
            console.error('Error initializing chart:', e);
        }
    });
}

// Function to toggle between different form tabs
function switchFormTab(tabId) {
    // Hide all tabs
    document.querySelectorAll('.form-tab').forEach(tab => {
        tab.classList.remove('show', 'active');
    });

    // Show selected tab
    document.getElementById(tabId).classList.add('show', 'active');

    // Update active nav link
    document.querySelectorAll('.form-tab-link').forEach(link => {
        link.classList.remove('active');
    });

    document.querySelector(`.form-tab-link[href="#${tabId}"]`).classList.add('active');
}

// Function to confirm delete actions
function confirmDelete(message) {
    return confirm(message || 'Are you sure you want to delete this item?');
}

// Chat with Ppang AI functionality
document.addEventListener('DOMContentLoaded', function() {
    const chatInput = document.getElementById('chatInput');
    const sendChatBtn = document.getElementById('sendChatBtn');
    const chatMessages = document.getElementById('chatMessages');

    if (chatInput && sendChatBtn && chatMessages) {
        // Send message when button is clicked
        sendChatBtn.addEventListener('click', function() {
            sendUserMessage();
        });

        // Send message when Enter key is pressed
        chatInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendUserMessage();
            }
        });

        function sendUserMessage() {
            const message = chatInput.value.trim();
            if (message === '') return;

            // Add user message to chat
            addMessageToChat('user', message);

            // Clear input
            chatInput.value = '';

            // Show loading indicator
            showTypingIndicator();

            // Send message to server
            fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message
                }),
            })
            .then(response => response.json())
            .then(data => {
                // Remove typing indicator
                removeTypingIndicator();

                // Handle the response
                if (data.status === 'success') {
                    // Add AI response to chat
                    addMessageToChat('ai', data.response);
                } else {
                    // Add error message
                    addMessageToChat('ai', 'Sorry, I encountered an error processing your request. Please try again.');
                }

                // Scroll to bottom of chat
                chatMessages.scrollTop = chatMessages.scrollHeight;
            })
            .catch(error => {
                // Remove typing indicator
                removeTypingIndicator();

                // Add error message
                addMessageToChat('ai', 'Sorry, there was a technical issue. Please try again later.');
                console.error('Error:', error);

                // Scroll to bottom of chat
                chatMessages.scrollTop = chatMessages.scrollHeight;
            });
        }

        function addMessageToChat(type, message) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `chat-message ${type}-message`;

            const avatarDiv = document.createElement('div');
            avatarDiv.className = 'chat-avatar';

            const icon = document.createElement('i');
            if (type === 'user') {
                icon.className = 'fas fa-user';
            } else {
                icon.className = 'fas fa-leaf';
            }

            avatarDiv.appendChild(icon);

            const bubbleDiv = document.createElement('div');
            bubbleDiv.className = 'chat-bubble';

            // Handle message content
            // Check if message contains bullet points
            if (message.includes('•') || message.includes('-') || message.includes('*')) {
                const parts = message.split(/[•\-\*]/);
                const paragraph = document.createElement('p');
                paragraph.textContent = parts[0].trim();
                bubbleDiv.appendChild(paragraph);

                const list = document.createElement('ul');
                for (let i = 1; i < parts.length; i++) {
                    if (parts[i].trim().length > 0) {
                        const item = document.createElement('li');
                        item.textContent = parts[i].trim();
                        list.appendChild(item);
                    }
                }

                if (list.children.length > 0) {
                    bubbleDiv.appendChild(list);
                }
            } else {
                // Simple text message
                const paragraph = document.createElement('p');
                paragraph.textContent = message;
                bubbleDiv.appendChild(paragraph);
            }

            messageDiv.appendChild(avatarDiv);
            messageDiv.appendChild(bubbleDiv);

            chatMessages.appendChild(messageDiv);
        }

        function showTypingIndicator() {
            const typingDiv = document.createElement('div');
            typingDiv.className = 'chat-message ai-message typing-indicator';
            typingDiv.id = 'typingIndicator';

            const avatarDiv = document.createElement('div');
            avatarDiv.className = 'chat-avatar';

            const icon = document.createElement('i');
            icon.className = 'fas fa-leaf';
            avatarDiv.appendChild(icon);

            const bubbleDiv = document.createElement('div');
            bubbleDiv.className = 'chat-bubble';

            const typingAnimation = document.createElement('div');
            typingAnimation.className = 'typing-animation';

            for (let i = 0; i < 3; i++) {
                const dot = document.createElement('span');
                dot.className = 'dot';
                typingAnimation.appendChild(dot);
            }

            bubbleDiv.appendChild(typingAnimation);
            typingDiv.appendChild(avatarDiv);
            typingDiv.appendChild(bubbleDiv);

            chatMessages.appendChild(typingDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        function removeTypingIndicator() {
            const typingIndicator = document.getElementById('typingIndicator');
            if (typingIndicator) {
                typingIndicator.remove();
            }
        }
    }
});