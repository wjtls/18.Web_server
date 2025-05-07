

/*
const renderChart_tradingview = (chartData) => {
    console.log('[renderChart_tradingview 시작]');

    // --- 인터벌 값 변환 (TradingView 위젯 형식에 맞게) ---
    // 이 함수는 생성/업데이트 모두 필요하므로 먼저 수행
    let tvInterval;
    if (!currentInterval) { // currentInterval 전역 변수 사용
        console.error("[오류] currentInterval 값이 정의되지 않음! 기본값 '5m' 사용.");
        currentInterval = '5m';
        tvInterval = '5';
    } else if (typeof currentInterval === 'string') {
        // mapIntervalToTradingViewFormat 헬퍼 함수 사용 (이 함수는 별도 정의 필요, 이전 답변 참고)
        tvInterval = mapIntervalToTradingViewFormat(currentInterval);
    } else {
        console.error("[오류] currentInterval 값이 문자열이 아님:", currentInterval, "기본값 '5m' 사용.");
        currentInterval = '5m';
        tvInterval = '5';
    }
    console.log(`[인터벌 매핑] currentInterval: '${currentInterval}' -> tvInterval: '${tvInterval}'`);

    // --- 위젯 인스턴스 존재 여부 확인 ---
    if (window.tvWidgetInstance) {
        // <<<=== 위젯이 이미 존재하면 업데이트 로직 수행 ===>>>
        console.log('[업데이트] 기존 위젯 인스턴스 발견. 심볼/인터벌 업데이트 시도...');
        console.log(`[업데이트] 대상 심볼: ${currentSymbol}, 대상 인터벌(매핑됨): ${tvInterval}`); // 전역 변수 사용

        try {
            // ★★★ 위젯의 setSymbol 메소드 사용하여 업데이트 ★★★
            window.tvWidgetInstance.setSymbol(currentSymbol, tvInterval, () => {
                console.log(`[업데이트] 위젯 심볼/인터벌 변경 완료: 심볼=${currentSymbol}, 인터벌=${tvInterval}`);
                // 참고: setSymbol이 호출되면 위젯은 datafeed의 getBars를 다시 호출해서
                // 새 심볼/인터벌에 맞는 데이터를 *스스로* 가져감. 여기서 chartData를 다시 줄 필요 없음.
            });
        } catch(setError) {
            console.error("[업데이트][오류] 위젯 setSymbol 실행 중 오류:", setError);
             // setSymbol 실패 시 위젯을 강제로 재생성하는 로직 추가 고려 가능
             // console.log("[업데이트] setSymbol 오류로 위젯 재생성 시도...");
             // window.tvWidgetInstance.remove();
             // window.tvWidgetInstance = null;
             // // 여기서 생성 로직을 다시 호출하거나, 에러 처리 후 종료
             // // createNewWidget(chartData); // 아래 생성 로직을 별도 함수로 분리했다면 호출
        }

    } else {
        // <<<=== 위젯이 없으면 새로 생성하는 로직 수행 ===>>>
        console.log('[생성] 위젯 인스턴스 없음. 새로 생성 시작...');
        console.log('[생성] 초기 데이터 샘플:', chartData?.slice(0, 3)); // 초기 데이터 확인

        const chartContainerId = 'tvchart_container';
        const chartContainer = document.getElementById(chartContainerId);

        // --- 필수 요소 확인 ---
        if (!chartContainer) {
            console.error(`[생성][오류] 차트 컨테이너 #${chartContainerId}를 찾을 수 없음.`);
            return;
        }
        if (!Array.isArray(chartData) || chartData.length === 0) {
            console.warn("[생성][경고] 초기 차트 데이터가 유효하지 않아 생성 중단.");
            chartContainer.innerHTML = '차트 데이터 없음';
            return;
        }
        if (!currentSymbol || !currentExchange) {
             console.error(`[생성][오류] currentSymbol 또는 currentExchange 값이 유효하지 않음. Symbol: ${currentSymbol}, Exchange: ${currentExchange}`);
             return;
        }

        // --- 데이터 형식 변환 (초기 생성 시에만 필요) ---
        const tradingViewBars = chartData.map(item => ({
            time: item.x, open: item.o, high: item.h, low: item.l, close: item.c,
        }));
        console.log('[생성] 데이터 변환 완료. 샘플:', tradingViewBars.slice(0, 3));

        // --- 위젯 생성 전 필수 값 확인 로그 ---
        console.log('--- 위젯 생성 전 확인 ---');
        console.log('  - 컨테이너 요소:', chartContainer ? '찾음' : '못 찾음!!!');
        console.log('  - currentSymbol:', currentSymbol);
        console.log('  - currentExchange:', currentExchange);
        console.log('  - tvInterval (매핑됨):', tvInterval);
        console.log('  - TradingView 객체:', typeof TradingView === 'object' && TradingView !== null ? '유효함' : '문제 있음!!!');
        console.log('-----------------------');

        // --- 위젯 생성 ---
        try {
            console.log('[생성] TradingView.widget 생성 시도...');
            window.tvWidgetInstance = new TradingView.widget({
                container_id: chartContainerId,
                symbol: currentSymbol,      // 초기 심볼
                interval: tvInterval,       // 매핑된 초기 인터벌
                locale: 'ko',
                theme: 'dark',
                style: '1',
                autosize: true, // 크기 자동 조절

                // --- Datafeed 구현 (pricescale=10000 유지) ---
                datafeed: new class Datafeed { // Datafeed 구현은 동일
                    constructor(historicalBars) {
                        // constructor에서 초기 historicalBars를 받아두는 건 최초 로딩 시 유용할 수 있지만,
                        // getBars를 동적으로 바꿀 거면 여기서 this._bars를 저장하는 게 필수는 아니게 됨.
                        // 아니면 여기서 받은 초기 데이터를 캐시 등으로 활용할 수도 있고.
                        // 여기서는 getBars에서만 서버 통신하도록 수정할게.
                        console.log("[TradingView DataFeed] 생성자 호출됨.");
                        // this._bars = historicalBars; // 동적 로딩 시 이 라인은 필요 없을 수 있음
                    }
                    // ... resolveSymbol 메소드는 그대로 둬 ...

                    getBars(symbolInfo, resolution, periodParams, onHistoryCallback, onErrorCallback) {
                        console.log(`[TradingView DataFeed] === getBars 호출됨: ${symbolInfo.name}, 해상도: ${resolution} ===`);
                        console.log(`[TradingView DataFeed] 요청 기간: ${new Date(periodParams.from * 1000)} ~ ${new Date(periodParams.to * 1000)} (Unix: ${periodParams.from} ~ ${periodParams.to})`);

                        // --- TradingView 해상도 값을 네 백엔드 URL 형식에 맞게 변환 ---
                        // 'resolution' 값은 '5', '15', '60', 'D', 'W' 등 TradingView 형식이야.
                        // 네 URL '<str:minute>' 부분에 어떤 형식을 기대하는지 확인하고 매핑해야 해.
                        // 만약 URL이 '5', '15', '60'은 숫자로 받고 'D', 'W'는 문자로 받는다면 아래처럼
                        let backendInterval;
                        if (resolution === 'D') {
                            backendInterval = 'D';
                        } else if (resolution === 'W') {
                            backendInterval = 'W';
                        } else {
                            // 분/시간 단위는 숫자로 변환 (TradingView '60' -> 백엔드 '60')
                             backendInterval = resolution; // TradingView resolution이 이미 숫자 문자열이면 그대로 사용
                            // 만약 TradingView 240 -> 네 백엔드 4h 이런 식이라면 여기서 변환 로직 필요
                            // backendInterval = mapTradingViewResolutionToBackendFormat(resolution); // 이런 헬퍼 함수 필요
                        }
                        console.log(`[TradingView DataFeed] 매핑된 백엔드 인터벌: ${backendInterval}`);


                        // --- 백엔드 API 호출 ★★★ 네 Django URL 패턴에 맞게 조정 ★★★ ---
                        // 네 URL은 /oversea_api/<str:minute>/<str:symbol>/<str:exchange_code> 야.
                        // 그리고 TradingView getBars는 'from', 'to' 기간 파라미터를 주는데, 네 URL은 이게 없어! ★ 중요 ★
                        // 네 Django 백엔드 /oversea_api 뷰도 'from', 'to' 파라미터를 받아서
                        // 해당 기간의 데이터만 필터링해서 넘겨주도록 수정해야만 해.
                        // 그렇지 않으면 항상 전체 데이터를 가져오게 되고, 차트가 느려지거나 멈출 거야.
                        const symbol = symbolInfo.name;
                        const exchange = symbolInfo.exchange; // resolveSymbol에서 설정된 값 사용
                        // 'from', 'to' 파라미터를 URL에 추가하는 형식 (예: 쿼리 파라미터)
                        const apiUrl = `/oversea_api_from_to/${backendInterval}/${symbol}/${exchange}?from=${periodParams.from}&to=${periodParams.to}`;
                        console.log(`[TradingView DataFeed] API 호출 URL: ${apiUrl}`);

                        fetch(apiUrl)
                            .then(response => {
                                if (!response.ok) {
                                    throw new Error(`HTTP error! status: ${response.status}`);
                                }
                                return response.json();
                            })
                            .then(data => {
                                if (!data || data.length === 0) {
                                    console.warn("[TradingView DataFeed] getBars: 서버에서 데이터 없음.", data);
                                    // 데이터가 없을 때는 noData: true 로 콜백 호출
                                    onHistoryCallback([], { noData: true });
                                } else {
                                    // ★★★ 서버에서 받은 데이터 형식을 TradingView 형식으로 변환 ★★★
                                    // 네 Django 뷰에서 어떤 형식으로 데이터를 주는지에 따라 이 부분 코드가 달라짐.
                                    // 예를 들어 각 항목이 { 'timestamp': ..., 'open': ..., 'high': ..., 'low': ..., 'close': ..., 'volume': ... } 라면
                                    const bars = data.map(item => ({
                                         time: item.timestamp * 1000, // TradingView는 밀리초 단위 타임스탬프를 기대
                                         open: item.open,
                                         high: item.high,
                                         low: item.low,
                                         close: item.close,
                                         volume: item.volume || 0 // 볼륨 데이터가 있다면 추가, 없으면 0 또는 null
                                    }));
                                    console.log(`[TradingView DataFeed] getBars: 서버에서 ${bars.length}개 데이터 받음. 샘플:`, bars.slice(0, 3));
                                    onHistoryCallback(bars, { noData: false });
                                }
                            })
                            .catch(error => {
                                console.error("[TradingView DataFeed] getBars 데이터 가져오기 오류:", error);
                                onErrorCallback(`Error fetching data: ${error.message}`);
                            });
                    }
                    subscribeBars(symbolInfo, resolution, onRealtimeCallback, listenerGuid) {
                         console.log(`[TradingView DataFeed] === subscribeBars 호출됨: ${symbolInfo.name}, 해상도: ${resolution}, Guid: ${listenerGuid} ===`);

                        // 위젯이 넘겨준 onRealtimeCallback 함수를 listenerGuid와 함께 저장해 둠.
                        // 이 콜백을 나중에 네 실시간 데이터 수신부에서 호출할 거야.
                        this._subscribers[listenerGuid] = {
                            symbolInfo: symbolInfo,
                            resolution: resolution,
                            onRealtimeCallback: onRealtimeCallback, // ★★★ 이 함수를 저장! ★★★
                            // 필요한 경우 여기에 마지막 봉 데이터 정보 등 저장
                        };

                         // ★★★ 여기서 네 백엔드 실시간 데이터 스트림 구독을 실제로 시작하는 로직 호출 필요 ★★★
                         // 예시: 네 WebSocket 클라이언트 객체의 구독 메소드 호출
                         // connectRealtimeStream(symbolInfo.name, resolution, listenerGuid); // listenerGuid를 같이 넘겨주면 실시간 데이터 수신 시 구분하기 좋음
                         console.log(`[TradingView DataFeed] 실시간 데이터 구독 시작 요청: 심볼 ${symbolInfo.name}, 해상도 ${resolution}, GUID ${listenerGuid}`);
                    }

                    // 위젯이 실시간 데이터 구독 해지를 요청할 때 호출됨 (차트가 숨겨지거나 심볼 변경 시 등)
                    unsubscribeBars(listenerGuid) {
                         console.log(`[TradingView DataFeed] === unsubscribeBars 호출됨: ${listenerGuid} ===`);

                        // 저장해 둔 구독 정보 삭제
                        delete this._subscribers[listenerGuid];

                        // ★★★ 여기서 네 백엔드 실시간 데이터 스트림 구독을 실제로 해지하는 로직 호출 필요 ★★★
                        // 예시: 네 WebSocket 클라이언트 객체의 구독 해지 메소드 호출
                         // disconnectRealtimeStream(listenerGuid);
                         console.log(`[TradingView DataFeed] 실시간 데이터 구독 해지 요청: GUID ${listenerGuid}`);
                    }

                    // 필요하다면 TradingView resolution 값을 네 백엔드 형식으로 매핑하는 헬퍼 함수를 datafeed 안에 추가
                    // mapTradingViewResolutionToBackendFormat(resolution) { ... }
                }(),
                with_technical_indicators: true, // 기술적 지표 UI 표시 여부
                allow_symbol_change: false, // 위젯 내에서 심볼 변경 UI 허용 여부 (false 권장, 네 UI로 변경 유도)
                allow_resolution_change: true, // 위젯 내에서 해상도 변경 UI 허용 여부

            });
            console.log('[생성] TradingView.widget 생성 성공. 인스턴스:', window.tvWidgetInstance);

        } catch (widgetError) {
            console.error('[생성][오류] TradingView.widget 생성자에서 에러 발생 !!!', widgetError);
            if (chartContainer) { chartContainer.innerHTML = '<p style="color: red;">차트 생성 오류 발생.</p>'; }
        }
    } // end of else (위젯 새로 생성)

    console.log('[renderChart_tradingview 종료]');

}; // end of renderChart_tradingview


// ★★★ 인터벌 값 변환 헬퍼 함수 ★★★
function mapIntervalToTradingViewFormat(intervalString) {
    if (!intervalString || typeof intervalString !== 'string') return '5'; // 기본값

    if (intervalString.endsWith('m')) {
        return intervalString.replace('m', '');
    } else if (intervalString.endsWith('h')) {
        const hours = parseInt(intervalString.replace('h', ''), 10);
        // TradingView 표준 분봉 해상도에 맞추는 것이 좋음 (e.g., 60, 120, 180, 240)
        // 6시간(360) 같은 비표준은 지원 안될 수 있음. 여기서는 일단 계산값 반환.
        return (hours * 60).toString();
    } else if (intervalString.endsWith('d')) {
        return intervalString.replace('d', 'D');
    } else if (intervalString.endsWith('w')) {
        return intervalString.replace('w', 'W');
    }
    // 숫자 문자열 ('1', '5' 등) 이나 'D', 'W' 등은 그대로 반환
    return intervalString;
}

 */

