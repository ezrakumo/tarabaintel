<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TarabaInsight | My Rewards</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .glass-panel {
            background: rgba(31, 41, 55, 0.7);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(75, 85, 99, 0.4);
            transition: all 0.3s ease;
        }
        .hover-lift:hover {
            transform: translateY(-4px);
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
        }
        .tier-badge {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .points-glow {
            text-shadow: 0 0 20px rgba(251, 191, 36, 0.5);
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(15px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .fade-in { animation: fadeIn 0.7s ease-out forwards; }
    </style>
</head>
<body class="bg-gray-950 text-gray-100 min-h-screen font-sans">

    <header class="bg-gray-900 border-b border-gray-800 sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
            <div class="flex items-center space-x-3">
                <div class="bg-blue-600 p-2 rounded-lg">
                    <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                </div>
                <div>
                    <h1 class="text-xl font-bold text-white tracking-wide">TARABA INSIGHT</h1>
                    <p class="text-xs text-gray-400">Rewards & Recognition Center</p>
                </div>
            </div>
            <div class="flex items-center space-x-4">
                <a href="/api/briefing/" class="text-sm text-blue-400 hover:text-blue-300">← Briefing Center</a>
                <span id="user-tier" class="tier-badge text-white text-xs font-bold px-3 py-1 rounded-full"></span>
            </div>
        </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 fade-in">

        <!-- Points Balance Cards -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div class="glass-panel rounded-xl p-6 text-center hover-lift">
                <p class="text-gray-400 text-sm uppercase tracking-wider mb-2">Available Points</p>
                <p id="total-points" class="text-5xl font-bold text-yellow-400 points-glow">0</p>
                <p class="text-xs text-gray-500 mt-2">Ready to redeem</p>
            </div>
            <div class="glass-panel rounded-xl p-6 text-center hover-lift">
                <p class="text-gray-400 text-sm uppercase tracking-wider mb-2">Lifetime Earned</p>
                <p id="lifetime-points" class="text-5xl font-bold text-green-400">0</p>
                <p class="text-xs text-gray-500 mt-2">Total contribution</p>
            </div>
            <div class="glass-panel rounded-xl p-6 text-center hover-lift">
                <p class="text-gray-400 text-sm uppercase tracking-wider mb-2">Next Tier</p>
                <p id="next-tier" class="text-2xl font-bold text-purple-400">—</p>
                <p id="points-to-next" class="text-xs text-gray-500 mt-2">0 pts needed</p>
            </div>
        </div>

        <!-- Main Grid -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">

            <!-- Left: Recent Transactions -->
            <div class="lg:col-span-2 space-y-6">
                <div class="glass-panel rounded-xl p-6">
                    <h3 class="text-lg font-semibold text-white mb-4 flex items-center">
                        <svg class="w-5 h-5 mr-2 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
                        </svg>
                        Recent Transactions
                    </h3>
                    <div id="transactions-list" class="space-y-3">
                        <p class="text-gray-500 text-center py-4">Loading...</p>
                    </div>
                </div>

                <!-- Active Redemptions -->
                <div class="glass-panel rounded-xl p-6 border-l-4 border-blue-500">
                    <h3 class="text-lg font-semibold text-white mb-4 flex items-center">
                        <svg class="w-5 h-5 mr-2 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"></path>
                        </svg>
                        Active Redemptions
                    </h3>
                    <div id="redemptions-list" class="space-y-3">
                        <p class="text-gray-500 text-center py-4">No active redemptions</p>
                    </div>
                </div>
            </div>

            <!-- Right: Available Rewards -->
            <div class="space-y-6">
                <div class="glass-panel rounded-xl p-6 border-l-4 border-green-500">
                    <h3 class="text-lg font-semibold text-white mb-4 flex items-center">
                        <svg class="w-5 h-5 mr-2 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v13m0-13V6a2 2 0 112 2h-2zm0 0V5.5A2.5 2.5 0 109.5 8H12zm-7 4h14M5 12a2 2 0 110-4h14a2 2 0 110 4M5 12v7a2 2 0 002 2h10a2 2 0 002-2v-7"></path>
                        </svg>
                        Available Rewards
                    </h3>
                    <div id="rewards-list" class="space-y-3">
                        <p class="text-gray-500 text-center py-4">Loading rewards...</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- My Intel Reports -->
        <div class="glass-panel rounded-xl p-6">
            <h3 class="text-lg font-semibold text-white mb-4 flex items-center">
                <svg class="w-5 h-5 mr-2 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                </svg>
                My Intelligence Reports
                <span id="reports-summary" class="ml-2 text-sm text-gray-400"></span>
            </h3>
            <div id="reports-list" class="space-y-3">
                <p class="text-gray-500 text-center py-4">Loading reports...</p>
            </div>
        </div>

    </main>

    <!-- Redeem Modal -->
    <div id="redeem-modal" class="hidden fixed inset-0 bg-black bg-opacity-75 z-50 flex items-center justify-center p-4">
        <div class="glass-panel rounded-xl p-6 max-w-md w-full">
            <h3 class="text-lg font-semibold text-white mb-4">Confirm Redemption</h3>
            <div id="redeem-details" class="text-gray-300 mb-4"></div>
            <textarea id="delivery-details" placeholder="Delivery details (phone, address, etc.)" 
                class="w-full bg-gray-800 border border-gray-700 rounded-lg p-3 text-white mb-4" rows="3"></textarea>
            <div class="flex space-x-3">
                <button onclick="closeRedeemModal()" class="flex-1 bg-gray-700 hover:bg-gray-600 text-white py-2 rounded-lg">Cancel</button>
                <button onclick="confirmRedeem()" class="flex-1 bg-green-600 hover:bg-green-700 text-white py-2 rounded-lg">Confirm</button>
            </div>
        </div>
    </div>

    <script>
        const API_BASE = '/api/rewards';
        let selectedRewardId = null;

        // Load dashboard data
        async function loadDashboard() {
            try {
                const response = await fetch(`${API_BASE}/dashboard/`, {
                    credentials: 'include',
                    headers: { 'Accept': 'application/json' }
                });
                
                if (!response.ok) {
                    // Not authenticated - show login prompt
                    document.body.innerHTML = `
                        <div class="min-h-screen flex items-center justify-center">
                            <div class="glass-panel rounded-xl p-8 text-center">
                                <h2 class="text-2xl font-bold text-white mb-4">Authentication Required</h2>
                                <p class="text-gray-400 mb-6">Please log in to view your rewards dashboard.</p>
                                <a href="/admin/" class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg">Go to Login</a>
                            </div>
                        </div>`;
                    return;
                }
                
                const data = await response.json();
                renderDashboard(data);
            } catch (error) {
                console.error('Failed to load dashboard:', error);
            }
        }

        function renderDashboard(data) {
            // Profile
            document.getElementById('user-tier').textContent = data.profile.tier;
            document.getElementById('total-points').textContent = data.profile.total_points.toLocaleString();
            document.getElementById('lifetime-points').textContent = data.profile.lifetime_points.toLocaleString();
            
            if (data.next_tier) {
                document.getElementById('next-tier').textContent = data.next_tier;
                document.getElementById('points-to-next').textContent = `${data.points_to_next_tier} pts needed`;
            } else {
                document.getElementById('next-tier').textContent = 'MAX';
                document.getElementById('points-to-next').textContent = 'Highest tier achieved!';
            }

            // Transactions
            const txList = document.getElementById('transactions-list');
            if (data.recent_transactions.length === 0) {
                txList.innerHTML = '<p class="text-gray-500 text-center py-4">No transactions yet. Submit intel to earn points!</p>';
            } else {
                txList.innerHTML = data.recent_transactions.map(tx => `
                    <div class="bg-gray-800 rounded-lg p-3 border-l-2 ${tx.points > 0 ? 'border-green-500' : 'border-red-500'}">
                        <div class="flex justify-between items-start">
                            <div>
                                <p class="text-sm font-semibold text-white">${tx.transaction_type_display}</p>
                                <p class="text-xs text-gray-400 mt-1">${tx.description}</p>
                            </div>
                            <div class="text-right">
                                <p class="text-lg font-bold ${tx.points > 0 ? 'text-green-400' : 'text-red-400'}">
                                    ${tx.points > 0 ? '+' : ''}${tx.points}
                                </p>
                                <p class="text-xs text-gray-500">${new Date(tx.created_at).toLocaleDateString()}</p>
                            </div>
                        </div>
                    </div>
                `).join('');
            }

            // Redemptions
            const redList = document.getElementById('redemptions-list');
            if (data.active_redemptions.length === 0) {
                redList.innerHTML = '<p class="text-gray-500 text-center py-4">No active redemptions</p>';
            } else {
                redList.innerHTML = data.active_redemptions.map(r => `
                    <div class="bg-gray-800 rounded-lg p-3 border-l-2 border-blue-500">
                        <div class="flex justify-between items-start">
                            <div>
                                <p class="text-sm font-semibold text-white">${r.reward_title}</p>
                                <p class="text-xs text-gray-400">${r.reward_category}</p>
                            </div>
                            <span class="text-xs px-2 py-1 rounded ${
                                r.status === 'PENDING' ? 'bg-yellow-900 text-yellow-300' :
                                r.status === 'APPROVED' ? 'bg-blue-900 text-blue-300' :
                                'bg-gray-700 text-gray-300'
                            }">${r.status}</span>
                        </div>
                        <p class="text-xs text-gray-500 mt-2">-${r.points_deducted} pts • ${new Date(r.created_at).toLocaleDateString()}</p>
                    </div>
                `).join('');
            }

            // Rewards
            const rewardsList = document.getElementById('rewards-list');
            if (data.affordable_rewards.length === 0) {
                rewardsList.innerHTML = '<p class="text-gray-500 text-center py-4">Earn more points to unlock rewards!</p>';
            } else {
                rewardsList.innerHTML = data.affordable_rewards.map(r => `
                    <div class="bg-gray-800 rounded-lg p-3 hover:bg-gray-750 cursor-pointer transition" onclick="openRedeemModal(${r.id}, '${r.title}', ${r.points_required})">
                        <div class="flex justify-between items-start mb-1">
                            <p class="text-sm font-semibold text-white">${r.title}</p>
                            <span class="text-xs bg-yellow-900 text-yellow-300 px-2 py-0.5 rounded">${r.points_required} pts</span>
                        </div>
                        <p class="text-xs text-gray-400">${r.description}</p>
                        <p class="text-xs text-gray-500 mt-1">Click to redeem →</p>
                    </div>
                `).join('');
            }

            // My Reports
            loadMyReports();
        }

        async function loadMyReports() {
            try {
                const response = await fetch(`${API_BASE}/my-reports/`, {
                    credentials: 'include'
                });
                if (!response.ok) return;
                
                const data = await response.json();
                const list = document.getElementById('reports-list');
                const summary = document.getElementById('reports-summary');
                
                summary.textContent = `(${data.summary.total_reports} reports • ${data.summary.total_points_earned} pts earned • avg quality: ${data.summary.average_quality_score})`;
                
                if (data.reports.length === 0) {
                    list.innerHTML = '<p class="text-gray-500 text-center py-4">No reports submitted yet</p>';
                } else {
                    list.innerHTML = data.reports.map(r => `
                        <div class="bg-gray-800 rounded-lg p-3 flex justify-between items-center">
                            <div>
                                <p class="text-sm font-semibold text-white">${r.issue_category} • ${r.lga_name}</p>
                                <p class="text-xs text-gray-400">${new Date(r.submitted_at).toLocaleString()}</p>
                            </div>
                            <div class="text-right">
                                <div class="flex items-center space-x-2">
                                    <span class="text-xs px-2 py-1 rounded ${
                                        r.intel_quality_score >= 70 ? 'bg-green-900 text-green-300' :
                                        r.intel_quality_score >= 40 ? 'bg-yellow-900 text-yellow-300' :
                                        'bg-gray-700 text-gray-300'
                                    }">Quality: ${r.intel_quality_score}</span>
                                    <span class="text-sm font-bold text-yellow-400">+${r.points_awarded} pts</span>
                                </div>
                            </div>
                        </div>
                    `).join('');
                }
            } catch (error) {
                console.error('Failed to load reports:', error);
            }
        }

        function openRedeemModal(id, title, points) {
        selectedRewardId = id;
            document.getElementById('redeem-details').innerHTML = `
                <p class="font-semibold text-white">${title}</p>
                <p class="text-yellow-400 mt-2">Cost: ${points} points</p>
                <p class="text-gray-400 text-sm mt-2">Your balance: ${document.getElementById('total-points').textContent} pts</p>
            `;
            document.getElementById('redeem-modal').classList.remove('hidden');
        }

        function closeRedeemModal() {
            document.getElementById('redeem-modal').classList.add('hidden');
            document.getElementById('delivery-details').value = '';
            selectedRewardId = null;
        }

        async function confirmRedeem() {
            const deliveryDetails = document.getElementById('delivery-details').value;
            try {
                const response = await fetch(`${API_BASE}/redemptions/`, {
                    method: 'POST',
                    credentials: 'include',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify({
                        reward_id: selectedRewardId,
                        delivery_details: deliveryDetails
                    })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    alert('✅ Redemption submitted! An admin will review it shortly.');
                    closeRedeemModal();
                    loadDashboard(); // Refresh
                } else {
                    alert('❌ ' + (data.error || 'Redemption failed'));
                }
            } catch (error) {
                alert('❌ Network error');
            }
        }

        function getCookie(name) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }

        // Load on page load
        loadDashboard();
    </script>
</body>
</html>