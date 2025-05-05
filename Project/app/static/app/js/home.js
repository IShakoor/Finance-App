// ===========================
// Plaid Link Initialization
// ===========================
async function initializePlaid() {
    try {
        const response = await fetch('/create-link-token/');
        const { link_token } = await response.json();

        Plaid.create({
            token: link_token,
            onSuccess: handlePlaidSuccess,
            onExit: handlePlaidExit,
        }).open();
    } catch (err) {
        handleError('Plaid Initialization Error', err);
    }
}
// loads all data after successful bank connection
async function handlePlaidSuccess(public_token) {
    try {
        const response = await fetch('/exchange-public-token/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ public_token }),
        });

        if (!response.ok) throw new Error('Failed to save access token.');

        await syncBankAccounts();
        alert("Accounts Successfully Linked!")
        await loadAllData();
        window.location.reload();
    } catch (err) {
        handleError('Plaid Success Handling Error', err);
    }
}

// store new account data
async function syncBankAccounts() {
    try {
        const response = await fetch('/sync-bank-accounts/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCSRFToken() },
        });
        if (!response.ok) throw new Error('Failed to sync bank accounts.');
    } catch (err) {
        handleError('Error syncing bank accounts', err);
    }
}

function handlePlaidExit(err, metadata) {
    console.error('Plaid exit:', err, metadata);
}

// ===========================
// Fetch Account Balances
// ===========================
async function fetchBalance() {
    try {
        const { accounts } = await fetchData('/get-account-balance/');
        renderBalances(accounts || []);
    } catch (err) {
        handleError('Error fetching account balances', err);
    }
}

function renderBalances(accounts) {
    document.getElementById('balance-items').innerHTML = accounts.length
        ? accounts.map(account => `
            <div class="balance-item">
                <h3>${account.account_name || account.bank_name}</h3>
                <p>£${Number(account.balance).toFixed(2)}</p>
            </div>
        `).join('')
        : '<p>No accounts found.</p>';
}

// ===========================
// fetch transactions
// ===========================
// Get all transactions for graph
async function getAllTransactionsInsights() {
    try {
        const response = await fetch('/get-all-transactions-insights/');
        const data = await response.json();
        return data.transactions;
    } catch (error) {
        console.error('Error fetching transactions:', error);
    }
}

async function fetchTransactions() {
    try {
        const { transactions } = await fetchData('/get-all-transactions/');
        renderTransactions(transactions
            .sort((a, b) => new Date(b.date) - new Date(a.date))
            .slice(0, 10)
            .map(txn => ({ ...txn, is_received: txn.is_received ?? txn.amount > 0 }))
        );
    } catch (error) {
        console.error('Error fetching transactions:', error);
    }
}

// render transactions
function renderTransactions(transactions) {
    document.getElementById('transactions-items').innerHTML = transactions.length
        ? transactions.map(txn => `
            <div class="transaction-item ${txn.is_received ? 'received' : 'sent'}">
                <div class="transaction-details">
                    <h3>${txn.name}</h3>
                    <p>${txn.date} - ${txn.category}</p>
                </div>
                <div class="transaction-amount">£${Math.abs(txn.amount).toFixed(2)}</div>
            </div>
        `).join('')
        : '<p>No transactions found.</p>';
}

// ===========================
// Fetch Savings Goal
// ===========================
async function fetchSavingsGoal() {
    try {
        const response = await fetch('/get-all-goals/');
        const data = await response.json();
        renderSavingsGoal(data.goals);
    } catch (err) {
        handleError('Error fetching savings goal', err);
    }
}

