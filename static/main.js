

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
                upchanged:"#999"
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


const toggle_oversea_exchange = () => {
    const exchangeSelect = document.getElementById("exchange");
    const selectedExchange = exchangeSelect.value;
    const overseaTable = document.getElementById("oversea_options"); //HTML에서 불러올때테이블 이름설정
    console.log('실행확인gsdgsdgsdg')
    if (selectedExchange) {
        // 선택된 거래소에 따라 해외 종목 테이블을 표시
        overseaTable.style.display = "table"; // 해외 종목 테이블 표시
        // 여기에 선택된 거래소에 따른 데이터 로딩 로직을 추가할 수 있습니다.
    } else {
        overseaTable.style.display = "none"; // 거래소가 선택되지 않으면 테이블 숨김
    }
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