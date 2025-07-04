let currentPage = 1;
let totalPages = 1;

// fetch today's date
function getTodayDate() {
    const today = new Date();
    return today.toISOString().split('T')[0];
}

// fetch transactions
async function fetchTransactions(page = 1) {
    const queryParams = new URLSearchParams({
        page,
        search: document.getElementById('search-input').value || '',
        category: document.getElementById('category').value,
        start_date: document.getElementById('start_date').value || '',
        end_date: document.getElementById('end_date').value || getTodayDate(),
        min_price: parseFloat(document.getElementById('min_price').value) || '0',
        max_price: parseFloat(document.getElementById('max_price').value) || '',
        type: document.getElementById('transaction-type-filter').value,
        bank_account: document.getElementById('bank-account-filter').value || '',
    });

    try {
        const response = await fetch(`/get-all-transactions/?${queryParams.toString()}`);
        const data = await response.json();
        renderTransactions(data.transactions);
        currentPage = data.page;
        totalPages = data.total_pages;
        updatePaginationControls();
    } catch (error) {
        console.error('Error fetching transactions:', error);
    }
}

// load categories
async function loadCategories() {
    try {
        const response = await fetch('/get-categories/');
        const categories = await response.json();
        
        // populate category dropdowns
        const filterCategorySelect = document.getElementById('category');
        const addCategorySelect = document.getElementById('add-transaction-category');
        const editCategorySelect = document.getElementById('edit-transaction-category');

        filterCategorySelect.innerHTML = '<option value="">All Categories</option>';
        addCategorySelect.innerHTML = '<option value="" disabled selected>Select Category</option>';
        editCategorySelect.innerHTML = '<option value="" disabled selected>Select Category</option>';

        categories.forEach(category => {
            filterCategorySelect.insertAdjacentHTML('beforeend', `<option value="${category}">${category}</option>`);
            addCategorySelect.insertAdjacentHTML('beforeend', `<option value="${category}">${category}</option>`);
            editCategorySelect.insertAdjacentHTML('beforeend', `<option value="${category}">${category}</option>`);
        });
    } catch (error) {
        console.error('Error loading categories:', error);
    }
}

async function fetchBankAccounts() {
    try {
        const response = await fetch('/get-bank-accounts/');
        const accounts = await response.json();
        
        // populate filter dropdown
        const filterSelect = document.getElementById('bank-account-filter');
        filterSelect.innerHTML = '<option value="">All Accounts</option>';
        
        // populate add transaction dropdown
        const addTransactionSelect = document.getElementById('add-transaction-account');
        addTransactionSelect.innerHTML = '<option value="" disabled selected>Select Account</option>';
        
        // add account options to both dropdowns
        accounts.forEach(account => {
            const filterOption = document.createElement('option');
            filterOption.value = account.id;
            filterOption.textContent = account.account_name;
            filterSelect.appendChild(filterOption);
            const addOption = document.createElement('option');
            addOption.value = account.id;
            addOption.textContent = account.account_name;
            addTransactionSelect.appendChild(addOption);
        });
    } catch (error) {
        console.error('Error fetching bank accounts:', error);
        const errorMessage = 'Failed to load bank accounts. Please refresh the page.';
        document.querySelectorAll('.bank-account-error').forEach(element => {
            element.textContent = errorMessage;
        });
    }
}

