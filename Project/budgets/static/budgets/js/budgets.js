document.addEventListener('DOMContentLoaded', () => {
    const popup = document.getElementById('popup-form');
    const editPopup = document.getElementById('editBudgetPopup');
    const addBudgetBtn = document.getElementById('add-budget-btn');
    const closePopupBtn = document.getElementById('close-popup');
    const addBudgetForm = document.getElementById('add-budget-form');
    document.getElementById("deleteBudgetBtn").addEventListener("click", deleteBudget);
    document.getElementById("saveChangesBtn").addEventListener("click", saveBudgetChanges);

    // show popup
    addBudgetBtn.addEventListener('click', () => {
        popup.style.display = 'block';
    });

    // close popup
    closePopupBtn.addEventListener('click', () => {
        popup.style.display = 'none';
    });

    // close popup when clicking off
    window.addEventListener('click', e => {
        if (e.target === popup) {
            popup.style.display = 'none';
        }
        if (e.target === editPopup) {
            closeEditPopup();
        }
    });

    // add budget
    addBudgetForm.addEventListener('submit', async e => {
        e.preventDefault();

        const name = document.getElementById('budget-name').value;
        const targetAmount = parseFloat(document.getElementById('budget-amount').value);
        const category = document.getElementById('budget-category').value;
        const timePeriod = document.getElementById('budget-time-period').value;

        if (!name || isNaN(targetAmount) || !category || !timePeriod) {
            alert('Please fill in all fields correctly.');
            return;
        }

        try {
            const response = await fetch('/add-budget/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCSRFToken() },
                body: JSON.stringify({ name, target_amount: targetAmount, category, time_period: timePeriod }),
            });

            const result = await response.json();

            if (response.ok) {
                popup.style.display = 'none';
                addBudgetForm.reset();
                loadBudgets();
            } else {
                alert(`Error: ${result.error}`);
            }
        } catch (error) {
            console.error('Error adding budget:', error);
        }
    });

    // fetch and add categories
    let cachedCategories = [];

    async function fetchCategories() {
        try {
            const response = await fetch('/get-categories/');
            const categories = await response.json();
    
            if (response.ok) {
                cachedCategories = categories;
                populateCategoryDropdown(categories, "budget-category");
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
    
        categorySelect.innerHTML = '<option value="" disabled>Select Category</option>';
        categories.forEach(category => {
            const option = document.createElement("option");
            option.value = category;
            option.textContent = category;
            categorySelect.appendChild(option);
        });
    }
    
    fetchCategories();

    // fetch budgets
    async function fetchBudgets() {
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

    // render budgets to html
    function renderBudgets(budgets) {
        const budgetList = document.getElementById('budget-list');
        budgetList.innerHTML = "";

        if (!budgets || budgets.length === 0) {
            budgetList.innerHTML = "<p>No budgets set yet.</p>";
            return;
        }

        budgets.forEach(budget => {
            const percentage = Math.min(Math.abs((budget.current_amount / budget.target_amount) * 100), 100);
            const isMaxedOut = percentage >= 100;

            const budgetItem = document.createElement('div');
            budgetItem.classList.add('budget-item');
            budgetItem.innerHTML = `
                <div class="budget-progress">
                    <svg viewBox="0 0 100 100" class="progress-circle">
                        <circle class="progress-background" cx="50" cy="50" r="45"></circle>
                        <circle class="progress-bar" cx="50" cy="50" r="45"
                            stroke-dasharray="282.6"
                            stroke-dashoffset="${282.6 - (282.6 * percentage) / 100}"
                            style="stroke: ${isMaxedOut ? 'red' : '#4caf50'};">
                        </circle>
                        <text x="50" y="55" text-anchor="middle" class="progress-text">${Math.round(percentage)}%</text>
                    </svg>
                </div>
                <div class="budget-details">
                    <h3>${budget.name}</h3>
                    <p>Target: £${budget.target_amount.toFixed(2)}</p>
                    <p>Current: £${budget.current_amount.toFixed(2)}</p>
                    <p>Category: ${budget.category}</p>
                    <p>Time Period: ${budget.time_period}</p>
                </div>
                <button class="edit-budget-btn" 
                    data-id="${budget.id}"
                    data-name="${budget.name}"
                    data-target="${budget.target_amount}"
                    data-category="${budget.category}"
                    data-period="${budget.time_period}"
                ></button>
            `;

            budgetList.appendChild(budgetItem);
        });

        // event listeners for edit
        document.querySelectorAll('.edit-budget-btn').forEach(button => {
            button.addEventListener('click', (event) => {
                const button = event.target;
                openEditPopup(
                    button.dataset.id, 
                    button.dataset.name, 
                    button.dataset.target, 
                    button.dataset.category, 
                    button.dataset.period
                );
            });
        });
    }

    // fetch & render budgets
    async function loadBudgets() {
        const budgets = await fetchBudgets();
        renderBudgets(budgets);
    }
    loadBudgets();

    // edit budget
    function openEditPopup(id, name, target, category, period) {
        document.getElementById("editBudgetId").value = id;
        document.getElementById("editBudgetName").value = name;
        document.getElementById("editBudgetTarget").value = target;
        document.getElementById("editBudgetTimePeriod").value = period;
    
        const categorySelect = document.getElementById("editBudgetCategory");
        categorySelect.innerHTML = '<option value="" disabled>Select Category</option>';
    
        cachedCategories.forEach(cat => {
            const option = document.createElement("option");
            option.value = cat;
            option.textContent = cat;
            if (cat === category) {
                option.selected = true;
            }
            categorySelect.appendChild(option);
        });
    
        editPopup.style.display = "flex";
    }

    async function saveBudgetChanges() {
        const id = document.getElementById("editBudgetId").value;
        if (!id) {
            alert("Error: Budget ID is missing.");
            return;
        }

        const name = document.getElementById("editBudgetName").value;
        const target = parseFloat(document.getElementById("editBudgetTarget").value);
        const category = document.getElementById("editBudgetCategory").value;
        const timePeriod = document.getElementById("editBudgetTimePeriod").value;

        try {
            const response = await fetch(`/edit-budget/${id}/`, {
                method: "POST",
                headers: { "Content-Type": "application/json", "X-CSRFToken": getCSRFToken() },
                body: JSON.stringify({ name, target_amount: target, category, time_period: timePeriod })
            });

            if (!response.ok) {
                alert("Error updating budget.");
                return;
            }

            closeEditPopup();
            loadBudgets();
        } catch (error) {
            console.error("Error saving budget changes:", error);
        }
    }

    // delete a budget
    async function deleteBudget() {
        const id = document.getElementById("editBudgetId").value;

        if (!id || !confirm("Are you sure you want to delete this budget?")) return;

        try {
            const response = await fetch(`/delete-budget/${id}/`, {
                method: "POST",
                headers: { "X-CSRFToken": getCSRFToken() }
            });

            if (!response.ok) {
                alert("Error deleting budget.");
                return;
            }

            closeEditPopup();
            loadBudgets();
        } catch (error) {
            console.error("Error deleting budget:", error);
        }
    }

    // fetch token
    function getCSRFToken() {
        return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    }

    // close edit popup
    function closeEditPopup() {
        editPopup.style.display = "none";
    }
});