const renderChart223 = (info)=>{
    const ma = getMA(info,5)
    chart.config.data.datasets = [
        {
            data: info,
            color:{
                up:"#FF5755",
                down:"#0A6CFF",
                upchanged:"#35cd55"
            }
        },
        {
            data:ma,
            type:"line"
        }
    ]
    chart.update()
}




const renderChart = (info)=>{
    chart.config.data.datasets = [
        {
            data: info,
            color:{
                up:"#FF5755",
                down:"#0A6CFF",
                upchanged:"#35cd55"
            }
        }
    ]
    chart.update()
}






// renderChart 함수 수정 (예시: 차트 인스턴스 생성 로직 포함)
const renderChart22 = (info) => {

    const canvas = document.getElementById('financialChart');
    if (!canvas) {
         console.error("오류: 'financialChart' 캔버스 요소를 찾을 수 없습니다.");
         console.log("--- renderChart 함수 종료 (캔버스 요소 오류) ---"); // 종료 로그
         return;
    }
    const ctx = canvas.getContext('2d');


    // ★★★ 수정된 파괴 로직: chartInstance 변수 대신 캔버스 자체를 확인하고, 결과가 유효할 때만 destroy 호출 ★★★
    const existingChart = Chart.getChart(canvas); // 캔버스에 연결된 Chart 인스턴스 가져오기 (없으면 undefined)

    // 캔버스에 기존 Chart 인스턴스가 발견되면 (existingChart가 undefined가 아니면) 파괴
    if (existingChart) { // ★ 여기에 null/undefined 체크가 포함된 거야! ★
         console.log(">>> 캔버스에 기존 Chart 인스턴스 발견. 파괴 시도:", existingChart); // 파괴 시도 로그
         try {
             existingChart.destroy(); // ★ existingChart가 null/undefined가 아닐 때만 이 코드가 실행됨 ★
             console.log(">>> 캔버스 기존 Chart 인스턴스 파괴 성공."); // 파괴 성공 로그
         } catch (e) {
             console.error(">>> 캔버스 기존 Chart 인스턴스 파괴 중 오류 발생:", e); // 파괴 오류 로그
             console.log("--- renderChart 함수 종료 (파괴 오류) ---"); // 종료 로그
             throw e; // 에러를 다시 throw
         }
         // 캔버스에 붙어있던 인스턴스를 파괴했으니, 우리가 관리하는 변수도 null로 설정 (상태 동기화)
         if (chartInstance === existingChart) { // 만약 chartInstance 변수가 파괴된 그 인스턴스였다면
             chartInstance = null;
         } else if (chartInstance !== null) {
         } else {
         }
    } else {
    }
    // ★★★ 수정된 파괴 로직 끝 ★★★


    // 새 Chart 인스턴스 생성 시작 (이제 캔버스가 비어있을 것으로 기대)
    console.log(">>> 새 Chart.js 인스턴스 생성 시작..."); // 생성 시작 로그
     try {
         // 새 인스턴스를 생성하고 chartInstance 변수에 할당
         chartInstance = new Chart(ctx, { // 변수 할당은 생성 성공 후
             type: 'candlestick', // 타입 확인
             data: { datasets: [] },
             options: {
                 responsive: true, maintainAspectRatio: false,
                 scales: {
                     x: { type: 'time', time: { unit: currentInterval.endsWith('m') ? 'minute' : 'day' } },
                     y: { /* ... 기존 y축 설정 ... */ }
                 },
                 plugins: {
                     buyAveragePriceLine: {}, // 평균가 라인 플러그인 활성화
                     tooltip: { /* ... */ },
                     legend: { display: false }
                 },
                 // ... 다른 옵션 ...
             }
         });
     } catch (e) {
         throw e; // 에러를 다시 throw
     }

    // Chart.js 플러그인 전역 등록 (DOMContentLoaded에서 이미 했다면 여기서 제거)
    // Chart.register(buyAveragePriceLinePlugin);


    // 데이터셋 업데이트
    const ma5 = typeof getMA === 'function' ? getMA(info, 5) : []; // getMA 함수 존재 확인
    const ma20 = typeof getMA === 'function' ? getMA(info, 20) : []; // getMA 함수 존재 확인

    chartInstance.config.data.datasets = [
        {
            label: 'Price', data: info, type: 'candlestick',
            color: { up: "#FF5755", down: "#0A6CFF", upchanged: "#35cd55" },
            borderColor: function(context) {
                 const dataPoint = context.dataset.data[context.dataIndex];
                 if (dataPoint) { return dataPoint.c > dataPoint.o ? '#FF5755' : '#0A6CFF'; }
                 return '#000';
             }
        },
        {
            label: 'MA(5)', data: ma5, type: 'line',
            borderColor: 'orange', borderWidth: 1, pointRadius: 0, fill: false
        },
         {
             label: 'MA(20)', data: ma20, type: 'line',
             borderColor: 'purple', borderWidth: 1, pointRadius: 0, fill: false
         }
    ];

    // 차트 업데이트
    chartInstance.update();
};