// render transactions
function renderTransactions(transactions) {
    const transactionList = document.getElementById('transactions-list');
    transactionList.innerHTML = transactions.length
        ? transactions.map(txn => `
            <div class="transaction-item ${txn.is_received ? 'received' : 'sent'}" data-id="${txn.id}">
                <div class="transaction-details">
                    <h3>${txn.name}</h3>
                    <h3>${txn.account_name || ''}</h3>
                    <p class="txn-amount">£${Math.abs(txn.amount).toFixed(2)}</p>
                    <p>${txn.date} - ${txn.category}</p>
                </div>
                <button class="edit-transaction-btn" data-id="${txn.id}"
                    data-name="${txn.name}"
                    data-amount="${txn.amount}"
                    data-date="${txn.date}"
                    data-category="${txn.category}"
                    data-received="${txn.is_received}">
                </button>
            </div>
        `).join('')
        : '<p>No transactions found.</p>';

        document.querySelectorAll('.edit-transaction-btn').forEach(button => {
            button.addEventListener('click', (event) => {
                const button = event.target;
                openEditPopup(button.dataset.id, button.dataset.name, button.dataset.amount, button.dataset.date, button.dataset.is_received, button.dataset.category);
            });
        });
}

// update pagination
function updatePaginationControls() {
    document.getElementById('page-info').innerText = `Page ${currentPage} of ${totalPages}`;
    document.getElementById('prev-page').disabled = currentPage === 1;
    document.getElementById('next-page').disabled = currentPage === totalPages;
}

// add transaction to the list
function appendTransaction(transaction) {
    document.getElementById('transactions-list').insertAdjacentHTML('afterbegin', `
        <div class="transaction-item ${transaction.is_received ? 'received' : 'sent'}" data-id="${transaction.id}">
            <div class="transaction-info">
                <span class="txn-name">${transaction.name}</span>
                <span class="txn-amount">£${Math.abs(transaction.amount).toFixed(2)}</span>
                <span class="txn-date">${transaction.date}</span>
                <span class="txn-category">${transaction.category}</span>
                <span class="txn-id">ID: ${transaction.transaction_id}</span>
            </div>
            <button class="edit-transaction-btn" onclick="editTransaction(${transaction.id})">Edit</button>
        </div>
    `);
}

function editTransaction(transactionId) {
    const transactionElement = document.querySelector(`.transaction-item[data-id="${transactionId}"]`);
    if (!transactionElement) return;

    // collect transaction details
    const name = transactionElement.querySelector("h3").textContent;
    const amountText = transactionElement.querySelector(".transaction-amount").textContent.replace('£', '');
    const amount = parseFloat(amountText);
    const dateCategoryText = transactionElement.querySelector("p").textContent;
    const [date, category] = dateCategoryText.split(" - ");
    const isReceived = transactionElement.classList.contains("received");

    openEditPopup(transactionId, name, amount, date, isReceived, category);
}

function openEditPopup(id, name, amount, date, is_received, category) {
    document.getElementById('editTransactionId').value = id;
    document.getElementById('edit-txn-name').value = name;
    document.getElementById('edit-txn-price').value = amount;
    document.getElementById('edit-txn-date').value = date;
    document.getElementById('edit-transaction-category').value = category;
    document.getElementById('edit-transaction-type').checked = is_received;

    document.getElementById('edit-transaction-popup').style.display = 'block';
}

// close edit popup
document.getElementById('close-edit-transaction-popup').addEventListener('click', () => {
    document.getElementById('edit-transaction-popup').style.display = 'none';
});

