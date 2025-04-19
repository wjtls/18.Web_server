


// --- Helper Functions ---
function formatCurrency(value, currency = '$') {
    return `${currency}${Math.round(value).toLocaleString('ko-KR')}`;
}

function formatPercent(value) {
    return `${value.toFixed(2)}%`;
}

function getSliderValue() {
     const slider = document.getElementById('simulatorSlider');
     return slider ? slider.value : '100'; // 기본값 반환
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
    loadUnit(currentInterval, sliderValue);


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

function formatCurrency_(value, currency = '$') {
    return `${currency}${Math.round(value).toLocaleString('ko-KR')}`;
}

function getPriceClass(value) {
    if (value > 0) return 'price-up';
    if (value < 0) return 'price-down';
    return 'price-neutral';
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







// 초기 차트 로드 및 폴링 시작 함수
function loadAndStartPolling() {
    // 초기 차트 로드
    if (typeof load_oversea_StockCandle === 'function') {
        load_oversea_StockCandle(currentSymbol, currentInterval, currentExchange);
    } else {
        console.error("load_oversea_StockCandle 함수 없음");
    }

    // 기존 폴링 인터벌 제거 후 새로 설정
    if (pollingIntervalId) clearInterval(pollingIntervalId);
    pollingIntervalId = setInterval(() => {
        if (typeof load_oversea_StockCandle === 'function') {
            // 현재 설정된 인터벌로 계속 폴링
            load_oversea_StockCandle(currentSymbol, currentInterval, currentExchange);
        }
    }, POLLING_INTERVAL_MS);
    console.log(`폴링 시작: ${POLLING_INTERVAL_MS}ms 간격`);
}







//웹소켓 메세지 처리
function handleWebSocketMessage(event) {
    // console.log("Raw WS Data:", event.data); // 원시 데이터 확인용

    // PONG 메시지 처리 (API가 PING/PONG 요구 시 필요)
    if (event.data === 'PONG') {
        console.log('PONG received');
        // 필요한 PONG 처리 로직
        return;
    }
    // PING 메시지 처리
    if (event.data === 'PING') {
        console.log('PING received, sending PONG');
        ws.send('PONG');
        return;
    }

    // 실제 데이터 처리 (데이터 형식 확인 필요 - JSON 응답 또는 ^ 구분 문자열)
    // KIS API는 보통 ^ 구분 문자열 또는 JSON 형식의 응답(오류 등)을 보냄
    if (typeof event.data === 'string' && event.data.includes('^')) {
        // ^ 구분자 데이터 처리
        const fields = event.data.split('^');
        // console.log("Parsed Fields:", fields); // 필드 확인용

        // ----- ★★★ 필드 인덱스 확인 필수 ★★★ -----
        // 문서의 Response Body 순서대로 인덱스를 정확히 확인해야 합니다.
        // 아래는 *가정*입니다. (실제와 다를 수 있음!)
        const msgType = fields[0]; // 0: 실시간 체결, 1: 실시간 호가 등 (문서 확인 필요)
        const receivedSymbol = fields[1]; // SYMB (종목코드)
        const lastPriceStr = fields[7];   // LAST (현재가)
        const koreaTimeStr = fields[6];   // KHMS (한국시간)
        // -------------------------------------------

        // 수신 데이터가 현재 보고 있는 종목과 일치하고, 차트 데이터가 있을 때
        if (msgType === '0' && receivedSymbol === currentSymbol && chartInstance && currentChartData.length > 0) {
            const newPrice = parseFloat(lastPriceStr);
            if (isNaN(newPrice)) {
                console.warn("수신된 가격 데이터가 유효하지 않음:", lastPriceStr);
                return;
            }

            const lastCandle = currentChartData[currentChartData.length - 1];

            // 마지막 캔들 업데이트
            lastCandle.c = newPrice; // 종가
            lastCandle.h = Math.max(lastCandle.h, newPrice); // 고가
            lastCandle.l = Math.min(lastCandle.l, newPrice); // 저가

            // 차트 라이브러리 업데이트 함수 호출
            updateLastCandleOnChart(lastCandle);

            // (선택) 현재가 표시 업데이트
            const priceElement = document.getElementById('chart-price');
            if (priceElement) priceElement.textContent = newPrice.toFixed(2); // 소수점 처리 필요

        } else if (msgType === '0') {
             // console.log(`다른 종목(${receivedSymbol}) 데이터 수신 or 차트 준비 안됨`);
        } else {
             //console.log("체결 데이터(type 0)가 아닌 메시지 수신:", msgType);
        }

    }
    else if (typeof event.data === 'string') {
        // JSON 형태의 응답 처리 (예: 구독 성공/실패 메시지)
        try {
            const jsonData = JSON.parse(event.data);
            console.log("JSON 응답 수신:", jsonData);
            if (jsonData.header?.tr_id === 'HDFSCNT0' && jsonData.body?.rt_cd === '0') {
                 console.log(`구독 성공: ${jsonData.header.tr_key}`);
                 isSubscribed = true; // 구독 성공 시 상태 변경
            } else if (jsonData.body?.rt_cd !== '0') {
                 console.error(`구독/해제 실패: ${jsonData.body?.msg1}`);
                 isSubscribed = false;
            }
        } catch(e) {
            // console.warn("JSON 파싱 불가 메시지 수신:", event.data);
        }
    }
}

// 차트 라이브러리의 마지막 캔들 업데이트 함수 (라이브러리에 맞게 구현)
function updateLastCandleOnChart(lastCandleData) {
    // 예: TradingView Lightweight Charts
    // if (chartInstance && chartInstance.candlestickSeries?.update) {
    //     chartInstance.candlestickSeries.update(lastCandleData);
    // }
    // 예: Chart.js (캔들스틱 플러그인 사용 시)
    if (chartInstance && chartInstance.data?.datasets?.[0]?.data) {
        const lastIndex = chartInstance.data.datasets[0].data.length - 1;
        if (lastIndex >= 0) {
            // Chart.js는 보통 {x, o, h, l, c} 객체로 데이터를 다룸
            chartInstance.data.datasets[0].data[lastIndex] = lastCandleData;
            chartInstance.update('none'); // 'none'은 애니메이션 없이 즉시 업데이트
        }
    } else {
        // console.warn("차트 인스턴스 또는 데이터셋이 준비되지 않아 업데이트 불가");
    }
}