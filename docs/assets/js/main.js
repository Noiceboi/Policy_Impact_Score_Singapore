// Singapore Policy Impact Assessment - Main JavaScript

// Global data storage
let policyData = null;
let assessmentData = null;
let internationalData = null;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// Main initialization function
function initializeApp() {
    // Add smooth scrolling
    addSmoothScrolling();
    
    // Initialize navigation
    initializeNavigation();
    
    // Add animation on scroll
    addScrollAnimations();
    
    // Load data if available
    loadPolicyData();
    
    // Initialize interactive elements
    initializeInteractiveElements();
}

// Navigation functionality
function initializeNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // Remove active class from all links
            navLinks.forEach(l => l.classList.remove('active'));
            
            // Add active class to clicked link
            this.classList.add('active');
            
            // Handle internal page navigation
            const href = this.getAttribute('href');
            if (href.startsWith('#')) {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth' });
                }
            }
        });
    });
}

// Smooth scrolling for anchor links
function addSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Scroll animations
function addScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
            }
        });
    }, observerOptions);
    
    // Observe all sections and cards
    document.querySelectorAll('.section, .card').forEach(el => {
        observer.observe(el);
    });
}

// Load and process policy data
function loadPolicyData() {
    // This would typically load from JSON files or API
    // For now, we'll use embedded data structures
    
    policyData = {
        totalPolicies: 16,
        verifiedPolicies: 13,
        verificationRate: 81.2,
        transparencyScore: 87.6,
        scientificConfidence: 88
    };
    
    // Update metrics on page
    updateMetrics();
}

// Update metrics display
function updateMetrics() {
    if (!policyData) return;
    
    // Update policy metrics
    updateElement('total-policies', policyData.totalPolicies);
    updateElement('verified-policies', policyData.verifiedPolicies);
    updateElement('verification-rate', policyData.verificationRate + '%');
    updateElement('transparency-score', policyData.transparencyScore + '/100');
    updateElement('confidence-level', policyData.scientificConfidence + '%');
    
    // Update progress bars
    updateProgressBar('verification-progress', policyData.verificationRate);
    updateProgressBar('transparency-progress', policyData.transparencyScore);
    updateProgressBar('confidence-progress', policyData.scientificConfidence);
}

// Helper function to update element content
function updateElement(id, value) {
    const element = document.getElementById(id);
    if (element) {
        element.textContent = value;
    }
}

// Helper function to update progress bars
function updateProgressBar(id, percentage) {
    const progressBar = document.getElementById(id);
    if (progressBar) {
        progressBar.style.width = percentage + '%';
        
        // Add appropriate class based on percentage
        if (percentage >= 85) {
            progressBar.className = 'progress-bar excellent';
        } else if (percentage >= 70) {
            progressBar.className = 'progress-bar good';
        } else if (percentage >= 55) {
            progressBar.className = 'progress-bar moderate';
        } else {
            progressBar.className = 'progress-bar low';
        }
    }
}

// Initialize interactive elements
function initializeInteractiveElements() {
    // Policy cards hover effects
    document.querySelectorAll('.policy-card').forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
    
    // Expandable sections
    document.querySelectorAll('.expandable').forEach(section => {
        const header = section.querySelector('.expandable-header');
        const content = section.querySelector('.expandable-content');
        
        if (header && content) {
            header.addEventListener('click', function() {
                const isExpanded = content.style.display !== 'none';
                content.style.display = isExpanded ? 'none' : 'block';
                header.classList.toggle('expanded');
            });
        }
    });
    
    // Filter functionality
    initializeFilters();
}

// Filter functionality for policy lists
function initializeFilters() {
    const filterButtons = document.querySelectorAll('.filter-btn');
    const policyItems = document.querySelectorAll('.policy-item');
    
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            const filter = this.getAttribute('data-filter');
            
            // Update active button
            filterButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            // Filter items
            policyItems.forEach(item => {
                const category = item.getAttribute('data-category');
                if (filter === 'all' || category === filter) {
                    item.style.display = 'block';
                    item.classList.add('fade-in');
                } else {
                    item.style.display = 'none';
                }
            });
        });
    });
}

// Create charts using Chart.js (if available)
function createCharts() {
    if (typeof Chart === 'undefined') return;
    
    // Policy verification chart
    createVerificationChart();
    
    // International validation chart
    createInternationalChart();
    
    // Timeline chart
    createTimelineChart();
}

function createVerificationChart() {
    const ctx = document.getElementById('verificationChart');
    if (!ctx) return;
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Verified', 'Estimated', 'Requires Clarification'],
            datasets: [{
                data: [13, 1, 2],
                backgroundColor: [
                    'rgba(56, 161, 105, 0.8)',
                    'rgba(221, 107, 32, 0.8)',
                    'rgba(229, 62, 62, 0.8)'
                ],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom'
                },
                title: {
                    display: true,
                    text: 'Policy Verification Status'
                }
            }
        }
    });
}

function createInternationalChart() {
    const ctx = document.getElementById('internationalChart');
    if (!ctx) return;
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['OECD', 'World Bank', 'IMF', 'UN', 'WEF', 'Transparency Intl', 'Heritage Found.', 'EIU'],
            datasets: [{
                label: 'Credibility Score',
                data: [95, 94, 93, 92, 88, 87, 82, 89],
                backgroundColor: 'rgba(49, 130, 206, 0.8)',
                borderColor: 'rgba(49, 130, 206, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'International Sources Credibility Scores'
                }
            }
        }
    });
}

function createTimelineChart() {
    const ctx = document.getElementById('timelineChart');
    if (!ctx) return;
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['1955', '1960', '1967', '1984', '1994', '2001', '2007', '2014', '2015'],
            datasets: [{
                label: 'Cumulative Policies',
                data: [1, 2, 3, 4, 5, 6, 7, 8, 9],
                borderColor: 'rgba(44, 82, 130, 1)',
                backgroundColor: 'rgba(44, 82, 130, 0.1)',
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Policy Implementation Timeline'
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Utility functions
function formatNumber(num) {
    return new Intl.NumberFormat().format(num);
}

function formatPercentage(num) {
    return num.toFixed(1) + '%';
}

function formatScore(num) {
    return num.toFixed(1) + '/100';
}

// Export functions for use in other scripts
window.PolicyApp = {
    updateMetrics,
    createCharts,
    formatNumber,
    formatPercentage,
    formatScore
};

// Load charts when page is ready
window.addEventListener('load', function() {
    setTimeout(createCharts, 500); // Delay to ensure DOM is fully rendered
});
