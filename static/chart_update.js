


// --- Helper Functions ---
function formatCurrency(value, currency = '₩') {
    // Basic formatting, consider locale-specific for production
    return `${currency}${Math.round(value).toLocaleString('ko-KR')}`;
}

function formatPercent(value) {
    return `${value.toFixed(2)}%`;
}

function getSliderValue() {
     const slider = document.getElementById('simulatorSlider');
     return slider ? slider.value : '100'; // 기본값 반환
}

function getPriceClass(value) {
    if (value > 0) return 'price-up';
    if (value < 0) return 'price-down';
    return 'price-neutral';
}

function getCurrentTimestamp() {
     const now = new Date();
     return now.toLocaleString('ko-KR', { hour12: false }); // HH:MM:SS format
}