// render savings goal
function renderSavingsGoal(savings_goals) {
    const savingsGoalContainer = document.getElementById('savings-goal-item');
    if (savings_goals.length > 0) {
        // select most recent goal
        const latestGoal = savings_goals.reduce((a, b) => new Date(a.goal_date) < new Date(b.goal_date) ? a : b);
        const progress = (latestGoal.current_amount / latestGoal.target_amount) * 100;
        savingsGoalContainer.innerHTML = `
            <div class="savings-goal-item">
                <h3>${latestGoal.name}</h3>
                <div class="goal-progress">
                    <svg viewBox="0 0 100 100" class="progress-circle">
                        <circle class="progress-background" cx="50" cy="50" r="45"></circle>
                        <circle class="progress-bar" cx="50" cy="50" r="45"
                            stroke-dasharray="282.6"
                            stroke-dashoffset="${282.6 - (282.6 * progress) / 100}">
                        </circle>
                        <text x="50" y="55" text-anchor="middle" class="progress-text">${Math.round(progress)}%</text>
                    </svg>
                </div>
                <p>£${latestGoal.current_amount.toFixed(2)} / £${latestGoal.target_amount.toFixed(2)}</p>
                <p>${latestGoal.goal_date}</p>
            </div>
        `;

        // attach savings goal data to button
        const editButton = document.getElementById('edit-goal-btn');
        editButton.dataset.id = latestGoal.id;
        editButton.dataset.name = latestGoal.name;
        editButton.dataset.target = latestGoal.target_amount;
        editButton.dataset.current = latestGoal.current_amount;
        editButton.dataset.date = latestGoal.goal_date;
    } else {
        savingsGoalContainer.innerHTML = '<p>No savings goals found.</p>';
    }
}

// ===========================
// fetch budget
// ===========================
async function fetchBudget() {
    try {
        const response = await fetch("/get-all-budgets/");
        if (response.ok) {
            const data = await response.json();
            renderBudget(data.budgets);
        } else {
            const errorData = await response.json();
            console.error("Error fetching budget:", errorData.error);
        }
    } catch (error) {
        console.error("Error fetching budget:", error);
    }
}

// render budget
function renderBudget(budgets) {
    const budgetContainer = document.getElementById('budget-item');
    if (budgets.length > 0) {
        // select budget with highest current amount
        const highestBudget = budgets.reduce((a, b) => a.current_amount > b.current_amount ? a : b);
        const progress = (highestBudget.current_amount / highestBudget.target_amount) * 100;
        budgetContainer.innerHTML = `
            <div class="budget-item">
                <h3>${highestBudget.name}</h3>
                <div class="budget-progress">
                    <svg viewBox="0 0 100 100" class="progress-circle">
                        <circle class="progress-background" cx="50" cy="50" r="45"></circle>
                        <circle class="progress-bar" cx="50" cy="50" r="45"
                            stroke-dasharray="282.6"
                            stroke-dashoffset="${282.6 - (282.6 * progress) / 100}">
                        </circle>
                        <text x="50" y="55" text-anchor="middle" class="progress-text">${Math.round(progress)}%</text>
                    </svg>
                </div>
                <p>£${highestBudget.current_amount.toFixed(2)} / £${highestBudget.target_amount.toFixed(2)}</p>
                <p>${highestBudget.category} - ${highestBudget.time_period}</p>
            </div>
        `;

        // attach budget data to button
        const editButton = document.getElementById('edit-budget-btn');
        editButton.dataset.id = highestBudget.id;
        editButton.dataset.name = highestBudget.name;
        editButton.dataset.target = highestBudget.target_amount;
        editButton.dataset.date = highestBudget.created_date;
    } else {
        budgetContainer.innerHTML = '<p>No budgets found.</p>';
    }
}

// ===========================
// add transactions to UI
// ===========================
function addTransactionToUI(transaction, prepend = false) {
    const transactionTypeClass = transaction.is_received ?? transaction.amount > 0 ? 'received' : 'sent';
    const transactionItem = `
        <div class="transaction-item ${transactionTypeClass}">
            <h3>${transaction.name}</h3>
            <p>${transaction.date} - ${transaction.category}</p>
            <p>£${Math.abs(transaction.amount).toFixed(2)}</p>
            
        </div>
    `;

    const transactionsContainer = document.getElementById('transactions-items');
    transactionsContainer.insertAdjacentHTML(prepend ? 'afterbegin' : 'beforeend', transactionItem);
    while (transactionsContainer.children.length > 10) {
        transactionsContainer.removeChild(transactionsContainer.lastChild);
    }
}

