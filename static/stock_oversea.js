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



const load_oversea_StockCandle = (id, unit, exchange_code) => {
    const interval = unit; // 캔들 간격
    const slidervalue = document.getElementById('simulatorSlider'); // 슬라이더 요소 가져오기
    // id : 종목
    // 표시할 캔들 개수 (최신 n개)를 설정
    const numberOfCandlesToShow = parseInt(slidervalue.value, 10) || 50; // 기본값: 최신 50개
    console.log(numberOfCandlesToShow,id,unit,exchange_code, '캔들 개수 설정 완료');

    // 데이터 요청
    getJson2(`/oversea_api/${interval}/${id}/${exchange_code}`).then(json => {
        let rawData = json.response.data.sort((a, b) => new Date(a.localDate) - new Date(b.localDate)); // 데이터 정렬 (오름차순)

        // 최신 n개의 캔들만 선택
        const startIndex = Math.max(0, rawData.length - numberOfCandlesToShow);
        const latestResult = rawData.slice(startIndex);

        // 데이터를 차트 형식으로 변환
        const chartData = latestResult.map(item => ({
            x: new Date(item.localDate).getTime(), // localDate를 타임스탬프로 변환
            o: item.openPrice,                    // openPrice
            h: item.highPrice,                   // highPrice
            l: item.lowPrice,                    // lowPrice
            c: item.closePrice                   // closePrice
        }));

        console.log(chartData, '차트 데이터 변환 완료');
        renderChart(chartData); // 차트 렌더링 함수 호출
    }).catch(error => {
        console.error("데이터 요청 중 오류 발생:", error);
    });
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
        console.log("Debounced call: Loading chart...");
        load_oversea_StockCandle(currentId, currentUnit, currentExchangeCode);
    }, 300); // 사용자가 입력을 멈춘 후 300ms 뒤에 실행
}