// submit edited transaction
document.getElementById('saveTransactionBtn').addEventListener('click', async event => {
    event.preventDefault();
    const id = document.getElementById('editTransactionId').value;

    if (!id) {
        alert("Error: Transaction ID is missing.");
        return;
    }

    const name = document.getElementById('edit-txn-name').value;
    const amount = parseFloat(document.getElementById('edit-txn-price').value);
    const date = document.getElementById('edit-txn-date').value;
    const category = document.getElementById('edit-transaction-category').value;
    const is_received = document.getElementById('edit-transaction-type').checked;

    try {
        const response = await fetch(`/edit-transaction/${id}/`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({ 
                name, 
                amount, 
                date, 
                category, 
                is_received
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to update transaction');
        }

        const result = await response.json();
        if (result.success) {
            document.getElementById('edit-transaction-popup').style.display = 'none';
            fetchTransactions();

            // get all budget ids
            const budgetIds = await getBudgetIdsByCategory(category);
                
            // update all matching budgets
            if (budgetIds.length > 0) {
                const updatePromises = budgetIds.map(budgetId => updateBudget(budgetId));
                await Promise.all(updatePromises);
            }

        } else {
            alert(result.error || 'Error updating transaction');
        }
    } catch (error) {
        console.error('Error updating transaction:', error);
        alert(error.message || 'An error occurred while updating the transaction');
    }
});

// delete transaction
async function deleteTransaction() {
    const id = document.getElementById('editTransactionId').value;
    const category = document.getElementById('edit-transaction-category').value;

    if (!id || !confirm("Are you sure you want to delete this budget?")) return;
    
    try {
        const response = await fetch(`/delete-transaction/${id}/`, {
            method: 'POST',
            headers: { 'X-CSRFToken': getCSRFToken() }
        });

        if (!response.ok) {
            alert("Error deleting budget.");
            return;
        }
        else {
            document.getElementById('edit-transaction-popup').style.display = 'none';
            fetchTransactions();

            // get all budget ids
            const budgetIds = await getBudgetIdsByCategory(category);

            // update all matching budgets
            if (budgetIds.length > 0) {
                const updatePromises = budgetIds.map(budgetId => updateBudget(budgetId));
                await Promise.all(updatePromises);
            }
        }
    } catch (error) {
        console.error('Error deleting transaction:', error);
    }
}

document.getElementById('deleteTransactionBtn').addEventListener('click', deleteTransaction);

function getCSRFToken() {
    const cookie = document.cookie.split('; ').find(row => row.startsWith('csrftoken='));
    return cookie ? cookie.split('=')[1] : null;
}

// clear popup form
function clearPopupForm() {
    document.getElementById('add-txn-name').value = '';
    document.getElementById('add-txn-price').value = '';
    document.getElementById('add-txn-date').value = '';
    const transactionTypeToggle = document.getElementById('add-transaction-type');
    transactionTypeToggle.checked = false;
    document.getElementById('add-transaction-type-label').textContent = 'Sent';
    document.getElementById('add-transaction-account').value = '';
}

// document & event listeners
document.addEventListener('DOMContentLoaded', () => {
    loadCategories();
    fetchBankAccounts();
    fetchTransactions();

    // update pages
    document.getElementById('prev-page').addEventListener('click', () => fetchTransactions(currentPage - 1));
    document.getElementById('next-page').addEventListener('click', () => fetchTransactions(currentPage + 1));
    document.getElementById('filter-form').addEventListener('submit', e => {
        e.preventDefault();
        fetchTransactions(1);
    });
    document.getElementById('search-input').addEventListener('input', () => fetchTransactions(1));
    const clearFiltersBtn = document.getElementById('clear-filters-btn');
    if (clearFiltersBtn) {
        clearFiltersBtn.addEventListener('click', () => {
            const filterForm = document.getElementById('filter-form');
            filterForm.reset();
            document.getElementById('end_date').value = getTodayDate();
            fetchTransactions(1);
        });
    }

    // Get both popups
    const addPopup = document.getElementById('add-transaction-popup');
    const editPopup = document.getElementById('edit-transaction-popup');
    const transactionTypeToggle = document.getElementById('add-transaction-type');
    const transactionTypeLabel = document.getElementById('add-transaction-type-label');

    // Add transaction popup handlers
    document.getElementById('add-transaction-btn').addEventListener('click', () => {
        addPopup.style.display = 'block';
    });

    document.getElementById('close-add-transaction-popup').addEventListener('click', () => {
        addPopup.style.display = 'none';
        clearPopupForm();
    });

    // Edit transaction popup handlers
    document.getElementById('close-edit-transaction-popup').addEventListener('click', () => {
        editPopup.style.display = 'none';
    });

    // Close popups when clicking outside
    window.addEventListener('click', e => {
        if (e.target === addPopup) {
            addPopup.style.display = 'none';
            clearPopupForm();
        }
        if (e.target === editPopup) {
            editPopup.style.display = 'none';
        }
    });   
    transactionTypeToggle.addEventListener('change', () => {
        transactionTypeLabel.textContent = transactionTypeToggle.checked ? 'Received' : 'Sent';
    });

    // add transactions
    document.getElementById('add-transaction-form').addEventListener('submit', async e => {
        e.preventDefault();
        const name = document.getElementById('add-txn-name').value;
        const price = parseFloat(document.getElementById('add-txn-price').value);
        const date = document.getElementById('add-txn-date').value;
        const category = document.getElementById('add-transaction-category').value;
        const is_received = transactionTypeToggle.checked;
        const bank_account = document.getElementById('add-transaction-account').value;

        if (!name || isNaN(price) || !date) {
            alert('Please fill in all fields correctly.');
            return;
        }

        try {
            const response = await fetch('/add-transaction/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCSRFToken() },
                body: JSON.stringify({ name, amount: price, date, category, is_received, bank_account, transaction_id: generateTransactionId()}),
            });

            if (response.ok) {
                const result = await response.json();
                if (result.success) {
                    const popup = document.getElementById('add-transaction-popup');
                    popup.style.display = 'none';
                    clearPopupForm();
                    fetchTransactions();

                // get all budget ids
                const budgetIds = await getBudgetIdsByCategory(category);
                
                // update all matching budgets
                if (budgetIds.length > 0) {
                    const updatePromises = budgetIds.map(budgetId => updateBudget(budgetId));
                    await Promise.all(updatePromises);
                }
                } else {
                    alert(result.error || 'Error adding transaction');
                }
            } else {
                const errorData = await response.json();
                alert(`Error: ${errorData.error}`);
            }
        } catch (error) {
            console.error('Error adding transaction:', error);
            alert('An error occurred while adding the transaction.');
        }
    });

});

// generate a random transaction ID (for custom transactions only)
function generateTransactionId() {
    const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let transactionId = '';
    for (let i = 0; i < 37; i++) {
        const randomIndex = Math.floor(Math.random() * characters.length);
        transactionId += characters[randomIndex];
    }
    return transactionId;
}

// get budgets
async function getBudgets() {
    try {
        const response = await fetch('/get-all-budgets/');
        const data = await response.json();

        if (data.error) {
            console.error("Error fetching budgets:", data.error);
            return null;
        }

        return data.budgets;
    } catch (error) {
        console.error('Error fetching budgets:', error);
        return null;
    }
}

// update budgets based on transactions
async function updateBudget(budgetId) {
    try {
        console.log(`Attempting to update budget with ID: ${budgetId}`);
        
        const response = await fetch(`/update-budget-progress/${budgetId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            }
        });

        console.log('Update Budget Response Status:', response.status);

        if (!response.ok) {
            const errorData = await response.json();
            console.error('Error updating budget:', errorData);
            throw new Error(errorData.error || 'Failed to update budget');
        }

        const result = await response.json();

        if (result.success) {
            return result.current_amount;
        } else {
            console.error('Failed to update budget progress');
            return null;
        }
    } catch (error) {
        console.error('Error in updateBudget:', error);
        return null;
    }
}

// get budget from its category
async function getBudgetIdsByCategory(category) {
    try {
        const budgets = await getBudgets();
        
        if (!budgets) {
            console.error('No budgets found');
            return [];
        }

        // find all matching budgets
        const matchingBudgets = budgets.filter(budget => budget.category === category);
        
        if (matchingBudgets.length > 0) {
            return matchingBudgets.map(budget => budget.id);
        }
        
        console.error(`No budget found for category: ${category}`);
        return [];
    } catch (error) {
        console.error('Error finding budgets by category:', error);
        return [];
    }
}