const load_oversea_StockCandle = (id, unit, exchange_code) => {

    // --- 1. 기존 폴링 중지 ---
    if (pollingIntervalId) { // pollingIntervalId로 변수명 통일
        clearInterval(pollingIntervalId);
        pollingIntervalId = null;
        console.log("기존 폴링 중지됨.");
    }

    // --- 2. 현재 정보 업데이트 ---
    currentSymbol = id;
    currentExchange = exchange_code;
    currentInterval = unit; // 인터벌 정보 업데이트

    // --- 3. UI 업데이트 ---
    const interval = unit;
    const slidervalue = document.getElementById('simulatorSlider');
    const priceElement = document.getElementById('chart-price'); // 현재가 표시할 <b> 태그 찾기
    const numberOfCandlesToShow = parseInt(slidervalue.value, 10) || 50;
    document.getElementById('identify').value = id; //id 값 업데이트 차트에서
    document.getElementById('exchange').value = exchange_code
    document.getElementById('chart-title').textContent = `종목 : ${id}` //차트 타이틀업뎃
    document.getElementById('chart-interval').textContent = unit;

    // --- 4. 과거 데이터 로드 API 호출 ---
    // ★★ 이 API 엔드포인트(/oversea_api/...)가 과거 데이터를 충분히 반환하는지 확인 ★★
    const historicalApiUrl = `/oversea_api/${unit}/${id}/${exchange_code}`; // 가격 API 주소

    getJson2(historicalApiUrl).then(json => {
         let rawData = json.response?.output2 || json.response?.data;
         if (!Array.isArray(rawData)) {
             console.error("과거 데이터(rawData)가 배열이 아닙니다.", json);
             rawData = [];
         } else {
             // 시간순 정렬 필수
             rawData.sort((a, b) => new Date(a.localDate || a.stck_cntg_hour).getTime() - new Date(b.localDate || b.stck_cntg_hour).getTime());
         }

        // 3. 표시할 캔들 개수(numberOfCandlesToShow)에 맞춰 최신 데이터 추출
         const startIndex = Math.max(0, rawData.length - numberOfCandlesToShow);
         // ★★★ 여기가 누락된 핵심 로직 ★★★
         const latestResult = rawData.slice(startIndex);
         // ★★★ 여기가 누락된 핵심 로직 ★★★

         // --- ★★★ 수정/복원 필요한 부분 끝 ★★★ ---
         // 4. 차트 데이터 형식으로 변환 (이제 latestResult 사용 가능)
         const chartData = latestResult.map(item => ({
             x: new Date(item.localDate).getTime(),
             o: item.openPrice,
             h: item.highPrice,
             l: item.lowPrice,
             c: item.closePrice
         }));
         currentChartData = chartData; // 전역 변수 업데이트

         // ★★★ 2. 현재가 표시 업데이트 ★★★
         const priceElement = document.getElementById('chart-price');
         if (priceElement && currentChartData.length > 0) {
             // 배열의 마지막 요소(가장 최신 캔들)의 종가(c)를 가져옴
             const lastCandleClosePrice = currentChartData[currentChartData.length - 1].c;
             if (typeof lastCandleClosePrice === 'number' && !isNaN(lastCandleClosePrice)) {
                 // textContent 속성을 사용하여 내용 업데이트
                 priceElement.textContent = lastCandleClosePrice.toFixed(4); // 예: 소수점 4자리
                 console.log(`#chart-price 업데이트 완료: ${lastCandleClosePrice.toFixed(4)}`);
             } else {
                 console.warn("마지막 캔들 종가 값이 유효하지 않습니다.");
                 priceElement.textContent = "--.--"; // 오류 시 대체 텍스트
             }
         } else if (!priceElement) {
             console.error("#chart-price 요소를 찾을 수 없습니다.");
         } else {
             console.warn("차트 데이터가 비어있어 현재가를 표시할 수 없습니다.");
             priceElement.textContent = "--.--";
         }

         // 초기 차트 렌더링
         renderChart(currentChartData);
         updateCurrentPriceDisplay(currentChartData);
         updatePortfolioDisplay();

         // --- 5. 실시간 데이터 폴링 시작 ---
         // ★★ exchangeCode를 API market 코드로 변환 필요 시 여기서 처리 ★★
         //const apiMarketCode = currentExchange;
         //startPolling(currentSymbol, apiMarketCode); // 폴링 시작

    }).catch(error => {
         console.error(`과거 데이터 (${historicalApiUrl}) 요청 중 오류:`, error);
         currentChartData = []; // 오류 시 데이터 비우기
         renderChart(currentChartData);
         if (priceElement) priceElement.textContent = '과거 데이터 로드 오류';
         // 오류 발생 시 폴링을 시작할지 결정 필요 (여기서는 시작하지 않음)
    });


    //매수 붉은선 위한 코드 추가
    getJson2(historicalApiUrl).then(json => {
        // ... (데이터 처리 코드) ...
        console.log("load_oversea_StockCandle: 과거 데이터 로드 및 처리 완료. renderChart 호출 전.");
        renderChart(currentChartData); // 여기서 renderChart 호출
        console.log("load_oversea_StockCandle: renderChart 호출 완료.");
        // ... (나머지 코드) ...
    }).catch(error => {
        console.error(`과거 데이터 (${historicalApiUrl}) 요청 중 오류 (catch 블록):`, error);
        currentChartData = [];
        console.log("load_oversea_StockCandle: 오류 발생. renderChart 호출 전.");
        renderChart(currentChartData); // 오류 시에도 renderChart 호출
        console.log("load_oversea_StockCandle: 오류 발생 후 renderChart 호출 완료.");
        // ... (나머지 오류 처리 코드) ...
    });
};




