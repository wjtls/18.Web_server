


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


function updateChartPeriodically() {
    const currentInterval = getCurrentChartInterval(); // 현재 활성화된 시간 간격
    const sliderValue = getSliderValue(); // 현재 슬라이더 값
    // const currentSymbol = document.getElementById('chart-title')?.textContent; // loadUnit 함수가 심볼을 필요로 할 경우 주석 해제

    // loadUnit 함수가 현재 제목(title)에 표시된 심볼의 데이터를 가져오고,
    // 제공된 interval과 sliderValue를 사용한다고 가정
    console.log(`[${getCurrentTimestamp()}] 차트 자동 업데이트: 간격=${currentInterval}, 범위=${sliderValue}`);
    if (typeof loadUnit === 'function') {
         // loadUnit 함수가 심볼을 명시적으로 요구하는지 확인하세요.
         // 만약 loadUnit(symbol, unit, range) 형식이라면 심볼을 전달
         // loadUnit(currentSymbol, currentInterval, sliderValue);
         // 만약 loadUnit(unit, range) 형식이고 내부적으로 심볼을 가져온다면 아래로 사용
         loadUnit(currentInterval, sliderValue);
    } else {
        console.error("주기적 업데이트를 위한 loadUnit 함수를 찾을 수 없습니다!");
        stopRealtimeChartUpdates(); // 함수가 없으면 업데이트 시도 중지
    }

    // 주기적으로 포트폴리오 디스플레이도 업데이트하여 최신 차트 가격 변동을 반영
    if (typeof updatePortfolioDisplay === 'function') {
        updatePortfolioDisplay();
    }
}

/**
 * 차트 업데이트를 위한 인터벌 타이머를 시작
 */
function startRealtimeChartUpdates() {
    stopRealtimeChartUpdates(); // 새 타이머 시작 전 기존 타이머 정리
    console.log(`실시간 차트 업데이트 시작 (${CHART_UPDATE_INTERVAL_MS / 1000}초 마다).`);
    chartUpdateInterval = setInterval(updateChartPeriodically, CHART_UPDATE_INTERVAL_MS);
}

/**
 * 차트 업데이트를 위한 인터벌 타이머를 중지
 */
function stopRealtimeChartUpdates() {
    if (chartUpdateInterval !== null) {
        clearInterval(chartUpdateInterval);
        chartUpdateInterval = null; // 타이머 ID 초기화
        console.log("실시간 차트 업데이트 중지.");
    }
}

/**
 * 버튼 클릭 시 차트 시간 간격을 변경하는 함수.
 * @param {string} newUnit - 새로운 시간 간격 (예: '1m', '5m', '1h').
 */
function switchInterval(newUnit) {
    console.log(`사용자 인터벌 변경: ${newUnit}`);

    // 1. 활성 버튼 클래스 업데이트
    document.querySelectorAll('.chart-footer .footer-group button.units').forEach(btn => {
        // 버튼의 onclick 속성에서 인터벌 추출하여 비교
        const btnIntervalMatch = btn.onclick.toString().match(/switchInterval\('([^']+)'/);
        if (btnIntervalMatch && btnIntervalMatch[1] === newUnit) {
            btn.classList.add('active'); // 클릭된 버튼에 active 클래스 추가
        } else {
            btn.classList.remove('active'); // 나머지 버튼에서 active 클래스 제거
        }
    });

    // 2. 화면에 표시되는 간격 텍스트 업데이트 (예: "5분봉")
    let intervalDisplay = newUnit;
    if (newUnit.includes('m')) intervalDisplay = newUnit.replace('m', '분봉');
    if (newUnit.includes('h')) intervalDisplay = newUnit.replace('h', '시간봉'); // 필요시 시간봉 처리 추가
    if (newUnit.includes('d')) intervalDisplay = newUnit.replace('d', '일봉');   // 필요시 일봉 처리 추가
    document.getElementById('chart-interval').textContent = intervalDisplay;

    // 3. 새로운 간격으로 loadUnit 즉시 호출
    const sliderValue = getSliderValue();
    if (typeof loadUnit === 'function') {
        console.log(`수동 유닛 로드: ${newUnit}, 범위: ${sliderValue}`);
         // 필요시 심볼 전달: loadUnit(symbol, newUnit, sliderValue);
        loadUnit(newUnit, sliderValue);
    } else {
         console.error("loadUnit 함수를 찾을 수 없습니다!");
    }

    // 4. 주기적 업데이트 타이머 시작/재시작
    // 타이머는 이제 새로운 간격을 사용
    startRealtimeChartUpdates();
}


/**
 * 현재 활성화된 인터벌 버튼을 찾아 인터벌 문자열(예: '1m', '5m')을 반환
 */
function getCurrentChartInterval() {
    // 'active' 클래스를 가진 버튼 탐색
    const activeButton = document.querySelector('.chart-footer .footer-group button.units.active');
    if (activeButton && activeButton.onclick) {
        // onclick 속성에서 인터벌 추출 (예: "switchInterval('5m')")
        const match = activeButton.onclick.toString().match(/switchInterval\('([^']+)'/);
        if (match && match[1]) {
            return match[1]; // '1m', '5m' 등 반환
        }
    }
    // 추출 실패 시, 화면에 표시된 텍스트 기반으로 추정 (대체 방안)
    const intervalText = document.getElementById('chart-interval')?.textContent || '5m'; // 기본 '5분봉'
    // '분봉' -> 'm', '시간봉' -> 'h', '일봉' -> 'd' 등으로 변환 시도
    return intervalText.replace('분봉','m').replace('시간봉','h').replace('일봉','d');
}