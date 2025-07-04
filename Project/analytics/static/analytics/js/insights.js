document.addEventListener('DOMContentLoaded', () => {
    if (typeof Chart === 'undefined') {
        console.error('Chart.js is not loaded');
    }
});

// get all transactions for insights
async function getAllTransactionsInsights() {
    try {
        const response = await fetch('/get-all-transactions-insights/');
        const data = await response.json();
        return data.transactions;
    } catch (error) {
        console.error('Error fetching transactions:', error);
    }
}

// fetch category breakdown data
async function getCategoryBreakdown() {
    try {
        const response = await fetch('/get-category-breakdown/');
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching transactions:', error);
    }

}

// fetch account breakdown data
async function getAccountBreakdown() {
    try {
        const response = await fetch('/get-account-breakdown/');
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching transactions:', error);
    }

}

// fetch stats
async function getSpendingStatistics() {
    try {
        const response = await fetch('/get-spending-statistics/');
        const data = await response.json();

        if (data && !data.error) {
            displaySpendingStatistics(data);
        } else {
            console.error('Error:', data ? data.error : 'Unknown error');
            displaySpendingStatistics({ highest_received_transaction: null, highest_spent_transaction: null });
        }
    } catch (error) {
        console.error('Error fetching transactions:', error);
        displaySpendingStatistics({ highest_received_transaction: null, highest_spent_transaction: null });
    }
}

// create spending analytics chart
async function createSpendingAnalyticsChart() {
    try {
        // fetch transactions
        const transactions = await getAllTransactionsInsights();

        // group transactions by time period
        function groupTransactions(transactions, timePeriod) {
            const groupedData = {};
            const monthOrder = ['January', 'February', 'March', 'April', 'May', 'June', 
                                'July', 'August', 'September', 'October', 'November', 'December'];
        
            transactions.forEach(transaction => {
                const date = new Date(transaction.date);
                let key;
                
                // select correct transactions 
                switch(timePeriod) {
                    case 'weekly':
                        const startOfWeek = new Date(date);
                        startOfWeek.setDate(date.getDate() - date.getDay());
                        key = startOfWeek.toISOString().split('T')[0];
                        break;
                    case 'monthly':
                        key = date.toLocaleString('default', { month: 'long', year: 'numeric' });
                        break;
                    case 'annual':
                        key = date.getFullYear().toString();
                        break;
                }
        
                if (!groupedData[key]) {
                    groupedData[key] = {
                        spending: 0,
                        income: 0
                    };
                }
        
                // separate income and spending 
                if (transaction.is_received) {
                    groupedData[key].income += transaction.amount;
                } else {
                    groupedData[key].spending += transaction.amount;
                }
            });
        
            // sort by time period
            const sortedKeys = Object.keys(groupedData).sort((a, b) => {
                if (timePeriod === 'weekly') {
                    return new Date(a) - new Date(b);
                } else if (timePeriod === 'monthly') {
                    const [monthA, yearA] = a.split(' ');
                    const [monthB, yearB] = b.split(' ');
                    
                    if (yearA !== yearB) return parseInt(yearA) - parseInt(yearB);
                    return monthOrder.indexOf(monthA) - monthOrder.indexOf(monthB);
                } else if (timePeriod === 'annual') {
                    return parseInt(a) - parseInt(b);
                }
            });
        
            // create a new object with the sorted keys
            const sortedGroupedData = {};
            sortedKeys.forEach(key => {
                sortedGroupedData[key] = groupedData[key];
            });
        
            return sortedGroupedData;
        }

        // create chart
        function createChart(groupedData, timePeriod) {
            const labels = Object.keys(groupedData);
            const spending = labels.map(label => groupedData[label].spending);
            const income = labels.map(label => groupedData[label].income);
        
            // calc averages
            const averageSpending = spending.reduce((a, b) => a + b, 0) / spending.length;
            const averageIncome = income.reduce((a, b) => a + b, 0) / income.length;
            
            // data and formatting
            const chartData = {
                labels: labels,
                datasets: [
                    {
                        label: 'Spending',
                        data: spending,
                        backgroundColor: 'rgba(255, 99, 132, 0.6)',
                        borderColor: 'rgba(255, 99, 132, 1)',
                        borderWidth: 1
                    },
                    {
                        label: 'Income',
                        data: income,
                        backgroundColor: 'rgba(75, 192, 192, 0.6)',
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 1
                    },
                    {
                        type: 'line',
                        label: 'Average Spending',
                        data: labels.map(() => averageSpending),
                        borderColor: 'rgba(255, 99, 132, 0.5)',
                        borderDash: [5, 5],
                        fill: false,
                        pointRadius: 0,
                        borderWidth: 2
                    },
                    {
                        type: 'line',
                        label: 'Average Income',
                        data: labels.map(() => averageIncome),
                        borderColor: 'rgba(75, 192, 192, 0.5)',
                        borderDash: [5, 5],
                        fill: false,
                        pointRadius: 0,
                        borderWidth: 2
                    }
                ]
            };
        
            const ctx = document.getElementById('spending-insights-chart');
            
            if (!ctx) {
                console.error('Canvas element not found');
                return;
            }
        
            const chartContext = ctx.getContext('2d');
        
            if (window.spendingChart instanceof Chart) {
                window.spendingChart.destroy();
            }
        
            window.spendingChart = new Chart(chartContext, {
                type: 'bar',
                data: chartData,
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: `${timePeriod.charAt(0).toUpperCase() + timePeriod.slice(1)} Spending Analytics`
                        },
                        legend: {
                            display: true
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    if (context.datasetIndex === 2) {
                                        return `Average Spending: $${averageSpending.toFixed(2)}`;
                                    }
                                    if (context.datasetIndex === 3) {
                                        return `Average Income: $${averageIncome.toFixed(2)}`;
                                    }
                                    return context.formattedValue;
                                }
                            }
                        }
                    },
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: timePeriod.charAt(0).toUpperCase() + timePeriod.slice(1)
                            }
                        },
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }

        const timePeriodSelect = document.getElementById('spending-time-period-select');
        
        // update chart
        function updateChart() {
            const timePeriod = timePeriodSelect.value;
            const groupedData = groupTransactions(transactions, timePeriod);
            createChart(groupedData, timePeriod);
        }

        // monitor time changes
        timePeriodSelect.addEventListener('change', updateChart);

        updateChart();

    } catch (error) {
        console.error('Error in createSpendingAnalyticsChart:', error);
    }
}