const renderInfo2 = (label, desc, price, change) => {
    let header = document.getElementById("chart").getElementsByTagName("div")[0]
    let h1 = header.getElementsByTagName("h1")[0]
    h1.innerText = label
    let small = header.getElementsByTagName("small")[0]
    small.innerText = desc
    let b = header.getElementsByTagName("b")[0]
    b.innerText = price.toLocaleString() + "원"
    let span = header.getElementsByTagName("span")[0]
    let style = "";
    if (change > 0) {
        style += "color:#FF5755;"
    } else if (change < 0) {
        style += "color:#0A6CFF;"
    }
    span.setAttribute("style", style)
    span.innerText = (change > 0 ? "+" : "") + Math.round(change * 10000) / 100 + "%"
}
const toggle_oversea_Stock = () => {
    getJson2("/oversea_list").then(json => {
        let list = document.getElementById("oversea_list")
        let tbody = list.getElementsByTagName("tbody")[0]
        tbody.innerHTML = ""
        json.stocks.map(item => {
            let tr = document.createElement("tr")
            tr.addEventListener("click", () => {
                load_oversea_Stock(item.itemCode, item.exchange_code)
            })

            let td1 = document.createElement("td")
            td1.innerText = item.stockName
            let td2 = document.createElement("td")
            td2.innerText = item.closePrice
            td2.setAttribute("style", "text-align:right;font-weight:bold;")
            let td3 = document.createElement("td")
            let td3style = "text-align:right;"
            let td3value = item.fluctuationsRatio + "%"
            if (Number(item.fluctuationsRatio) < 0) {
                td3style += "color:#0A6CFF;"
            } else if (Number(item.fluctuationsRatio) > 0) {
                td3style += "color:#FF5755;"
                td3value = "+" + td3value
            }
            td3.innerText = td3value
            td3.setAttribute("style", td3style)

            tr.append(td1)
            tr.append(td2)
            tr.append(td3)

            tbody.append(tr)

        })
    })
}

