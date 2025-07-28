// Modern Dashboard JavaScript with Interactive Elements and Theme Support

class AquaMonitorDashboard {
    constructor() {
        this.currentTheme = 'light';
        this.charts = {};
        this.liveDataInterval = null;
        this.sensorData = {
            ph: [],
            temperature: [],
            turbidity: [],
            waterLevel: []
        };
        
        this.init();
    }

    init() {
        this.setupThemeToggle();
        this.setupNavigation();
        this.setupCharts();
        this.setupInteractiveElements();
        this.setupSpeciesManagement();
        this.setupAnalytics();
        this.setupSettings();
        this.startLiveDataSimulation();
        this.setupAnimations();
        this.loadInitialData();
    }

    // Theme Management
    setupThemeToggle() {
        const themeToggle = document.getElementById('themeToggle');
        const savedTheme = localStorage.getItem('theme') || 'light';
        
        this.setTheme(savedTheme);
        
        themeToggle.addEventListener('click', () => {
            this.currentTheme = this.currentTheme === 'light' ? 'dark' : 'light';
            this.setTheme(this.currentTheme);
        });
    }

    setTheme(theme) {
        this.currentTheme = theme;
        document.body.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        
        const themeIcon = document.querySelector('#themeToggle i');
        themeIcon.className = theme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
        
        // Update charts with new theme colors
        this.updateChartsTheme();
    }

