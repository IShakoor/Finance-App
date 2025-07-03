// update message button to indicate unread messages
async function updateMessageButton() {
    try {
        const response = await fetch('/count-unread-messages/');
        const data = await response.json();
        const messageButton = document.querySelector('.message-button');
        if (data.unread_messages > 0) {
            messageButton.innerHTML = '<span class="unread-indicator">' + data.unread_messages + '</span> <i class="fa-regular fa-envelope"></i>';
        } else {
            messageButton.innerHTML = '<i class="fa-regular fa-envelope"></i>';
        }
    } catch (error) {
        console.error('Error updating message button:', error);
    }
}

document.addEventListener('DOMContentLoaded', updateMessageButton);
setInterval(updateMessageButton, 10000);