const load_oversea_Stock = (id, exchange_code) => {
    load_oversea_StockOrder(id)
    load_oversea_StockCurrent(id)
    toggle_oversea_Stock()
    document.getElementById("identify").value = id

    // 새로운 input 요소 생성
    const exchangeInput = document.createElement("exchange"); //HTML에 있는 요소이름이 들어와야함
    // 생성한 input 요소에 ID 설정
    exchangeInput.id = "select_exchange_code"; //이걸로 getElementById로 읽고, 같은값이 있으면 HTML에서 읽어들이는거임
    // exchange_code 값 설정
    exchangeInput.value = exchange_code;
    load_oversea_Unit('5m')
}

const processGroup = (group, previousClosePrice, isFirstGroup) => {
    // 첫 번째 그룹이면 previousClosePrice 대신 group[0].openPrice 사용
    const openPrice = !isFirstGroup && previousClosePrice !== null && previousClosePrice !== undefined
        ? previousClosePrice
        : group[0]?.openPrice || 0; // 안전한 접근 및 기본값 설정

    // 마지막 요소의 closePrice 가져오기 (첫 번째 그룹은 원래 데이터 사용)
    const closePrice = group.length > 0
        ? group[group.length - 1].closePrice
        : 0;

    return {
        x: luxon.DateTime.fromISO(group[0]?.localDate || new Date().toISOString()).valueOf(), // 첫 번째 데이터의 타임스탬프 사용
        o: openPrice,                                            // 이전 closePrice를 시가로 설정하거나 기본값 사용
        h: Math.max(...group.map(item => item.highPrice || 0)),  // 그룹 내 최고가 계산
        l: Math.min(...group.map(item => item.lowPrice || 0)),   // 그룹 내 최저가 계산
        c: closePrice                                            // 마지막 데이터의 종가 사용
    };
};
const load_oversea_StockOrder = id => {
    getJson2("/oversea_ask/" + id).then(json => {
        let result = []
        json.sellInfo.forEach((item, k) => {
            result.push([item.count, item.price, ""])
        })
        json.buyInfos.forEach((item, k) => {
            result.push(["", item.price, item.count])
        })
        renderOrder(result)
    })
}

