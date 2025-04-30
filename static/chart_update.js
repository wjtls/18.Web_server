


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
    loadUnit(currentInterval, sliderValue);


    // 주기적으로 포트폴리오 디스플레이도 업데이트하여 최신 차트 가격 변동을 반영
    if (typeof updatePortfolioDisplay === 'function') {
        updatePortfolioDisplay();
    }
}

//슬라이더할때 차트를 마지막 한번만 로딩
function debounce(func, wait) {
    let timeout; // 타이머 ID 저장 변수
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout); // 기존 타이머 취소 (실행 전에)
            func.apply(this, args); // 실제 함수 실행
        };
        clearTimeout(timeout); // 이전 타이머 취소 (새 이벤트 발생 시)
        timeout = setTimeout(later, wait); // 새 타이머 설정
    };
}




/**
 * 차트 업데이트를 위한 인터벌 타이머를 시작
 */
function startRealtimeChartUpdates() {
    stopRealtimeChartUpdates(); // 새 타이머 시작 전 기존 타이머 정리
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
    // 1. 모든 수신 메시지 로깅 (디버깅에 매우 중요)
    const receivedData = event.data;

    // 2. PING/PONG 처리 (KIS 문서 재확인 필요)
    if (receivedData === 'PING') {
        try { ws.send('PONG'); } catch(e){ console.error("PONG 전송 오류:", e); }
        return; // PING/PONG 메시지 처리 후 함수 종료
    }
    if (receivedData === 'PONG') {
        return; // PING/PONG 메시지 처리 후 함수 종료
    }

    // 3. 문자열 데이터 처리 시도
    if (typeof receivedData === 'string') {

        // 3-1. ^ 구분자 실시간 데이터 처리 ('0' 또는 '1'로 시작 가정)
        if (receivedData.includes('^') && (receivedData.startsWith('0|') || receivedData.startsWith('1|'))) {
            const fields = receivedData.split('^');

            // ★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★
            // ★★★ KIS 공식 문서에서 HDFSCNT0 '응답(Response)' 명세 확인 필수! ★★★
            // ★★★ 아래 fields 배열의 인덱스 번호는 *매우 부정확한 가정*입니다! ★★★
            // ★★★ 문서 보고 반드시! 실제 응답 필드 순서에 맞게 수정하세요! ★★★
            // ★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★
            const msgType = fields[0];        // 예: '0' (체결) <- 문서 확인!
            const tr_id = fields[1];          // 예: 'HDFSCNT0' <- 문서 확인!
            const receivedTrKey = fields[2];  // 예: 'DNASAAPL' <- tr_key가 여기 오는지 확인!
            const lastPriceStr = fields[7];   // 예: 현재가? <- ★★인덱스 확인 필수★★
            const execTime = fields[6];       // 예: 시간? <- ★★인덱스 확인 필수★★


            // 종목 코드 추출 (tr_key 형식에 따라 조정 필요)
            let symbolFromKey = receivedTrKey;
            if (receivedTrKey && receivedTrKey.length > 4 && (receivedTrKey.startsWith('D') || receivedTrKey.startsWith('R'))) {
                 symbolFromKey = receivedTrKey.substring(4); // 앞 4자리 제거 (예: DNAS + AAPL -> AAPL)
            } else if (receivedTrKey && receivedTrKey.length > 3 && (receivedTrKey.startsWith('D') || receivedTrKey.startsWith('R'))) {
                 // 혹시 시장코드가 3자리일 경우 대비 (HDFSCNT0 문서 확인 필요)
                 symbolFromKey = receivedTrKey.substring(4);
                 // 또는 symbolFromKey = receivedTrKey.substring(3); ?? -> 문서 확인!
            } else {
            }

            // 해외주식 실시간 현재가(HDFSCNT0)의 체결 데이터(msgType='0') 처리 (가정)
            if (tr_id === "HDFSCNT0" && msgType === '0') {
                if (symbolFromKey === currentSymbol) { // 현재 보고 있는 종목 데이터만 처리
                    const newPrice = parseFloat(lastPriceStr);
                    if (!isNaN(newPrice)) {
                        // --- ▼▼▼ 실시간 가격 저장소 업데이트 ▼▼▼ ---
                        currentPrices[symbolFromKey] = newPrice; // ★★★ 여기! ★★★
                        console.log(`   [Price Stored] currentPrices['${symbolFromKey}'] = ${newPrice}`);
                        // --- ▲▲▲ 업데이트 완료 ▲▲▲ ---

                        // 현재 차트에 표시 중인 종목이면 차트/화면 즉시 업데이트
                        if (symbolFromKey === currentSymbol) {
                            console.log(`   [Live Update] ${symbolFromKey} Price: ${newPrice}`);
                            // 차트 업데이트
                            if (chartInstance && typeof updateLastCandleOnChart === 'function' && currentChartData?.length > 0) {
                                const lastCandle = currentChartData[currentChartData.length - 1];
                                lastCandle.c = newPrice;
                                lastCandle.h = Math.max(lastCandle.h, newPrice);
                                lastCandle.l = Math.min(lastCandle.l, newPrice);
                                updateLastCandleOnChart(lastCandle);
                            }
                            // 화면 현재가 업데이트
                            if (typeof updatePriceDisplay === 'function') { updatePriceDisplay(newPrice); }
                            else { const pe = document.getElementById('chart-price'); if(pe) pe.textContent = newPrice.toFixed(4); }
                        }

                        // (실시간 데이터 올 때마다 호출 -> 성능 영향 고려 필요)
                        if (typeof updatePortfolioDisplay === 'function') {
                            updatePortfolioDisplay();
                        }

                    } else { console.warn(`   [Data] Invalid price string received: ${lastPriceStr}`); }
                } else { console.log(`   [Data] Received data for a different symbol: ${symbolFromKey}`); }
            } else { console.log(`   [Data] Received caret-separated data, but not HDFSCNT0 type 0.`); }

        } else if (receivedData.startsWith('{')) { // 3-2. JSON 형식 응답 처리
            console.log("   [Type] JSON-like string received.");
            try {
                const jsonData = JSON.parse(receivedData);
                console.log("   [JSON Parsed]:", jsonData);

                const rtCd = jsonData.body?.rt_cd;
                const msg1 = jsonData.body?.msg1 || "";
                const resTrId = jsonData.header?.tr_id;
                const resTrKey = jsonData.header?.tr_key;

                // 구독/해제 응답 처리 (HDFSCNT0 또는 H0STCNT0 등)
                if (resTrId === 'HDFSCNT0' || resTrId === 'H0STCNT0') { // 관련 TR ID 확인
                    if (rtCd === '0' || rtCd === '1') { // 성공 또는 준성공(이미 구독 등)
                         if (msg1.includes('ALREADY')) { // 이미 구독 중 메시지 포함 시
                         } else {
                         }
                         // 현재 구독된 정보와 일치하면 isSubscribed = true
                         if(resTrKey === `D${currentExchange}${currentSymbol}`) { // 현재 요청 키와 일치 확인
                            isSubscribed = true;
                         }
                    } else { // 실패 응답
                         console.error(`   [JSON Result] Subscription Failed: ${msg1} (msg_cd: ${jsonData.body?.msg_cd}, rt_cd: ${rtCd})`);
                         // 실패 시 구독 상태 false로 명확히
                         if(resTrKey === `D${currentExchange}${currentSymbol}`) {
                            isSubscribed = false;
                         }
                    }
                } else { /* 기타 TR_ID JSON 처리 */ }

            } catch (e) {
                console.error("   [JSON Error] Failed to parse received string as JSON:", e);
                console.warn("   Received string was:", receivedData);
            }
        } else { // 3-3. 기타 알 수 없는 문자열
            console.warn("   [Type] Unknown string format received.");
        }
    } else { // 4. 문자열 외 데이터 타입 (거의 없음)
        console.warn("[WebSocket] Received non-string data:", typeof receivedData, receivedData);
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