// ===========================
// Utility Functions
// ===========================
async function fetchData(url) {
    const response = await fetch(url, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCSRFToken() },
    });

    if (!response.ok) throw new Error((await response.json()).error || 'Unknown error occurred');
    return await response.json();
}

function getCSRFToken() {
    return document.cookie.split('; ').reduce((acc, cookie) => {
        const [key, value] = cookie.split('=');
        return key === 'csrftoken' ? value : acc;
    }, null);
}

function handleError(message, err) {
    console.error(`${message}:`, err.message);
    alert(`${message}: ${err.message}`);
}

// ===========================
// Popup & Form Handling
// ===========================
const transactionPopup = document.getElementById('transaction-form-popup');
const editPopup = document.getElementById('edit-goal-popup');
const budgetpopup = document.getElementById('edit-budget-popup');

document.getElementById('add-transaction-btn').addEventListener('click', () => transactionPopup.style.display = 'block');
document.getElementById('close-popup-btn').addEventListener('click', () => transactionPopup.style.display = 'none');
document.getElementById('edit-goal-btn').addEventListener('click', (event) => {
    const button = event.target;
    openEditPopup(button.dataset.id, button.dataset.name, button.dataset.target, button.dataset.current, button.dataset.date);
});
document.getElementById("save-edit-changes-btn").addEventListener("click", saveGoalChanges);
document.getElementById('edit-budget-btn').addEventListener('click', (event) => {
    const button = event.target;
    openBudgetPopup(button.dataset.id, button.dataset.name, button.dataset.target);
});
document.getElementById("save-budget-changes-btn").addEventListener("click", saveBudgetChanges);

// clicking outside popup closes it
window.addEventListener('click', (e) => {
    if (e.target === transactionPopup) transactionPopup.style.display = 'none';
    if (e.target === editPopup) editPopup.style.display = 'none';
    if (e.target === budgetpopup) budgetpopup.style.display = 'none';

});

// open the edit popup form
function openEditPopup() {
    const editButton = document.getElementById('edit-goal-btn');
    const id = editButton.dataset.id;
    const name = editButton.dataset.name;
    const target = editButton.dataset.target;
    const current = editButton.dataset.current;
    const date = editButton.dataset.date;

    document.getElementById("edit-goal-id").value = id;
    document.getElementById("edit-goal-name").value = name;
    document.getElementById("edit-goal-target").value = target;
    document.getElementById("edit-goal-current").value = current;
    document.getElementById("edit-goal-date").value = date;

    const editPopup = document.getElementById("edit-goal-popup");
    editPopup.style.display = "flex";
}

// close edit popup
function closeEditPopup() {
    document.getElementById("edit-goal-popup").style.display = "none";
}

// open the edit budgets popup form
async function openBudgetPopup() {
    const editButton = document.getElementById('edit-budget-btn');
    const id = editButton.dataset.id;
    const name = editButton.dataset.name;
    const target = editButton.dataset.target;
    const date = editButton.dataset.date;

    document.getElementById("edit-budget-id").value = id;
    document.getElementById("edit-budget-name").value = name;
    document.getElementById("edit-budget-target").value = target;

    const editPopup = document.getElementById("edit-budget-popup");
    editPopup.style.display = "flex";
}

// close buget popup
function closeBudgetPopup() {
    document.getElementById("edit-budget-popup").style.display = "none";
}

// ===========================
// Initialization on Load
// ===========================
async function loadAllData() {
    await fetchBalance();
    await fetchTransactions();
    await fetchSavingsGoal();
    await fetchBudget();
    await fetchCategories();
    fetchBankAccounts();
    if (document.getElementById('balance-container')) showBalance();
}

// check token
document.addEventListener('DOMContentLoaded', async () => {
    try {
        if (isAuthenticated && hasAccessToken) await loadAllData();
    } catch (err) {
        handleError('Error auto-loading data', err);
    }
});

document.getElementById('connect-bank-btn').addEventListener('click', initializePlaid);

// display balance
function showBalance() {
    const balanceContainer = document.getElementById('balance-container');
    const welcomeSection = document.getElementById('welcome-section');
    if (balanceContainer && welcomeSection) {
        balanceContainer.style.display = 'block';
        welcomeSection.style.display = 'none';
    } else {
        console.warn('Balance or welcome section not found in DOM. Skipping style update.');
    }
}