// create category spending chart
async function createCategoryBreakdownChart() {
    // stores chart info
    let categoryChart;

    // creates chart
    function createChart(data) {
        const ctx = document.getElementById('category-breakdown-chart').getContext('2d');
    
        // destroy existing chart if it exists
        if (categoryChart instanceof Chart) {
            categoryChart.destroy();
        }
    
        // create donut chart
        categoryChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: data.categories,
                datasets: [{
                    label: 'Spending by Category',
                    data: data.amounts,
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.6)',
                        'rgba(54, 162, 235, 0.6)',
                        'rgba(255, 206, 86, 0.6)',
                        'rgba(75, 192, 192, 0.6)',
                        'rgba(153, 102, 255, 0.6)',
                        'rgba(255, 159, 64, 0.6)',
                    ],
                    borderColor: '#1f2428',
                    borderWidth: 3
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false,
                    },
                    tooltip: {
                        callbacks: {
                            label: function(tooltipItem) {
                                return `${tooltipItem.label}: ${data.percentages[tooltipItem.dataIndex]}%`;
                            }
                        }
                    }
                }
            }
        });
    }

    // update chart with data
    async function updateChart() {
        try {
            const data = await getCategoryBreakdown();
            console.log('Category Data:', data);
    
            if (data && data.categories && data.amounts) {
                if (data.categories.length > 0) {
                    createChart(data);
                } else {
                    console.warn('No categories found');
                    const ctx = document.getElementById('category-breakdown-chart').getContext('2d');
                    ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
                }
            } else {
                console.error('Invalid data received for category breakdown chart');
            }
        } catch (error) {
            console.error('Error updating chart:', error);
        }
    }

    updateChart();
}

