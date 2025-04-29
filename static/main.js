

var ctx = document.getElementById('chart').getElementsByTagName("canvas")[0].getContext('2d');

var chart = new Chart(ctx, {
    type: 'candlestick',
    data: {
        datasets: [{
            label: 'CHRT - Chart.js Corporation',
            data: []
        }]
    },
    options: {
        plugins: {
            legend: {
                display: false
            }
        },

        maintainAspectRatio: false,
    }
});



const renderChart = (info)=>{
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


const toggle = (e)=>{
    const isChecked = e.target.checked; // 체크박스의 상태를 가져옴
    const messageDiv = document.getElementById("message");

    const overseaTable = document.getElementById("oversea_list");
    const domesticTable = document.getElementById("list");

    if (isChecked) {
        toggle_korea_Stock()
        overseaTable.style.display = "none"; // 해외 종목 테이블 숨김
        domesticTable.style.display = "table"; // 국내 종목 테이블 표시
        overseaOptions.style.display = "block"; // 해외 거래소 드롭다운 표시
        messageDiv.textContent = "국내 종목이 선택되었습니다.";
    } else {
        toggle_oversea_Stock()
        overseaTable.style.display = "table"; // 해외 종목 테이블 표시
        domesticTable.style.display = "none"; // 국내 종목 테이블 숨김
        overseaOptions.style.display = "none"; // 해외 거래소 드롭다운 숨김
        messageDiv.textContent = "해외 종목이 선택되었습니다.";
    }
}




// 특정 API 경로에서 데이터를 가져와 #oversea_list 테이블을 채우는 함수
function populateOverseaStockTable(apiUrl) {
    console.log(`해외 종목 목록 로드 시작: ${apiUrl}`);
    // getJson2 함수를 사용하여 데이터를 가져옵니다.
    getJson2(apiUrl).then(json => {
        let list = document.getElementById("oversea_list");
        // list 엘리먼트와 tbody가 있는지 확인
        let tbody = list ? list.getElementsByTagName("tbody")[0] : null;

        if (!tbody) {
            console.error("Error: Could not find tbody for #oversea_list.");
            return; // tbody가 없으면 함수 종료
        }

        tbody.innerHTML = ""; // 기존 목록 비우기

        // 데이터가 없거나 stocks 배열이 비어있으면 메시지 표시
        if (!json || !json.stocks || json.stocks.length === 0) {
             const row = tbody.insertRow();
             const cell = row.insertCell(0);
             cell.textContent = '종목 데이터가 없습니다.';
             cell.colSpan = 3; // 3개 열에 걸쳐 표시
             cell.style.textAlign = 'center';
             return; // 데이터가 없으면 종료
        }

        // 받아온 데이터로 테이블 채우기
        json.stocks.map(item => {
            let tr = document.createElement("tr");
            // 행 클릭 시 load_oversea_Stock 함수 호출 (상세 정보 로드)
            tr.addEventListener("click", () => {
                console.log(`테이블 행 클릭됨: ${item.itemCode}`);
                 // load_oversea_Stock 함수가 정의되어 있는지 확인 후 호출
                if (typeof load_oversea_Stock === 'function') {
                    load_oversea_Stock(item.itemCode, item.exchange_code);
                } else {
                    console.warn("load_oversea_Stock function is not defined. Cannot load stock details.");
                    // load_oversea_Stock 함수가 없을 경우, 최소한 identify와 chart-title 업데이트
                     const identifyInput = document.getElementById('identify');
                     if (identifyInput) identifyInput.value = item.itemCode;
                     const chartTitle = document.getElementById('chart-title');
                     if (chartTitle) chartTitle.textContent = item.itemCode;
                }
            });

            // 종목명 셀
            let td1 = document.createElement("td");
            td1.innerText = item.stockName;

            // 현재가 셀
            let td2 = document.createElement("td");
            // 숫자인 경우 소수점 둘째 자리까지 표시, 아니면 '-' 표시
            td2.innerText = (typeof item.closePrice === 'number') ? item.closePrice.toFixed(2) : '-';
            td2.setAttribute("style", "text-align:right;font-weight:bold;");

            // 등락률 셀
            let td3 = document.createElement("td");
            let td3style = "text-align:right;";
            let fluctuationValue = (typeof item.fluctuationsRatio === 'number') ? item.fluctuationsRatio : null;
            let td3value = '-'; // 기본값

            if (fluctuationValue !== null) {
                if (fluctuationValue < 0) {
                    td3style += "color:#0A6CFF;"; // 파란색
                    td3value = fluctuationValue.toFixed(2) + "%";
                } else if (fluctuationValue > 0) {
                    td3style += "color:#FF5755;"; // 빨간색
                    td3value = "+" + fluctuationValue.toFixed(2) + "%";
                } else { // fluctuationValue === 0
                     td3value = "0.00%";
                }
            }

            td3.innerText = td3value;
            td3.setAttribute("style", td3style);

            // 행에 셀 추가
            tr.append(td1);
            tr.append(td2);
            tr.append(td3);

            // tbody에 행 추가
            tbody.append(tr);
        });
    })
    .catch(error => {
        console.error('해외 종목 데이터를 불러오는데 실패했습니다:', error);
        // 오류 발생 시 테이블 비우고 오류 메시지 표시
        const tbody = document.querySelector('#oversea_list tbody');
        if (tbody) {
            tbody.innerHTML = ''; // 기존 내용 비우기
            const row = tbody.insertRow();
            const cell = row.insertCell(0);
            cell.textContent = '데이터 로드 중 오류가 발생했습니다.';
            cell.colSpan = 3;
            cell.style.textAlign = 'center';
            cell.style.color = 'red';
        }
    });
}


// "해외" / "국내" 스위치 상태에 따라 UI를 토글하고 초기 종목 목록을 로드하는 함수
// HTML의 input[type="checkbox"] onlick에 연결됨: onclick="toggleExchangeView(this.checked)"
function toggleExchangeView(isDomestic) {
    console.log("Toggle Exchange View:", isDomestic ? "국내" : "해외");

    const overseaOptionsDiv = document.getElementById('oversea_options');
    const overseaListTable = document.getElementById('oversea_list'); // 목록 테이블 자체
     const overseaStockTableBody = overseaListTable ? overseaListTable.querySelector('tbody') : null;


    // TODO: 국내 주식 관련 엘리먼트들도 필요하다면 여기에 추가하세요.
    // 예: const domesticElementsContainer = document.getElementById('domestic_elements'); // 국내 UI 전체를 감싸는 div

    // 상태 전환 시 현재 표시된 테이블 내용을 일단 비웁니다.
     if (overseaStockTableBody) overseaStockTableBody.innerHTML = '';
    // TODO: 국내 테이블도 있다면 비워줍니다. (예: domesticStockTableBody.innerHTML = '';)


    if (isDomestic) {
        // '국내'가 선택된 경우 (체크박스 체크됨)
        // 해외 거래소 선택 부분과 해외 종목 목록 테이블을 숨깁니다.
        if (overseaOptionsDiv) overseaOptionsDiv.classList.add('hidden');
        if (overseaListTable) overseaListTable.classList.add('hidden'); // 목록 테이블 숨김

        // TODO: 국내 주식 관련 UI를 보여주는 코드를 여기에 추가합니다.
        // 예: if (domesticElementsContainer) domesticElementsContainer.classList.remove('hidden');
        // TODO: 국내 주식 목록을 불러오는 함수를 호출합니다. (예: loadDomesticStocks();)
        console.log("국내 주식 뷰 활성화. 국내 데이터 로드 기능은 구현 필요.");

    } else {
        // '해외'가 선택된 경우 (체크박스 해제됨)
        // 해외 거래소 선택 부분과 해외 종목 목록 테이블을 보여줍니다.
        if (overseaOptionsDiv) overseaOptionsDiv.classList.remove('hidden');
        if (overseaListTable) overseaListTable.classList.remove('hidden'); // 목록 테이블 보여줌


         // TODO: 국내 주식 관련 UI를 숨기는 코드를 여기에 추가합니다.
        // 예: if (domesticElementsContainer) domesticElementsContainer.classList.add('hidden');

        // 기본값 또는 현재 선택된 해외 거래소의 종목 목록을 불러옵니다.
        const exchangeSelect = document.getElementById('exchange');
        let initialApiUrl = '/api/oversea_stock_list/'; // 기본값: 전체 해외 주식 API 경로

        // HTML의 거래소 선택 select의 기본 선택 값에 따라 초기 로드할 API 경로를 결정
         if (exchangeSelect) {
             const selectedIndex = exchangeSelect.selectedIndex;
             const selectedOption = exchangeSelect.options[selectedIndex];
             // HTML에서 '전체'와 '나스닥' 옵션의 value가 둘 다 'NAS'인 경우를 텍스트로 구분
             if (selectedOption.value === 'NAS' && selectedOption.text === '나스닥') {
                  initialApiUrl = '/oversea_NASD_list/';
             } else if (selectedOption.value === 'NYS') {
                  initialApiUrl = '/oversea_NYSE_list/';
             } else if (selectedOption.value === 'AMS') {
                  initialApiUrl = '/oversea_AMEX_list/';
             }
              // value가 'NAS'이고 텍스트가 '전체'인 경우는 기본값('/api/oversea_stock_list/') 유지
         }

        // 종목 목록을 테이블에 채우는 함수 호출
        populateOverseaStockTable(initialApiUrl);
    }
}


const getJson=(url,option={})=>{
    return fetch(url,option).then(res=>res.json())
}

const toggleFull = ()=>{
    let container = document.getElementsByTagName("section")[0]
    let canvas = document.getElementsByTagName("canvas")[0]
    let children = container.children
    let styleOther = "";
    let styleMain = "";
    let styleCanvas = "";
    let containerStyle = "";
    if(children[0].style.display!=="none"){
        styleOther="display:none"
        styleCanvas="max-height: calc(100vh - 255px)"
        styleMain="flex:1"
        containerStyle="display:flex"
    }
    canvas.setAttribute("style",styleCanvas)
    container.setAttribute("style",containerStyle)
    for(let i=0; i<children.length;i++){
        if(i!==1){
            children[i].setAttribute("style",styleOther)
        }else{
            children[i].setAttribute("style",styleMain)
        }
    }
}


const renderOrder = info=>{

    let order = document.getElementById("order")
    let tbody = order.getElementsByTagName("tbody")[0]
    tbody.innerHTML=""

    info.forEach(item=>{
        let tr = document.createElement("tr")

        item.forEach((value)=>{
            let td = document.createElement("td")
            td.innerText=value
            let style = "text-align:center;"
            if(item[0]!==""){
                style+="color:#0A6CFF;"
            }else if(item[2]!==""){
                style+="color:#FF5755;"
            }
            td.setAttribute("style",style)
            tr.append(td)
        })
        tbody.append(tr)
    })
}





const getMA = (info,i)=>{
    return info.map((v,k)=>{
        let target = []
        const targetSize = i-1
        if(k>=targetSize){
            target = [...info].splice(k-targetSize,targetSize+1)
        }else{
            target = [...info].splice(0,k+1)
        }
        return {
            x:v.x,
            y:(target.map(v=>v.c).reduce((a,b)=>a+b))/target.length
        }
    })
}
const load_korea_Unit = (unit) => {
    let id = document.getElementById("identify").value;
    let messageDiv = document.getElementById("messageDiv"); // 메시지 표시할 요소 선택

    {
        loadStockCandle(id, unit); // 국내 주식 로드
        messageDiv.textContent = "국내 주식이 로드되었습니다.";
    }

    let units = document.getElementsByClassName("units");
    for (let i = 0; i < units.length; i++) {
        units[i].classList.remove("active");
        if ((unit === "day" && i === 0) || (unit === "week" && i === 1) || (unit === "month" && i === 2)) {
            units[i].classList.add("active");
        }
    }
}



const renderInfo = (label,desc,price,change)=>{
    let header = document.getElementById("chart").getElementsByTagName("div")[0]
    let h1 = header.getElementsByTagName("h1")[0]
    h1.innerText=label
    let small = header.getElementsByTagName("small")[0]
    small.innerText=desc
    let b = header.getElementsByTagName("b")[0]
    b.innerText=price.toLocaleString()+"원"
    let span = header.getElementsByTagName("span")[0]
    let style = "";
    if(change>0){
        style+="color:#FF5755;"
    }else if(change<0){
        style+="color:#0A6CFF;"
    }
    span.setAttribute("style",style)
    span.innerText=(change>0?"+":"")+Math.round(change*10000)/100+"%"
}

// === 필요한 유틸리티 함수 (외부 JS에 없을 경우) ===
function updateSliderValue(value) {
    const sliderValueElement = document.getElementById('sliderValue');
    if(sliderValueElement) sliderValueElement.textContent = value;
}
function updateQuantityValue(value) {
    const quantityValueElement = document.getElementById('quantity_value');
    if(quantityValueElement) quantityValueElement.textContent = value;
}
function getSliderValue() {
     const slider = document.getElementById('simulatorSlider');
     return slider ? slider.value : '100'; // 기본값 반환
}


function updateSliderValue(value) {
            const element = document.getElementById('sliderValue');
            if (element) element.textContent = value;
            // Potentially trigger chart load here if needed: loadUnit(currentUnit, value);
        }
function updateQuantityValue(value) {
    const element = document.getElementById('quantity_value');
    if (element) element.textContent = value;
}
// Submit function (As provided)
const submit = ()=>{
    let info = document.getElementById("message").value;
     if (!info.trim()) { alert("분석 요청 내용을 입력해주세요."); return; }
    let token = document.querySelector('[name=csrfmiddlewaretoken]')?.value; // CSRF 토큰 가져오기
    let form = new FormData();
    form.append("message", info);
    if (token) form.append("csrfmiddlewaretoken", token);

    console.log("Submitting AI request:", info);
    // 실제 fetch 로직은 외부 파일이나 다른 곳에 구현되어 있다고 가정
    fetch("/main",{ // 사용자의 기존 엔드포인트 유지
        method:"post",
        body:form
    })
    .then(response => { /* 응답 처리 */ console.log("AI Response received")})
    .catch(error => { console.error("Submit error:", error); });

    // alert(`AI 분석 요청 접수됨 (내용: ${info})`); // Using console log instead of alert
     document.getElementById("message").value = "";
};