    // Navigation System
    setupNavigation() {
        const menuItems = document.querySelectorAll('.menu-item');
        const sections = document.querySelectorAll('.content-section');

        menuItems.forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                
                // Remove active class from all items and sections
                menuItems.forEach(mi => mi.classList.remove('active'));
                sections.forEach(section => section.classList.remove('active'));
                
                // Add active class to clicked item
                item.classList.add('active');
                
                // Show corresponding section
                const targetSection = item.getAttribute('data-section');
                const section = document.getElementById(targetSection);
                if (section) {
                    section.classList.add('active');
                    this.animateSection(section);
                }
            });
        });
    }

    // Chart Setup and Management
    setupCharts() {
        this.createMiniCharts();
        this.createMainChart();
        this.createLiveChart();
    }

    createMiniCharts() {
        const miniChartConfigs = [
            { id: 'phMiniChart', color: '#10b981', data: this.generateMiniChartData() },
            { id: 'tempMiniChart', color: '#f59e0b', data: this.generateMiniChartData() },
            { id: 'turbidityMiniChart', color: '#ef4444', data: this.generateMiniChartData() },
            { id: 'waterLevelMiniChart', color: '#2563eb', data: this.generateMiniChartData() }
        ];

        miniChartConfigs.forEach(config => {
            const ctx = document.getElementById(config.id);
            if (ctx) {
                this.charts[config.id] = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: Array.from({length: 20}, (_, i) => i),
                        datasets: [{
                            data: config.data,
                            borderColor: config.color,
                            backgroundColor: config.color + '20',
                            borderWidth: 2,
                            fill: true,
                            tension: 0.4,
                            pointRadius: 0
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: { legend: { display: false } },
                        scales: {
                            x: { display: false },
                            y: { display: false }
                        },
                        elements: { point: { radius: 0 } }
                    }
                });
            }
        });
    }

    createMainChart() {
        const ctx = document.getElementById('mainChart');
        if (!ctx) return;

        const isDark = this.currentTheme === 'dark';
        const textColor = isDark ? '#cbd5e1' : '#64748b';
        const gridColor = isDark ? '#334155' : '#e2e8f0';

        this.charts.mainChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: this.generateTimeLabels(24),
                datasets: [
                    {
                        label: 'pH Level',
                        data: this.generateChartData(24, 6.5, 8.5),
                        borderColor: '#10b981',
                        backgroundColor: '#10b98120',
                        borderWidth: 3,
                        fill: false,
                        tension: 0.4
                    },
                    {
                        label: 'Temperature (°C)',
                        data: this.generateChartData(24, 20, 35),
                        borderColor: '#f59e0b',
                        backgroundColor: '#f59e0b20',
                        borderWidth: 3,
                        fill: false,
                        tension: 0.4
                    },
                    {
                        label: 'Turbidity (NTU)',
                        data: this.generateChartData(24, 100, 400),
                        borderColor: '#ef4444',
                        backgroundColor: '#ef444420',
                        borderWidth: 3,
                        fill: false,
                        tension: 0.4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: { color: textColor, usePointStyle: true }
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        backgroundColor: isDark ? '#1e293b' : '#ffffff',
                        titleColor: textColor,
                        bodyColor: textColor,
                        borderColor: gridColor,
                        borderWidth: 1
                    }
                },
                scales: {
                    x: {
                        grid: { color: gridColor },
                        ticks: { color: textColor }
                    },
                    y: {
                        grid: { color: gridColor },
                        ticks: { color: textColor }
                    }
                },
                interaction: {
                    mode: 'nearest',
                    axis: 'x',
                    intersect: false
                }
            }
        });
    }

    createLiveChart() {
        const ctx = document.getElementById('liveChart');
        if (!ctx) return;

        const isDark = this.currentTheme === 'dark';
        const textColor = isDark ? '#cbd5e1' : '#64748b';
        const gridColor = isDark ? '#334155' : '#e2e8f0';

        this.charts.liveChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    {
                        label: 'pH',
                        data: [],
                        borderColor: '#10b981',
                        backgroundColor: '#10b98120',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4
                    },
                    {
                        label: 'Temperature',
                        data: [],
                        borderColor: '#f59e0b',
                        backgroundColor: '#f59e0b20',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: { duration: 750 },
                plugins: {
                    legend: {
                        position: 'top',
                        labels: { color: textColor, usePointStyle: true }
                    }
                },
                scales: {
                    x: {
                        type: 'time',
                        time: { unit: 'minute' },
                        grid: { color: gridColor },
                        ticks: { color: textColor }
                    },
                    y: {
                        grid: { color: gridColor },
                        ticks: { color: textColor }
                    }
                }
            }
        });
    }

    // Interactive Elements
    setupInteractiveElements() {
        this.setupRefreshButton();
        this.setupExportButton();
        this.setupSpeciesPrediction();
        this.setupAlerts();
        this.setupTimeRangeSelector();
    }

    setupRefreshButton() {
        const refreshBtn = document.getElementById('refreshData');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.showLoading();
                this.refreshAllData();
                setTimeout(() => this.hideLoading(), 1500);
            });
        }
    }

    setupExportButton() {
        const exportBtn = document.getElementById('exportData');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => {
                this.exportData();
            });
        }
    }

    setupSpeciesPrediction() {
        const predictBtn = document.getElementById('predictSpecies');
        if (predictBtn) {
            predictBtn.addEventListener('click', () => {
                this.predictFishSpecies();
            });
        }
    }

    setupAlerts() {
        const clearAlertsBtn = document.getElementById('clearAlerts');
        if (clearAlertsBtn) {
            clearAlertsBtn.addEventListener('click', () => {
                this.clearAllAlerts();
            });
        }
    }

    setupTimeRangeSelector() {
        const timeRange = document.getElementById('timeRange');
        if (timeRange) {
            timeRange.addEventListener('change', (e) => {
                this.updateChartTimeRange(e.target.value);
            });
        }
    }

    // Data Management
    loadInitialData() {
        this.updateStatusCards();
        this.loadFishSpecies();
        this.loadAlerts();
    }

    updateStatusCards() {
        const statusData = {
            ph: { value: 7.2, status: 'optimal', trend: '+0.2' },
            temperature: { value: 26.5, status: 'optimal', trend: '-1.2' },
            turbidity: { value: 180, status: 'warning', trend: '+15' },
            waterLevel: { value: 85, status: 'optimal', trend: '0' }
        };

        Object.keys(statusData).forEach(key => {
            const data = statusData[key];
            const valueElement = document.getElementById(`${key}Value`);
            if (valueElement) {
                this.animateValue(valueElement, data.value, key === 'temperature' ? '°C' : key === 'turbidity' ? ' NTU' : key === 'waterLevel' ? '%' : '');
            }
        });
    }

    loadFishSpecies() {
        const speciesData = [
            { name: 'Tilapia', icon: '🐟', compatibility: 95, status: 'compatible' },
            { name: 'Catfish', icon: '🐠', compatibility: 88, status: 'compatible' },
            { name: 'Carp', icon: '🐟', compatibility: 72, status: 'compatible' },
            { name: 'Trout', icon: '🐠', compatibility: 45, status: 'incompatible' },
            { name: 'Bass', icon: '🐟', compatibility: 38, status: 'incompatible' },
            { name: 'Salmon', icon: '🐠', compatibility: 25, status: 'incompatible' }
        ];

        const speciesGrid = document.getElementById('speciesGrid');
        if (speciesGrid) {
            speciesGrid.innerHTML = speciesData.map(species => `
                <div class="species-card ${species.status}" data-species="${species.name}">
                    <div class="species-icon">${species.icon}</div>
                    <div class="species-name">${species.name}</div>
                    <div class="compatibility-score">${species.compatibility}% match</div>
                </div>
            `).join('');

            // Add click handlers
            speciesGrid.querySelectorAll('.species-card').forEach(card => {
                card.addEventListener('click', () => {
                    this.showSpeciesDetails(card.dataset.species);
                });
            });
        }
    }

    loadAlerts() {
        const alerts = [
            {
                type: 'warning',
                icon: 'fas fa-exclamation-triangle',
                title: 'Turbidity Level High',
                message: 'Current turbidity (180 NTU) exceeds optimal range',
                time: '5 minutes ago'
            },
            {
                type: 'info',
                icon: 'fas fa-info-circle',
                title: 'System Update',
                message: 'Sensor calibration completed successfully',
                time: '1 hour ago'
            },
            {
                type: 'danger',
                icon: 'fas fa-times-circle',
                title: 'pH Sensor Alert',
                message: 'pH sensor requires maintenance check',
                time: '2 hours ago'
            }
        ];

        const alertsList = document.getElementById('alertsList');
        if (alertsList) {
            alertsList.innerHTML = alerts.map(alert => `
                <div class="alert-item">
                    <div class="alert-icon ${alert.type}">
                        <i class="${alert.icon}"></i>
                    </div>
                    <div class="alert-content">
                        <div class="alert-title">${alert.title}</div>
                        <div class="alert-message">${alert.message}</div>
                    </div>
                    <div class="alert-time">${alert.time}</div>
                </div>
            `).join('');
        }
    }

    // Live Data Simulation
    startLiveDataSimulation() {
        this.liveDataInterval = setInterval(() => {
            this.updateLiveData();
        }, 3000);
    }

    updateLiveData() {
        const now = new Date();
        const liveChart = this.charts.liveChart;
        
        if (liveChart) {
            // Add new data point
            liveChart.data.labels.push(now);
            liveChart.data.datasets[0].data.push(6.8 + Math.random() * 1.4);
            liveChart.data.datasets[1].data.push(24 + Math.random() * 8);

            // Keep only last 20 points
            if (liveChart.data.labels.length > 20) {
                liveChart.data.labels.shift();
                liveChart.data.datasets.forEach(dataset => dataset.data.shift());
            }

            liveChart.update('none');
        }

        // Update status cards with slight variations
        this.updateStatusCardsLive();
    }

    updateStatusCardsLive() {
        const variations = {
            ph: (Math.random() - 0.5) * 0.1,
            temperature: (Math.random() - 0.5) * 0.5,
            turbidity: (Math.random() - 0.5) * 10,
            waterLevel: (Math.random() - 0.5) * 2
        };

        Object.keys(variations).forEach(key => {
            const element = document.getElementById(`${key}Value`);
            if (element) {
                const currentValue = parseFloat(element.textContent);
                const newValue = currentValue + variations[key];
                const suffix = key === 'temperature' ? '°C' : key === 'turbidity' ? ' NTU' : key === 'waterLevel' ? '%' : '';
                element.textContent = newValue.toFixed(1) + suffix;
            }
        });
    }

    // Interactive Functions
    predictFishSpecies() {
        this.showLoading();
        
        setTimeout(() => {
            const speciesCards = document.querySelectorAll('.species-card');
            speciesCards.forEach((card, index) => {
                setTimeout(() => {
                    card.style.transform = 'scale(1.05)';
                    setTimeout(() => {
                        card.style.transform = 'scale(1)';
                    }, 200);
                }, index * 100);
            });
            
            this.hideLoading();
            this.showNotification('AI prediction completed!', 'success');
        }, 2000);
    }

    // Species Management Functions
    setupSpeciesManagement() {
        this.loadSpeciesTable();
        
        const addSpeciesBtn = document.getElementById('addSpecies');
        if (addSpeciesBtn) {
            addSpeciesBtn.addEventListener('click', () => {
                this.showAddSpeciesModal();
            });
        }

        const speciesReportBtn = document.getElementById('speciesReport');
        if (speciesReportBtn) {
            speciesReportBtn.addEventListener('click', () => {
                this.generateSpeciesReport();
            });
        }
    }

    loadSpeciesTable() {
        const speciesData = [
            { name: 'Tilapia', phRange: '6.0-8.0', tempRange: '24-32°C', compatibility: '95%', status: 'optimal' },
            { name: 'Catfish', phRange: '6.0-8.0', tempRange: '24-30°C', compatibility: '88%', status: 'optimal' },
            { name: 'Common Carp', phRange: '6.5-8.5', tempRange: '20-28°C', compatibility: '72%', status: 'good' },
            { name: 'Grass Carp', phRange: '6.5-8.5', tempRange: '20-30°C', compatibility: '68%', status: 'good' },
            { name: 'Silver Carp', phRange: '6.5-8.5', tempRange: '20-28°C', compatibility: '65%', status: 'good' },
            { name: 'Trout', phRange: '6.5-7.5', tempRange: '10-18°C', compatibility: '45%', status: 'warning' },
            { name: 'Bass', phRange: '6.5-8.0', tempRange: '15-25°C', compatibility: '38%', status: 'warning' },
            { name: 'Salmon', phRange: '6.5-7.5', tempRange: '8-16°C', compatibility: '25%', status: 'danger' }
        ];

        const tableBody = document.getElementById('speciesTableBody');
        if (tableBody) {
            tableBody.innerHTML = speciesData.map(species => `
                <tr>
                    <td><strong>${species.name}</strong></td>
                    <td>${species.phRange}</td>
                    <td>${species.tempRange}</td>
                    <td>${species.compatibility}</td>
                    <td><span class="status ${species.status}">${species.status}</span></td>
                    <td>
                        <button class="btn btn-sm btn-secondary" onclick="dashboard.viewSpeciesDetails('${species.name}')">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-sm btn-primary" onclick="dashboard.editSpecies('${species.name}')">
                            <i class="fas fa-edit"></i>
                        </button>
                    </td>
                </tr>
            `).join('');
        }
    }

    // Analytics Functions
    setupAnalytics() {
        this.createAnalyticsCharts();
        
        const analyticsTimeframe = document.getElementById('analyticsTimeframe');
        if (analyticsTimeframe) {
            analyticsTimeframe.addEventListener('change', (e) => {
                this.updateAnalyticsTimeframe(e.target.value);
            });
        }
    }

    createAnalyticsCharts() {
        this.createTrendsChart();
        this.createDistributionChart();
        this.createAccuracyChart();
    }

    createTrendsChart() {
        const ctx = document.getElementById('trendsChart');
        if (!ctx) return;

        const isDark = this.currentTheme === 'dark';
        const textColor = isDark ? '#cbd5e1' : '#64748b';
        const gridColor = isDark ? '#334155' : '#e2e8f0';

        this.charts.trendsChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: this.generateTimeLabels(30),
                datasets: [
                    {
                        label: 'Water Quality Score',
                        data: this.generateTrendData(30),
                        borderColor: '#10b981',
                        backgroundColor: '#10b98120',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    x: {
                        grid: { color: gridColor },
                        ticks: { color: textColor }
                    },
                    y: {
                        grid: { color: gridColor },
                        ticks: { color: textColor },
                        min: 0,
                        max: 100
                    }
                }
            }
        });
    }

    createDistributionChart() {
        const ctx = document.getElementById('distributionChart');
        if (!ctx) return;

        const isDark = this.currentTheme === 'dark';
        const textColor = isDark ? '#cbd5e1' : '#64748b';

        this.charts.distributionChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Optimal', 'Good', 'Warning', 'Critical'],
                datasets: [{
                    data: [65, 25, 8, 2],
                    backgroundColor: ['#10b981', '#f59e0b', '#ef4444', '#dc2626'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: textColor }
                    }
                }
            }
        });
    }

    createAccuracyChart() {
        const ctx = document.getElementById('accuracyChart');
        if (!ctx) return;

        const isDark = this.currentTheme === 'dark';
        const textColor = isDark ? '#cbd5e1' : '#64748b';
        const gridColor = isDark ? '#334155' : '#e2e8f0';

        this.charts.accuracyChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['pH', 'Temperature', 'Turbidity', 'Water Level'],
                datasets: [{
                    label: 'Accuracy %',
                    data: [96, 94, 92, 98],
                    backgroundColor: ['#10b981', '#f59e0b', '#ef4444', '#2563eb'],
                    borderRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: {
                        grid: { display: false },
                        ticks: { color: textColor }
                    },
                    y: {
                        grid: { color: gridColor },
                        ticks: { color: textColor },
                        min: 80,
                        max: 100
                    }
                }
            }
        });
    }

    // Settings Functions
    setupSettings() {
        this.setupSliders();
        this.setupToggleSwitches();
        
        const saveSettingsBtn = document.getElementById('saveSettings');
        if (saveSettingsBtn) {
            saveSettingsBtn.addEventListener('click', () => {
                this.saveSettings();
            });
        }
    }

    setupSliders() {
        const sliders = document.querySelectorAll('.slider');
        sliders.forEach(slider => {
            const valueDisplay = slider.parentElement.querySelector('.setting-value');
            
            slider.addEventListener('input', (e) => {
                const value = parseFloat(e.target.value);
                const step = parseFloat(e.target.step) || 1;
                const displayValue = step < 1 ? value.toFixed(1) : value.toString();
                valueDisplay.textContent = displayValue;
            });
        });
    }

    setupToggleSwitches() {
        const toggles = document.querySelectorAll('.toggle-switch input');
        toggles.forEach(toggle => {
            toggle.addEventListener('change', (e) => {
                const setting = e.target.id;
                const enabled = e.target.checked;
                console.log(`${setting}: ${enabled}`);
                // Here you would typically save the setting
            });
        });
    }

    saveSettings() {
        this.showLoading();
        
        setTimeout(() => {
            this.hideLoading();
            this.showNotification('Settings saved successfully!', 'success');
        }, 1500);
    }

    // Utility Functions for Analytics
    generateTrendData(days) {
        const data = [];
        let baseValue = 75;
        
        for (let i = 0; i < days; i++) {
            baseValue += (Math.random() - 0.5) * 10;
            baseValue = Math.max(60, Math.min(95, baseValue));
            data.push(baseValue);
        }
        
        return data;
    }

    updateAnalyticsTimeframe(timeframe) {
        const days = timeframe === '7d' ? 7 : timeframe === '30d' ? 30 : timeframe === '90d' ? 90 : 365;
        
        if (this.charts.trendsChart) {
            this.charts.trendsChart.data.labels = this.generateTimeLabels(days);
            this.charts.trendsChart.data.datasets[0].data = this.generateTrendData(days);
            this.charts.trendsChart.update();
        }
        
        this.showNotification(`Analytics updated for ${timeframe}`, 'info');
    }

    showAddSpeciesModal() {
        this.showNotification('Add Species feature coming soon!', 'info');
    }

    generateSpeciesReport() {
        this.showLoading();
        
        setTimeout(() => {
            this.hideLoading();
            this.showNotification('Species report generated!', 'success');
        }, 2000);
    }

    viewSpeciesDetails(species) {
        this.showNotification(`Viewing details for ${species}`, 'info');
    }

    editSpecies(species) {
        this.showNotification(`Editing ${species} parameters`, 'info');
    }

    exportData() {
        const data = {
            timestamp: new Date().toISOString(),
            ph: 7.2,
            temperature: 26.5,
            turbidity: 180,
            waterLevel: 85
        };

        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `water-quality-data-${Date.now()}.json`;
        a.click();
        URL.revokeObjectURL(url);

        this.showNotification('Data exported successfully!', 'success');
    }

    refreshAllData() {
        // Refresh all charts
        Object.keys(this.charts).forEach(chartKey => {
            if (this.charts[chartKey] && chartKey.includes('Mini')) {
                this.charts[chartKey].data.datasets[0].data = this.generateMiniChartData();
                this.charts[chartKey].update();
            }
        });

        // Update status cards
        this.updateStatusCards();
        
        this.showNotification('Data refreshed!', 'info');
    }

    clearAllAlerts() {
        const alertsList = document.getElementById('alertsList');
        if (alertsList) {
            alertsList.innerHTML = '<div class="alert-item"><div class="alert-content"><div class="alert-title">No alerts</div><div class="alert-message">All systems operating normally</div></div></div>';
        }
        this.showNotification('All alerts cleared!', 'success');
    }

    showSpeciesDetails(species) {
        this.showNotification(`Showing details for ${species}`, 'info');
    }

    // Utility Functions
    generateMiniChartData() {
        return Array.from({length: 20}, () => Math.random() * 100);
    }

    generateChartData(points, min, max) {
        return Array.from({length: points}, () => min + Math.random() * (max - min));
    }

    generateTimeLabels(hours) {
        const labels = [];
        const now = new Date();
        for (let i = hours; i >= 0; i--) {
            const time = new Date(now.getTime() - i * 60 * 60 * 1000);
            labels.push(time.toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'}));
        }
        return labels;
    }

    updateChartsTheme() {
        const isDark = this.currentTheme === 'dark';
        const textColor = isDark ? '#cbd5e1' : '#64748b';
        const gridColor = isDark ? '#334155' : '#e2e8f0';

        Object.keys(this.charts).forEach(chartKey => {
            const chart = this.charts[chartKey];
            if (chart && chart.options.scales) {
                chart.options.scales.x.grid.color = gridColor;
                chart.options.scales.x.ticks.color = textColor;
                chart.options.scales.y.grid.color = gridColor;
                chart.options.scales.y.ticks.color = textColor;
                chart.options.plugins.legend.labels.color = textColor;
                chart.update();
            }
        });
    }

    updateChartTimeRange(range) {
        const hours = range === '1h' ? 1 : range === '6h' ? 6 : range === '24h' ? 24 : 168;
        const mainChart = this.charts.mainChart;
        
        if (mainChart) {
            mainChart.data.labels = this.generateTimeLabels(hours);
            mainChart.data.datasets.forEach(dataset => {
                dataset.data = this.generateChartData(hours + 1, 
                    dataset.label.includes('pH') ? 6.5 : dataset.label.includes('Temperature') ? 20 : 100,
                    dataset.label.includes('pH') ? 8.5 : dataset.label.includes('Temperature') ? 35 : 400
                );
            });
            mainChart.update();
        }
    }

    // Animation Functions
    animateSection(section) {
        section.style.opacity = '0';
        section.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            section.style.transition = 'all 0.5s ease';
            section.style.opacity = '1';
            section.style.transform = 'translateY(0)';
        }, 50);
    }

    animateValue(element, targetValue, suffix = '') {
        const startValue = parseFloat(element.textContent) || 0;
        const duration = 1000;
        const startTime = performance.now();

        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            const currentValue = startValue + (targetValue - startValue) * this.easeOutCubic(progress);
            element.textContent = currentValue.toFixed(1) + suffix;

            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };

        requestAnimationFrame(animate);
    }

    easeOutCubic(t) {
        return 1 - Math.pow(1 - t, 3);
    }

    setupAnimations() {
        // Intersection Observer for scroll animations
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }
            });
        });

        document.querySelectorAll('.status-card, .chart-container, .alerts-panel').forEach(el => {
            el.style.opacity = '0';
            el.style.transform = 'translateY(20px)';
            el.style.transition = 'all 0.6s ease';
            observer.observe(el);
        });
    }

    // Notification System
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'times-circle' : 'info-circle'}"></i>
            <span>${message}</span>
        `;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.classList.add('show');
        }, 100);

        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    // Loading States
    showLoading() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.classList.add('active');
        }
    }

    hideLoading() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.classList.remove('active');
        }
    }
}

// Initialize Dashboard
document.addEventListener('DOMContentLoaded', () => {
    new AquaMonitorDashboard();
});

// Add notification styles
const notificationStyles = `
.notification {
    position: fixed;
    top: 90px;
    right: 20px;
    background: var(--bg-primary);
    color: var(--text-primary);
    padding: 1rem 1.5rem;
    border-radius: 12px;
    box-shadow: var(--shadow-heavy);
    border: 1px solid var(--border-color);
    display: flex;
    align-items: center;
    gap: 0.75rem;
    transform: translateX(400px);
    transition: transform 0.3s ease;
    z-index: 10000;
    min-width: 300px;
}

.notification.show {
    transform: translateX(0);
}

.notification.success {
    border-left: 4px solid var(--success-color);
}

.notification.error {
    border-left: 4px solid var(--danger-color);
}

.notification.info {
    border-left: 4px solid var(--info-color);
}

.notification i {
    font-size: 1.2rem;
}

.notification.success i {
    color: var(--success-color);
}

.notification.error i {
    color: var(--danger-color);
}

.notification.info i {
    color: var(--info-color);
}
`;

// Inject notification styles
const styleSheet = document.createElement('style');
styleSheet.textContent = notificationStyles;
document.head.appendChild(styleSheet);
