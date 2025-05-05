document.addEventListener('DOMContentLoaded', () => {
    loadBankAccounts();
    attachEditDetailsListener();

    const deleteAccountButton = document.getElementById('delete-account-button');
    if (deleteAccountButton) {
        deleteAccountButton.addEventListener('click', deleteAccount);
    } else {
        console.error("Error: 'delete-account-button' not found");
    }
});

// attatch edit button listeners
function attachEditDetailsListener() {
    const editDetailsButton = document.getElementById('edit-details-button');
    const editUserDetailsPopup = document.getElementById('edit-user-details-popup');

    if (editDetailsButton && editUserDetailsPopup) {
        editDetailsButton.addEventListener('click', (event) => {
            event.preventDefault();
            editUserDetailsPopup.classList.remove('hidden');
        });
    } else {
        console.error("Error: 'edit-details-button' or 'edit-user-details-popup' not found");
        setTimeout(attachEditDetailsListener, 100);
    }
}

// attach close button listeners
function attachCloseButtonListener() {
    const closeButton = document.querySelector('#edit-user-details-popup .close-btn');
    if (closeButton) {
        closeButton.addEventListener('click', closeEditUserDetailsPopup);
    } else {
        console.error("Error: Close button not found!");
    }
}
 // hide popup on close
function closeEditUserDetailsPopup() {
    const popup = document.getElementById('edit-user-details-popup');
    if (popup) {
        popup.classList.add('hidden');
        document.getElementById('edit-user-details-form').reset();
    } else {
        console.error("Error: 'edit-user-details-popup' not found in closeEditUserDetailsPopup()");
    }
}

// handle form submission
document.getElementById('edit-user-details-form').addEventListener('submit', async (event) => {
    event.preventDefault();

    // get form values
    const userId = document.getElementById('edit-userid').value;
    const username = document.getElementById('edit-username').value;
    const email = document.getElementById('edit-email').value;
    const currentPassword = document.getElementById('edit-current-password').value;
    const password = document.getElementById('edit-password').value;
    const passwordConfirm = document.getElementById('edit-password-confirm').value;

    // validation
    if (!username || !email) {
        alert('Username and email are required.');
        return;
    }

    if (password !== "" && password !== passwordConfirm) {
        alert('Passwords do not match.');
        return;
    }

    // edit user details
    try {
        const response = await fetch(`/edit-user/${userId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({ username, email, password, password_confirm: passwordConfirm, current_password: currentPassword })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to update user details');
        }

        const data = await response.json();
        if (data.success) {
            closeEditUserDetailsPopup();
            location.reload();
        } else {
            alert(data.error || 'Error updating user details');
        }
    } catch (error) {
        console.error('Error updating user details:', error);
        alert(error.message || 'An error occurred while updating user details');
    }
});

// load bank accounts
async function loadBankAccounts() {
    try {
        const response = await fetch('/get-account-balance/');
        const data = await response.json();

        const accountsList = document.getElementById('bank-accounts-list');

        if (!data.accounts || data.accounts.length === 0) {
            accountsList.innerHTML = '<p>No bank accounts linked.</p>';
            return;
        }

        // add bank accounts to html
        accountsList.innerHTML = data.accounts.map(account => `
            <div class="bank-account-item" data-account-id="${account.id}">
                <div class="account-info">
                    <h3>${account.account_name || account.bank_name}</h3>
                    <p class="account-type">${account.account_type}</p>
                    <p class="account-balance">Balance: ${account.currency} ${Number(account.balance).toFixed(2)}</p>
                </div>
                <div class="account-actions">
                    <button class="delete-bank-button" data-account-id="${account.id}">
                        <i class="fa-solid fa-trash"></i>
                    </button>
                </div>
            </div>
        `).join('');

        attachDeleteBankEventListeners();

    } catch (error) {
        accountsList.innerHTML = '<p class="error">Error loading bank accounts. Please try again later.</p>';
    }
}

// delete bank account listeners
function attachDeleteBankEventListeners() {
    const deleteButtons = document.querySelectorAll('.delete-bank-button');
    deleteButtons.forEach(button => {
        button.addEventListener('click', () => {
            const accountId = button.dataset.accountId;
            deleteBankAccount(accountId);
        });
    });
}

// delete bank account
async function deleteBankAccount(accountId) {
    if (!confirm('Are you sure you want to delete this bank account?')) {
        return;
    }

    try {
        const response = await fetch(`/delete-bank-account/${accountId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken(),
            },
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error(`Error deleting bank account: ${response.status} - ${errorText}`);
            alert(`Error deleting bank account: ${response.status}`);
            return;
        }

        const data = await response.json();
        if (data.success) {
            loadBankAccounts();
            alert('Bank account deleted successfully!');
        } else {
            alert(data.error);
        }
    } catch (error) {
        console.error('Error deleting bank account:', error);
        alert('An error occurred while deleting the bank account.');
    }
}


// delete user acccount
async function deleteAccount() {
    if (!confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
        return;
    }

    try {
        const response = await fetch('/delete-account/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken()
            }
        });

        if (response.ok) {
            alert('Account deleted successfully. You will be redirected to the signup page.');
            window.location.href = signupUrl;
        } else {
            const errorData = await response.json();
            alert(errorData.error || 'Error deleting account.');
        }
    } catch (error) {
        console.error('Error deleting account:', error);
        alert('An error occurred while deleting your account.');
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