// save edited goals
async function saveGoalChanges() {
    const id = document.getElementById("edit-goal-id").value;
    if (!id) {
        alert("Error: Goal ID is missing.");
        return;
    }

    const name = document.getElementById("edit-goal-name").value;
    const target = parseFloat(document.getElementById("edit-goal-target").value);
    const current = parseFloat(document.getElementById("edit-goal-current").value);
    const date = document.getElementById("edit-goal-date").value;

    try {
        const response = await fetch(`/edit-goal/${id}/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken()
            },
            body: JSON.stringify({ name, target_amount: target, current_amount: current, goal_date: date })
        });

        if (!response.ok) {
            console.error("Failed to update goal:", await response.text());
            alert("Error updating goal.");
            return;
        }

        // close & refresh
        closeEditPopup();
        fetchSavingsGoal();
    } catch (error) {
        console.error("Error saving goal changes:", error);
    }
}

// fetch and add categories
let cachedCategories = [];

async function fetchCategories() {
    try {
        const response = await fetch("/get-categories/");
        const categories = await response.json();

        if (response.ok) {
          cachedCategories = categories;
          populateCategoryDropdown(categories, "edit-budget-category");
          populateCategoryDropdown(categories, "transaction-category");

        } else {
          console.error("Error fetching categories:", categories.error);
        }
    } catch (error) {
        console.error("Error fetching categories:", error);
    }
}

function populateCategoryDropdown(categories, elementId) {
    const categorySelect = document.getElementById(elementId);

    if (!categorySelect) {
        console.error(`Category dropdown (${elementId}) not found in the DOM.`);
        return;
    }

    categorySelect.innerHTML =
    '<option value="" disabled>Select Category</option>';
    categories.forEach((category) => {
    const option = document.createElement("option");
    option.value = category;
    option.textContent = category;
    categorySelect.appendChild(option);
    });
}

async function fetchBankAccounts() {
    try {
        const response = await fetch('/get-bank-accounts/');
        const accounts = await response.json();
                
        // populate add transaction dropdown
        const addTransactionSelect = document.getElementById('transaction-account');
        addTransactionSelect.innerHTML = '<option value="" disabled selected>Select Account</option>';
        
        // add account options to both dropdowns
        accounts.forEach(account => {
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

// save edited goals
async function saveBudgetChanges() {
    const id = document.getElementById("edit-budget-id").value;
    if (!id) {
        alert("Error: Budget ID is missing.");
        return;
    }

    // fetch editing data
    const name = document.getElementById("edit-budget-name").value;
    const target = parseFloat(document.getElementById("edit-budget-target").value);
    const category = document.getElementById("edit-budget-category").value;
    const timePeriod = document.getElementById("edit-budget-time-period").value;

    // endpoint call
    try {
        const response = await fetch(`/edit-budget/${id}/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken()
            },
            body: JSON.stringify({ name, target_amount: target, category, time_period: timePeriod })
        });

        if (response.ok) {
            const data = await response.json();
            console.log("Budget updated successfully:", data);
        } else {
            const errorData = await response.json();
            console.error("Error updating budget:", errorData.error);
        }

        // close & refresh
        closeBudgetPopup();
        fetchBudget();
    } catch (error) {
        console.error("Error saving budget changes:", error);
    }
}

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


// create & display custom transaction
document.getElementById('add-transaction-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const newTransaction = {
        name: document.getElementById('transaction-name').value,
        bank_account: document.getElementById('transaction-account').value,
        amount: parseFloat(document.getElementById('transaction-amount').value),
        date: document.getElementById('transaction-date').value,
        category: document.getElementById('transaction-category').value,
        is_received: document.getElementById('transaction-type').checked,
        transaction_id: generateTransactionId()
    };

    try {
        const response = await fetch('/add-transaction/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCSRFToken() },
            body: JSON.stringify(newTransaction),
        });

        if (!response.ok) throw new Error('Failed to save transaction.');

        addTransactionToUI(newTransaction, true);
        const transactionPopup = document.getElementById('transaction-form-popup');
        
        if (transactionPopup) {
            transactionPopup.style.display = 'none';
        }
        
        e.target.reset();
    } catch (err) {
        handleError('Error saving transaction', err);
    }
});

