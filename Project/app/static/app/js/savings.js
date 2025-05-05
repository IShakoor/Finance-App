document.addEventListener('DOMContentLoaded', () => {
    // load content
    const popup = document.getElementById('popup-form');
    const editPopup = document.getElementById('editGoalPopup')
    const addGoalBtn = document.getElementById('add-goal-btn');
    const closePopupBtn = document.getElementById('close-popup');
    const addGoalForm = document.getElementById('add-goal-form');
    document.getElementById("deleteGoalBtn").addEventListener("click", deleteGoal);
    document.getElementById("saveChangesBtn").addEventListener("click", saveGoalChanges);
    
    // show popup
    addGoalBtn.addEventListener('click', () => {
        popup.style.display = 'block';
    });

    // close popup
    closePopupBtn.addEventListener('click', () => {
        popup.style.display = 'none';
    });

    // close popup when clicking outside
    window.addEventListener('click', e => {
        if (e.target === popup) {
            popup.style.display = 'none';
        }
        if (e.target === editPopup) {
            closeEditPopup()
        }
    });

    // add goal
    addGoalForm.addEventListener('submit', async e => {
        e.preventDefault();

        const name = document.getElementById('goal-name').value;
        const targetAmount = parseFloat(document.getElementById('goal-amount').value);
        const currentAmount = parseFloat(document.getElementById('goal-current').value);
        const goalDate = document.getElementById('goal-date').value;

        if (!name || isNaN(targetAmount) || isNaN(currentAmount) || !goalDate) {
            alert('Please fill in all fields correctly.');
            return;
        }

        try {
            const response = await fetch('/add-savings-goal/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCSRFToken() },
                body: JSON.stringify({ name, target_amount: targetAmount, current_amount: currentAmount, goal_date: goalDate }),
            });

            const result = await response.json();

            if (response.ok) {
                popup.style.display = 'none';
                addGoalForm.reset();
                fetchGoals();
            } else {
                alert(`Error: ${result.error}`);
            }
        } catch (error) {
            console.error('Error adding goal:', error);
        }
    });

    // fetch all goals
    async function fetchGoals() {
        try {
            const response = await fetch('/get-all-goals/');
            const data = await response.json();
    
            if (data.error) {
                console.error("Error fetching goals:", data.error);
                return;
            }
    
            const goalsList = document.getElementById('goals-list');
            goalsList.innerHTML = "";
    
            if (data.goals.length === 0) {
                goalsList.innerHTML = "<p>No savings goals yet.</p>";
                return;
            }
    
            data.goals.forEach(goal => {
                const percentage = Math.min((goal.current_amount / goal.target_amount) * 100, 100);
    
                const goalItem = document.createElement('div');
                goalItem.classList.add('goal-item');
                goalItem.innerHTML = `
                    <div class="goal-progress">
                        <svg viewBox="0 0 100 100" class="progress-circle">
                            <circle class="progress-background" cx="50" cy="50" r="45"></circle>
                            <circle class="progress-bar" cx="50" cy="50" r="45"
                                stroke-dasharray="282.6"
                                stroke-dashoffset="${282.6 - (282.6 * percentage) / 100}">
                            </circle>
                            <text x="50" y="55" text-anchor="middle" class="progress-text">${Math.round(percentage)}%</text>
                        </svg>
                    </div>
                    <div class="goal-details">
                        <h3>${goal.name}</h3>
                        <p>Target: £${goal.target_amount.toFixed(2)}</p>
                        <p>Current: £${goal.current_amount.toFixed(2)}</p>
                        <p>Goal Date: ${goal.goal_date}</p>
                    </div>
                    <button class="edit-goal-btn" data-id="${goal.id}"
                        data-name="${goal.name}" 
                        data-target="${goal.target_amount}" 
                        data-current="${goal.current_amount}" 
                        data-date="${goal.goal_date}">
                    </button>
                `;
    
                goalsList.appendChild(goalItem);
            });
    
            document.querySelectorAll('.edit-goal-btn').forEach(button => {
                button.addEventListener('click', (event) => {
                    const button = event.target;
                    openEditPopup(button.dataset.id, button.dataset.name, button.dataset.target, button.dataset.current, button.dataset.date);
                });
            });
    
        } catch (error) {
            console.error('Error fetching goals:', error);
        }
    }
    fetchGoals();

    // edit goals
    function openEditPopup(id, name, target, current, date) {
        document.getElementById("editGoalId").value = id;
        document.getElementById("editGoalName").value = name;
        document.getElementById("editGoalTarget").value = target;
        document.getElementById("editGoalCurrent").value = current;
        document.getElementById("editGoalDate").value = date;
    
        const popup = document.getElementById("editGoalPopup");
        popup.style.display = "flex";
    }
        
    async function saveGoalChanges() {
        const id = document.getElementById("editGoalId").value;
        if (!id) {
            alert("Error: Goal ID is missing.");
            return;
        }
    
        const name = document.getElementById("editGoalName").value;
        const target = parseFloat(document.getElementById("editGoalTarget").value);
        const current = parseFloat(document.getElementById("editGoalCurrent").value);
        const date = document.getElementById("editGoalDate").value;
    
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
    
            closeEditPopup();
            fetchGoals();
        } catch (error) {
            console.error("Error saving goal changes:", error);
        }
    }
    
    // delete a goal
    async function deleteGoal() {
        const id = document.getElementById("editGoalId").value;
        
        if (!id) {
            alert("Error: Goal ID is missing.");
            return;
        }
    
        if (!confirm("Are you sure you want to delete this goal?")) return;
    
        try {
            const response = await fetch(`/delete-goal/${id}/`, {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCSRFToken()
                }
            });
    
            if (!response.ok) {
                console.error("Failed to delete goal:", await response.text());
                alert("Error deleting goal.");
                return;
            }
    
            closeEditPopup();
            fetchGoals();
        } catch (error) {
            console.error("Error deleting goal:", error);
        }
    }

    // fetch token
    function getCSRFToken() {
        return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    }
});

// close edit popup
function closeEditPopup() {
    document.getElementById("editGoalPopup").style.display = "none";
}