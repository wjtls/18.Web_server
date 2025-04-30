

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
    const numberOfCandlesToShow = parseInt(slidervalue.value, 10) || 50;
    document.getElementById('identify').value = id; //id 값 업데이트 차트에서
    document.getElementById('exchange').value = exchange_code
    document.getElementById('chart-title').textContent = `종목 : ${id}` //차트 타이틀업뎃

    try {
        document.getElementById('identify').value = id;
        document.getElementById('exchange').value = exchange_code;
        document.getElementById('chart-title').textContent = `종목 : ${id}`;
        document.getElementById('chart-interval').textContent = unit;
    } catch (uiError) { console.error("UI 업데이트 중 오류:", uiError); }

    // --- 4. 과거 데이터 로드 API 호출 ---
    // ★★ 이 API 엔드포인트(/oversea_api/...)가 과거 데이터를 충분히 반환하는지 확인 ★★
    const historicalApiUrl = `/oversea_api/${unit}/${id}/${exchange_code}`; // 과거 데이터 API 주소

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

         // 차트 렌더링
         renderChart(currentChartData);
         updateCurrentPriceDisplay(currentChartData);
         updatePortfolioDisplay(); //포트폴리오 업데이트

         // --- 5. 실시간 데이터 폴링 시작, 대규모 사용자에서 안좋음---
         // 한투 api
         //const apiMarketCode = currentExchange;
         //startPolling(currentSymbol, apiMarketCode); // 폴링 시작

    })
};

const load_oversea_StockCandle2 = (id, unit, exchange_code) => {

    // --- 종목 변경 시 웹소켓 구독/해제 처리 ---
    if (currentSymbol && currentExchange && (currentSymbol !== id || currentExchange !== exchange_code)) {
        // 이전 종목 구독 해제
        unsubscribeRealtimePrice(currentSymbol, currentExchange);
    }
    // 현재 정보 업데이트
    currentSymbol = id;
    currentExchange = exchange_code;
    // ------------------------------------

    const interval = unit;
    const slidervalue = document.getElementById('simulatorSlider');
    const priceElement = document.getElementById('chart-price'); // 현재가 표시할 <b> 태그 찾기
    const numberOfCandlesToShow = parseInt(slidervalue.value, 10) || 50;
    document.getElementById('identify').value = id; //id 값 업데이트 차트에서
    document.getElementById('exchange').value = exchange_code
    document.getElementById('chart-title').textContent = `종목 : ${id}` //차트 타이틀업뎃

    getJson2(`/oversea_api/${interval}/${id}/${exchange_code}`).then(json => {
         // 1. API 응답에서 데이터 추출 및 기본 검사
         let rawData = json.response?.data; // API 응답 구조에 맞게 조정 필요
         if (!Array.isArray(rawData)) {
             console.error("API 응답 데이터(rawData)가 배열이 아닙니다.", json);
             rawData = []; // 빈 배열로 초기화하여 이후 코드 에러 방지
         } else {
             // 2. 데이터 정렬 (localDate 기준 오름차순)
             rawData.sort((a, b) => new Date(a.localDate) - new Date(b.localDate));
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

         // 차트 렌더링
         renderChart(currentChartData);

         if (priceElement) { // 해당 ID를 가진 HTML 요소가 있는지 확인
             if (currentChartData && currentChartData.length > 0) {
                 // chartData 배열의 가장 마지막 요소(가장 최신 캔들)의 종가(.c) 가져오기
                 const lastClosePrice = currentChartData[currentChartData.length - 1].c;

                 if (typeof lastClosePrice === 'number' && !isNaN(lastClosePrice)) {
                     // 숫자가 맞으면 화면에 표시 (소수점 자릿수는 필요에 따라 toFixed()로 조절)
                     priceElement.textContent = lastClosePrice.toFixed(4); // 예: TQQQ는 소수점 4자리까지 표시
                     // (선택 사항) 초기 가격 표시 시 CSS 클래스 초기화 (예: price-neutral)
                     // priceElement.className = 'price-neutral';
                 } else {
                      console.warn("차트 데이터의 마지막 종가 값이 유효하지 않습니다:", lastClosePrice);
                      priceElement.textContent = '--.--'; // 유효하지 않으면 대체 텍스트
                 }
             } else {
                 // API에서 과거 데이터를 못 받아왔거나 비어있는 경우
                 console.warn("차트 데이터가 비어있어 초기 가격을 표시할 수 없습니다.");
                 priceElement.textContent = '--.--'; // 데이터 없을 때 대체 텍스트
             }
         } else {
             console.error("#chart-price 요소를 HTML에서 찾을 수 없습니다."); // ID 오타 등 확인 필요
         }
         // --- ▲▲▲ 초기 현재가 표시 업데이트 로직 완료 ▲▲▲ ---

         //웹소켓 실시간 가격
         subscribeRealtimePrice(currentSymbol, currentExchange);

    }).catch(error => {
         console.error(`/${id}/${interval}/ 데이터 요청 중 오류:`, error); // 에러 로깅
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