// create account breakdown chart
async function createAccountBreakdownChart() {
    let accountChart;

    // create chart
    function createChart(data) {
        const ctx = document.getElementById('account-breakdown-chart').getContext('2d');
    
        // destroy existing chart
        if (accountChart instanceof Chart) {
            accountChart.destroy();
        }
    
        // create chart
        accountChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: data.accounts,
                datasets: [{
                    label: 'Transactions by Account',
                    data: data.transaction_counts,
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.6)',
                        'rgba(54, 162, 235, 0.6)',
                        'rgba(255, 206, 86, 0.6)',
                        'rgba(75, 192, 192, 0.6)',
                        'rgba(153, 102, 255, 0.6)',
                        'rgba(255, 159, 64, 0.6)',
                    ],
                    borderColor: '#1f2428',
                    borderWidth: 3
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false,
                    },
                    tooltip: {
                        callbacks: {
                            label: function(tooltipItem) {
                                return `${tooltipItem.label}: ${data.percentages[tooltipItem.dataIndex]}%`;
                            }
                        }
                    }
                }
            }
        });
    }

    // update chart with data
    async function updateChart() {
        try {
            const data = await getAccountBreakdown();
            console.log('Account Data:', data);
    
            if (data && data.accounts && data.transaction_counts) {
                if (data.accounts.length > 0) {
                    createChart(data);
                } else {
                    console.warn('No accounts found');
                    const ctx = document.getElementById('account-breakdown-chart').getContext('2d');
                    ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
                }
            } else {
                console.error('Invalid data received for account breakdown chart');
            }
        } catch (error) {
            console.error('Error updating chart:', error);
        }
    }

    updateChart();
}

// display spending data
function displaySpendingStatistics(data) {
    const statisticsBox = document.getElementById('statistics-box');

    const { highest_received_transaction, highest_spent_transaction, transaction_count } = data;

    const statisticsInfo = `
        <div class="statistics-summary">
            <h2 class="count-heading">${transaction_count} Total Transactions</h2>
        </div>
    `;
    statisticsBox.insertAdjacentHTML('beforeend', statisticsInfo);

    if (highest_received_transaction) {
        const receivedTransactionInfo = `
            <h2 class="largest-heading">Largest Received Transaction:</h2>
            <div class="transaction-item received">
                <div class="transaction-details">
                    <h3>${highest_received_transaction.name}</h3>
                    <h3>${highest_received_transaction.account_name || ''}</h3>
                    <p class="txn-amount">£${Math.abs(highest_received_transaction.amount).toFixed(2)}</p>
                    <p>${highest_received_transaction.date} - ${highest_received_transaction.category}</p>
                </div>
            </div>
        `;
        statisticsBox.insertAdjacentHTML('beforeend', receivedTransactionInfo);
    }

    if (highest_spent_transaction) {
        const spentTransactionInfo = `
            <h2 class="largest-heading">Largest Spent Transaction:</h2>
            <div class="transaction-item sent">
                <div class="transaction-details">
                    <h3>${highest_spent_transaction.name}</h3>
                    <h3>${highest_spent_transaction.account_name || ''}</h3>
                    <p class="txn-amount">£${Math.abs(highest_spent_transaction.amount).toFixed(2)}</p>
                    <p>${highest_spent_transaction.date} - ${highest_spent_transaction.category}</p>
                </div>
            </div>
        `;
        statisticsBox.insertAdjacentHTML('beforeend', spentTransactionInfo);
    }

    if (!highest_received_transaction && !highest_spent_transaction) {
        const message = `
            <div class="no-transaction">
                <p>No transactions found.</p>
            </div>
        `;
        statisticsBox.insertAdjacentHTML('beforeend', message);
    }
}


// call functions
document.addEventListener('DOMContentLoaded', () => {
    createSpendingAnalyticsChart();
    createCategoryBreakdownChart();
    createAccountBreakdownChart();
    getSpendingStatistics();
});