document.getElementById('transaction-type').addEventListener('change', (e) => {
    document.getElementById('transaction-type-label').textContent = e.target.checked ? 'Received' : 'Sent';
});

// create bar chart
async function createBarChart() {
    const transactions = await getAllTransactionsInsights();
    const dailySpending = {};

    // find the date last week
    const sevenDaysAgo = new Date();
    sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);

    // filter and sum amounts
    transactions.forEach((transaction) => {
        const date = new Date(transaction.date);
        
        // only consider this weeks transactions
        if (date >= sevenDaysAgo) {
            const formattedDate = date.toLocaleDateString('default', { 
                month: 'short', 
                day: 'numeric' 
            });

            if (!dailySpending[formattedDate]) {
                dailySpending[formattedDate] = 0;
            }
            
            // only add spend transactions
            if (!transaction.is_received) {
                dailySpending[formattedDate] += Math.abs(transaction.amount);
            }
        }
    });

    // show daa for all 7 days
    const last7Days = [];
    for (let i = 6; i >= 0; i--) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        const formattedDate = date.toLocaleDateString('default', { 
            month: 'short', 
            day: 'numeric' 
        });
        
        last7Days.push({
            date: formattedDate,
            spending: dailySpending[formattedDate] || 0
        });
    }

    const labels = last7Days.map(day => day.date);
    const data = last7Days.map(day => day.spending);

    // format bars
    const generateColors = (count) => {
        const baseColors = [
            'rgba(255, 99, 132, 0.2)',
            'rgba(54, 162, 235, 0.2)',
            'rgba(255, 206, 86, 0.2)',
            'rgba(75, 192, 192, 0.2)',
            'rgba(153, 102, 255, 0.2)',
            'rgba(255, 159, 64, 0.2)',
            'rgba(236, 64, 255, 0.2)'
        ];
        const baseBorderColors = [
            'rgba(255, 99, 132, 1)',
            'rgba(54, 162, 235, 1)',
            'rgba(255, 206, 86, 1)',
            'rgba(75, 192, 192, 1)',
            'rgba(153, 102, 255, 1)',
            'rgba(255, 159, 64, 1)',
            'rgb(255, 64, 242)'

        ];

        // repeat colours
        return {
            backgroundColor: Array(count).fill(0).map((_, i) => baseColors[i % baseColors.length]),
            borderColor: Array(count).fill(0).map((_, i) => baseBorderColors[i % baseBorderColors.length])
        };
    };

    const colors = generateColors(labels.length);

    const chartData = {
        labels: labels,
        datasets: [{
            data: data,
            backgroundColor: colors.backgroundColor,
            borderColor: colors.borderColor,
            borderWidth: 1
        }]
    };

    // destroy existing chart if it exists
    if (window.monthlySpendingChart) {
        window.monthlySpendingChart.destroy();
    }

    // create chart
    const ctx = document.getElementById('chart').getContext('2d');
    const chart = new Chart(ctx, {
        type: 'bar',
        data: chartData,
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        display: true,
                        drawBorder: false,
                        color: 'rgba(0, 0, 0, 0.1)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        autoSkip: false
                    },
                    offset: true
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: false
                }
            }
        }
    });
}

// periodically update chart
function updateChartPeriodically() {
    createBarChart();
}

document.addEventListener('DOMContentLoaded', createBarChart);

// update chart each hour
setInterval(updateChartPeriodically, 3600000);

// ===========================
// connection section
// ===========================
document.addEventListener("DOMContentLoaded", async () => {
    const appContent = document.getElementById("app-content");
    const connectSection = document.getElementById("connect-section");

    if (isAuthenticated && hasAccessToken) {
        connectSection.style.display = "none";
        appContent.classList.remove("hidden");
        await loadAllData();
    } else {
        connectSection.style.display = "flex";
        appContent.classList.add("hidden");
    }
});

document.getElementById("connect-btn").addEventListener("click", initializePlaid);