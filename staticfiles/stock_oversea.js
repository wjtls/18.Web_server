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
    load_oversea_Unit("5m")
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
    const intervals = {'1m': 1, '3m': 3, '5m': 5,'7m':7, '10m': 10, '11m': 11, '15m': 15, '60m': 60,  '360m': 360,'1d': 1440}; // 간격 정의
    const interval = unit;
    const slider = document.getElementById('simulatorSlider');
    const slidervalue = slider.value

    // 표시할 캔들 개수 (최신 n개)를 설정합니다.
    const numberOfCandlesToShow = slidervalue; // 원하는 개수로 변경하세요.

    getJson2("/oversea_api/" + unit + "/" + id + "/" + exchange_code).then(json => {
        let rawData = json.response.data.sort((a, b) => new Date(a.localDate) - new Date(b.localDate)); // 데이터 정렬
        const groupByInterval = (data, intervalMinutes) => {
            let groupedData = [];
            let group = [];
            let currentStartTime = null;

            data.forEach(item => {
                let date = luxon.DateTime.fromISO(item.localDate);
                if (!currentStartTime) {
                    currentStartTime = date.startOf('minute');
                }

                if (date.diff(currentStartTime, 'minutes').minutes < intervalMinutes) {
                    group.push(item); // 현재 그룹에 추가
                } else {
                    if (group.length > 0) {
                        groupedData.push(group); // 기존 그룹 저장
                    }
                    group = [item]; // 새로운 그룹 시작
                    currentStartTime = date.startOf('minute'); // 새로운 그룹 시작 시간 설정
                }
            });

            if (group.length > 0) {
                groupedData.push(group); // 마지막 그룹 저장
            }

            return groupedData;
        };

        const intervalMinutes = intervals[interval]; // 간격을 분 단위로 변환
        let groupedData = groupByInterval(rawData, intervalMinutes); // 데이터를 간격별로 그룹화

        let previousClosePrice = null; // 이전 closePrice를 저장할 변수

        let result = groupedData.map((group, index) => {
            const isFirstGroup = index === 0; // 첫 번째 그룹 여부 확인
            const processedGroup = processGroup(group, previousClosePrice, isFirstGroup);
            previousClosePrice = processedGroup.c; // 다음 그룹을 위해 종가 저장

            return processedGroup;
        });

        // 최신 n개의 캔들만 선택합니다.
        const startIndex = Math.max(0, result.length - numberOfCandlesToShow);
        const latestResult = result.slice(startIndex);

        renderChart(latestResult); // 차트 렌더링 함수 호출
    });
};


const load_oversea_StockCandle2 = (id, unit, exchange_code) => {
    getJson2("/oversea_api/" + unit + "/" + id + "/" + exchange_code).then(json => {
        let result = json.response.data
            .sort((a, b) => new Date(a.localDate) - new Date(b.localDate))
            .map((item, index, array) => {
                let date = luxon.DateTime.fromISO(item.localDate);
                let openPrice = item.openPrice; // 기존 openPrice 유지

                // 첫 번째 캔들이 아니고, 이전 캔들의 closePrice가 존재하면 이전 closePrice로 설정
                if (index > 0 && index < array.length - 1 && array[index - 1].closePrice !== undefined) {
                    console.log('결과 0:', index, array[index - 1].closePrice);
                    openPrice = array[index - 1].closePrice;
                }
                if (index == array.length - 1) {
                    item.closePrice = item.openPrice
                } //실시간 가격 업데이트 필요

                console.log("결과:", date.valueOf(), openPrice, item.closePrice);
                let data = {
                    x: date.valueOf(),
                    o: openPrice,
                    h: item.highPrice,
                    l: item.lowPrice,
                    c: item.closePrice
                };
                return data;
            });
        renderChart(result);
    });
}


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