const load_oversea_StockCurrent = id => {
    getJson2("/oversea_basic/" + id).then(json => {
        renderInfo2(json.stockName, id, Number(json.closePrice.replaceAll(",", "")), Number(json.fluctuationsRatio) * 0.01)
    })
}

const getJson2 = (url, option = {}) => {
    return fetch(url, option).then(res => res.json())
}


//초기 차트 뷰
const load_oversea_Unit = (unit) => {
    let id = document.getElementById("identify").value; //stock_oversea.ks에서 document에 넣었던 identify값을 가져온다
    let exchange_code = document.getElementById("exchange").value;
    let messageDiv = document.getElementById("messageDiv"); // 메시지 표시할 요소 선택
    {
        load_oversea_StockCandle(id, unit, exchange_code); // 해외 주식 로드
        messageDiv.textContent = "해외 주식이 로드되었습니다.";
    }

    let units = document.getElementsByClassName("units");
    for (let i = 0; i < units.length; i++) {
        units[i].classList.remove("active");
        if ((unit === "day" && i === 0) || (unit === "week" && i === 1) || (unit === "month" && i === 2)) {
            units[i].classList.add("active");
        }
    }
}


//인터벌 설정시 차트뷰
const loadUnit = (unit) => {
    let id = document.getElementById("identify").value
    let exchange_code = document.getElementById("exchange").value;
    const isStock = id.indexOf("-") === -1
    if (isStock) {
        load_oversea_StockCandle(id, unit, exchange_code)
    } else {
        loadStockCandle(id, unit, exchange_code)
    }
    let units = document.getElementsByClassName("units")
    for (let i = 0; i < units.length; i++) {
        units[i].classList.remove("active")
        if ((unit === "day" && i === 0) || (unit === "week" && i === 1) || (unit === "month" && i === 2)) {
            units[i].classList.add("active")
        }
    }
}


// 슬라이더 조작을 멈춘 후 일정 시간(예: 200~500ms)이 지나면 마지막 단 한 번만
function handleSliderChangeDebounced(currentId,currentUnit,currentExchangeCode) {
    clearTimeout(debounceTimer); // 이전 타이머 취소
    debounceTimer = setTimeout(() => {
        if (!currentId || !currentUnit || !currentExchangeCode) {
            console.error("Debounce: Missing parameters.");
            return;
        }
        load_oversea_StockCandle(currentId, currentUnit, currentExchangeCode);
    }, 300); // 사용자가 입력을 멈춘 후 300ms 뒤에 실행
}


























//한국투자증권 웹소켓
function connectWebSocket() {
    if (!approvalKey) {

        console.error("웹소켓 접속키(approvalKey)가 없습니다.");
        // 사용자에게 알림 또는 접속키 발급 로직 실행
        return;
    }
    if (ws && ws.readyState === WebSocket.OPEN) {
        console.log("웹소켓이 이미 연결되어 있습니다.");
        // 필요하다면 현재 심볼 재구독 로직 추가
        if (currentSymbol && !isSubscribed) {
             subscribeRealtimePrice(currentSymbol, currentExchange);
        }
        return;
    }

    // 웹소켓 주소 확인 (실전투자 기준, ws://)
    ws = new WebSocket("ws://ops.koreainvestment.com:21000");

    ws.onopen = () => {
        console.log("웹소켓 연결 성공");
        isSubscribed = false; // 연결 시 구독 상태 초기화
        // 연결 성공 후 현재 보고 있는 종목이 있다면 구독 시도
        if (currentSymbol && currentExchange) {
            subscribeRealtimePrice(currentSymbol, currentExchange);
        }
    };

    ws.onmessage = handleWebSocketMessage; // 메시지 처리 함수 연결

    ws.onerror = (error) => {
        console.error("웹소켓 오류:", error);
        isSubscribed = false;
    };

    ws.onclose = (event) => {
        console.log("웹소켓 연결 종료:", event.code, event.reason);
        isSubscribed = false;
        ws = null; // 웹소켓 객체 초기화
    };
}



// 한국투자증권 웹소켓 실시간 데이터 (마지막 1개)
function subscribeRealtimePrice(symbol, exchange) {
    if (!ws || ws.readyState !== WebSocket.OPEN) { console.warn("구독 시 웹소켓 미연결"); return; }
    if (!approvalKey) { console.error("[WebSocket] 구독 시점 approvalKey 없음!"); return; }
    if (!symbol || !exchange) { console.warn("구독 정보 부족 (symbol or exchange)"); return; }

    const tr_id = "HDFSCNT0"; // 해외주식 실시간 현재가 TR ID

    // ★★★ tr_key 형식: HDFSCNT0 문서 기준 'D'+시장코드+종목코드 ★★★
    // (이 형식이 맞는지 KIS 문서를 통해 다시 한번 확인하세요!)
    const tr_key = `D${exchange}${symbol}`; // 예: DNASAAPL 또는 DNASTQQQ


    const subscriptionMessage = {
        header: {
            "approval_key": approvalKey,
            "tr_type": "1", // 1: 등록
            "custtype": "P", // 개인고객
            "content-type": "utf-8"
        },
        body: {
            "input":{
            "tr_id": tr_id,
            "tr_key": tr_key
            }
        }
    };
    const jsonMessageToSend = JSON.stringify(subscriptionMessage);

    try {
        ws.send(jsonMessageToSend);
        // isSubscribed = true; // 성공 응답(JSON)을 받은 후 설정하는 것이 더 정확합니다.
    } catch (e) {
        console.error("웹소켓 send 오류:", e);
        isSubscribed = false; // 전송 실패 시 구독 상태 false
    }
}






