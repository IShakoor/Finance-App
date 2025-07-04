// load all messages
async function loadMessages() {
    try {
        const response = await fetch('/get-messages/');
        const data = await response.json();

        const messageList = document.getElementById('message-list');
        messageList.innerHTML = '';
        
        // display message data & delete button
        data.messages.forEach(message => {
            const messageItem = document.createElement('li');
            messageItem.innerHTML = `
                <strong>${message.title}</strong>${message.content} <br>
                <small>${message.created_at}</small>
                <button class="delete-message-button" data-message-id="${message.id}"><i class="fa-solid fa-trash"></i></button>
            `;
            messageList.appendChild(messageItem);
        });

        // event listener for delete button
        const deleteButtons = document.querySelectorAll('.delete-message-button');
        deleteButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const messageId = e.target.dataset.messageId;
                deleteMessage(messageId);
            });
        });
    } catch (error) {
        console.error('Error loading messages:', error);
    }
}

// delete a message
async function deleteMessage(messageId) {
    try {
        const response = await fetch(`/delete-message/${messageId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken(),
            },
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error(`Error deleting message: ${response.status} - ${errorText}`);
            alert(`Error deleting message: ${response.status}`);
            return;
        }

        // reload messages on success
        const data = await response.json();
        if (data.success) {
            loadMessages();
            alert('Message deleted successfully!');
        } else {
            alert(data.error);
        }
    } catch (error) {
        console.error('Error deleting message:', error);
    }
}

// get CSRF token
function getCSRFToken() {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') {
            return value;
        }
    }
    return null;
}

// calling functions when page loads
document.addEventListener('DOMContentLoaded', loadMessages);