// 한국투자증권 웹소켓 실시간 시세 구독 해제 함수 (필요 시)
function unsubscribeRealtimePrice(symbol, exchange) {
     if (!ws || ws.readyState !== WebSocket.OPEN || !isSubscribed) {
         console.warn("웹소켓이 연결되지 않았거나 구독 중이 아니어서 해제할 수 없습니다.");
         return;
     }
     const tr_key = `D${exchange}${symbol}`; // 해제할 키 (구독 시 사용한 것과 동일)
     console.log(`실시간 시세 구독 해제 요청: ${tr_key}`);
     const unsubscriptionMessage = {
         header: {
             "approval_key": approvalKey,
             "tr_type": "2", // 2: 해제
             "custtype": "P",
             "content-type": "utf-8"
         },
         body: {
             "tr_id": "HDFSCNT0",
             "tr_key": tr_key
         }
     };
     ws.send(JSON.stringify(unsubscriptionMessage));
     isSubscribed = false;
}





//한국투자증권 웹소켓
async function initializeWebSocket() {
    console.log("[WebSocket] 승인키 API 호출 시도...");
    // 기존 연결 종료 및 변수 초기화
    if (ws && ws.readyState !== WebSocket.CLOSED) {
        console.log("[WebSocket] 기존 웹소켓 연결 종료 시도.");
        ws.close(); ws = null;
    }
    approvalKey = null; isSubscribed = false;

    try {
        // Django 템플릿이 아닌 별도 JS 파일이므로, URL을 직접 문자열로 쓰거나
        // HTML 어딘가에 data 속성 등으로 URL을 저장해두고 읽어와야 합니다.
        // 여기서는 임시로 URL 문자열을 직접 사용합니다. (urls.py 경로와 일치해야 함)
        const apiKeyUrl = "/api/get_websocket_key/"; // ★ Django {% url %} 태그 대신 직접 경로 사용 ★
        console.log("[WebSocket] 승인키 요청 URL:", apiKeyUrl);

        // --- ↓↓↓ CSRF 헤더 제거! ↓↓↓ ---
        const response = await fetch(apiKeyUrl, {
            method: 'GET'
            // headers: { 'X-CSRFToken': csrfToken } // <-- 이 줄 삭제 또는 주석 처리!
        });
        // --- ↑↑↑ CSRF 헤더 제거 완료! ↑↑↑ ---

        if (!response.ok) { // HTTP 에러 처리
            let errorMsg = `승인키 API 서버 응답 오류: ${response.status} ${response.statusText}`;
            try { const errorData = await response.json(); errorMsg += ` - ${errorData.message || '내용 없음'}`; } catch(e) {}
            throw new Error(errorMsg);
        }
        const data = await response.json(); // 정상 응답 JSON 파싱

        if (data.success && data.approval_key) {
            approvalKey = data.approval_key; // 전역 변수에 키 저장
            console.log("[WebSocket] 승인키 성공적으로 받아옴 (키 일부):", approvalKey.substring(0, 10) + "...");

            // 'approvalKeyReady' 이벤트 발생 (stock_oversea.js 등 다른 스크립트 연동용)
            console.log("[WebSocket] approvalKeyReady 이벤트 발생시킴");
            const event = new CustomEvent('approvalKeyReady', { detail: { key: approvalKey } });
            document.dispatchEvent(event);

            connectWebSocket(); // 웹소켓 연결 시도
        } else {
            // API 응답은 왔으나 success:false 또는 키 없음
            throw new Error(data.message || "응답에 approval_key 없음");
        }
    } catch (error) {
        // fetch 자체 실패 또는 위에서 발생시킨 오류
        console.error("[WebSocket] 승인키 API 호출/처리 중 오류:", error);
        alert(`실시간 데이터 연결 키 요청 중 오류: ${error.message}`);
        // 키 발급 실패 시 웹소켓 연결 시도 안 함
    }
}































// 한국투자증권 api 실시간 데이터, 새 캔들 데이터를 기존 차트 데이터에 병합하는 함수
function mergeRealtimeCandle(newCandle) {
    if (!currentChartData || currentChartData.length === 0) {
        currentChartData = [newCandle]; // 데이터가 없으면 그냥 추가
        return;
    }

    const lastCandle = currentChartData[currentChartData.length - 1];

    if (newCandle.x === lastCandle.x) {
        // 시간이 같으면 마지막 캔들 업데이트 (시가는 유지, 고/저/종/거래량 업데이트)
        // console.log(`실시간: 캔들 업데이트 (시간: ${new Date(newCandle.x).toLocaleTimeString()})`);
        currentChartData[currentChartData.length - 1] = {
            ...lastCandle, // 기존 값 복사 (시가 등 유지)
            h: Math.max(lastCandle.h, newCandle.h), // 기존 고가와 새 고가 중 높은 값
            l: Math.min(lastCandle.l, newCandle.l), // 기존 저가와 새 저가 중 낮은 값
            c: newCandle.c,                         // 새 종가로 업데이트
            v: (lastCandle.v || 0) + (newCandle.v || 0) // 거래량은 누적? API가 누적값을 주는지 확인 필요. 여기서는 새 값으로 가정. 만약 API가 해당 '분'의 누적량을 준다면 newCandle.v 사용
            // v: newCandle.v // 만약 API가 해당 분의 '현재까지 누적 거래량'을 준다면 이렇게
        };
    } else if (newCandle.x > lastCandle.x) {
        // 시간이 더 최신이면 새 캔들 추가
        console.log(`실시간: 새 캔들 추가 (시간: ${new Date(newCandle.x).toLocaleTimeString()})`);
        currentChartData.push(newCandle);
        // (선택 사항) 차트 캔들 개수 제한 (예: 100개 유지)
        const MAX_CANDLES = 100; // 원하는 최대 캔들 수
        if (currentChartData.length > MAX_CANDLES) {
            currentChartData.shift(); // 가장 오래된 캔들 제거
        }
    } else {
        // 수신된 데이터가 마지막 캔들보다 과거 데이터인 경우 (네트워크 지연 등) - 무시
         console.warn("수신된 실시간 데이터가 마지막 캔들보다 과거 데이터입니다. 무시합니다.", {last: lastCandle.x, new: newCandle.x});
    }
}
function startPolling(symbol, market) {
    if (pollingIntervalId) { clearInterval(pollingIntervalId); }
    console.log(`폴링 시작: ${symbol} (${market}), 인터벌: ${currentInterval}, 폴링 간격: ${POLLING_INTERVAL_MS}ms`);

    // 주기적 폴링 설정 (첫 호출은 load_oversea_StockCandle 완료 후 시작됨)
    pollingIntervalId = setInterval(() => {
        fetchAndMergeLatestCandles(symbol, market); // ★★★ 이름 변경 및 로직 수정된 함수 호출 ★★★
    }, POLLING_INTERVAL_MS);

    // 선택적: 폴링 시작 직후 한번 호출하여 빠르게 업데이트 시도
    // fetchAndMergeLatestCandles(symbol, market);
}

// === 최신 N개 데이터 가져와서 병합하는 함수 (수정됨) ===
function fetchAndMergeLatestCandles(symbol, market) { // ★★★ 함수 이름 변경 및 로직 수정 ★★★
    const apiUrl = `/api/realtime_candle/${market}/${currentInterval}/${symbol}/`; // interval 포함
    // console.log("최신 N개 API 요청:", apiUrl);

    getJson2(apiUrl).then(response => {
        if (response.success && Array.isArray(response.data) && response.data.length > 0) {
            // 1. 받은 최신 N개 데이터를 Chart.js 형식으로 변환 및 시간순 정렬
            const latestNCandles = response.data.map(item => ({
                // ★★ 백엔드 응답 키 이름 확인 필수! ★★
                x: new Date(item.localDate).getTime(), // 'datetime' 이었는지 확인!
                o: parseFloat(item.openPrice),
                h: parseFloat(item.highPrice),
                l: parseFloat(item.lowPrice),
                c: parseFloat(item.closePrice),
                v: parseInt(item.volume, 10) || 0
            })).sort((a, b) => a.x - b.x); // 시간 오름차순 정렬

            // 2. 기존 데이터(currentChartData)와 최신 N개 데이터 병합
            mergeCandleArrays(latestNCandles); // ★★★ 병합 함수 호출 ★★★

            // 3. 차트 렌더링
            renderChart(currentChartData); // 병합된 데이터로 다시 그리기

            // 4. 현재가 업데이트
            updateCurrentPriceDisplay(currentChartData);

        } else {
            console.warn(`최신 N개 캔들 데이터 수신 실패 또는 빈 데이터: ${symbol}`, response.error || "데이터 없음");
        }
    }).catch(error => {
        console.error(`최신 N개 캔들 요청 중 오류 (${symbol}):`, error);
    });
}

// === 기존 데이터와 최신 N개 데이터를 병합하는 함수 (새로 추가 또는 수정) ===
function mergeCandleArrays(latestNCandles) {
    if (!latestNCandles || latestNCandles.length === 0) {
        console.log("병합할 최신 데이터가 없습니다.");
        return; // 병합할 데이터 없으면 종료
    }

    if (!currentChartData || currentChartData.length === 0) {
        console.log("기존 데이터가 없어 최신 데이터로 초기화합니다.");
        currentChartData = latestNCandles; // 기존 데이터 없으면 최신 데이터로 대체
        return;
    }

    // 최신 N개 데이터 중 가장 빠른 시간 찾기
    const firstNewTime = latestNCandles[0].x;

    // 기존 데이터에서 최신 데이터 시작 시간보다 이전 데이터만 필터링
    const historicalPart = currentChartData.filter(candle => candle.x < firstNewTime);

    // 필터링된 과거 데이터와 최신 N개 데이터를 합치기
    // 이렇게 하면 중복 시간대는 최신 N개 데이터로 대체됨
    const mergedData = historicalPart.concat(latestNCandles);

    // (선택 사항) 전체 캔들 개수 제한 (예: 최근 500개만 유지)
    const MAX_TOTAL_CANDLES = 500; // 원하는 최대 총 캔들 수
    if (mergedData.length > MAX_TOTAL_CANDLES) {
        currentChartData = mergedData.slice(-MAX_TOTAL_CANDLES); // 뒤에서부터 잘라 최신 유지
    } else {
        currentChartData = mergedData;
    }
    // console.log(`데이터 병합 완료. 총 ${currentChartData.length}개 캔들.`);
}




// === 현재가 표시 업데이트 함수 (이전과 동일) ===
function updateCurrentPriceDisplay(chartDataArray) {
    const priceElement = document.getElementById('chart-price');
    if (!priceElement) return;
    if (chartDataArray && chartDataArray.length > 0) {
        const lastClosePrice = chartDataArray[chartDataArray.length - 1].c;
        if (typeof lastClosePrice === 'number' && !isNaN(lastClosePrice)) {
            const previousPriceText = priceElement.textContent;
            priceElement.textContent = lastClosePrice.toFixed(4);
            const previousPrice = parseFloat(previousPriceText);
            if (!isNaN(previousPrice)) {
                 if (lastClosePrice > previousPrice) priceElement.className = 'price-up';
                 else if (lastClosePrice < previousPrice) priceElement.className = 'price-down';
            }
        } else { priceElement.textContent = '--.--'; }
    } else { priceElement.textContent = '--.--'; }
}





