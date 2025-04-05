

const toggle_oversea_Stock = ()=>{
    getJson("/oversea_list").then(json=>{
        let list = document.getElementById("oversea_list")
        let tbody = list.getElementsByTagName("tbody")[0]
        tbody.innerHTML=""
        json.stocks.map(item=>{
            let tr = document.createElement("tr")
            tr.addEventListener("click",()=>{
                load_oversea_Stock(item.itemCode,item.exchange_code)
            })

            let td1 = document.createElement("td")
            td1.innerText=item.stockName
            let td2 = document.createElement("td")
            td2.innerText=item.closePrice
            td2.setAttribute("style","text-align:right;font-weight:bold;")
            let td3 = document.createElement("td")
            let td3style = "text-align:right;"
            let td3value = item.fluctuationsRatio+"%"
            if(Number(item.fluctuationsRatio)<0){
                td3style+="color:#0A6CFF;"
            }else if(Number(item.fluctuationsRatio)>0){
                td3style+="color:#FF5755;"
                td3value="+"+td3value
            }
            td3.innerText=td3value
            td3.setAttribute("style",td3style)

            tr.append(td1)
            tr.append(td2)
            tr.append(td3)

            tbody.append(tr)

        })
    })
}

const load_oversea_Stock = (id,exchange_code)=>{
    load_oversea_StockOrder(id)
    load_oversea_StockCurrent(id)
    toggle_oversea_Stock()
    document.getElementById("identify").value=id

    // 새로운 input 요소 생성
    const exchangeInput = document.createElement("exchange"); //HTML에 있는 요소이름이 들어와야함
    // 생성한 input 요소에 ID 설정
    exchangeInput.id = "select_exchange_code"; //이걸로 getElementById로 읽고, 같은값이 있으면 HTML에서 읽어들이는거임
    // exchange_code 값 설정
    exchangeInput.value = exchange_code;

    load_oversea_Unit("day",exchange_code)
}


const load_oversea_StockCandle = (id, unit, exchange_code) => {
    console.log(exchange_code,'111111222222222222222222')
    getJson("/oversea_api/" + unit + "/" + id + "/" + exchange_code).then(json => {
        // json.priceInfos를 콘솔에 출력
        console.log("결과:", json.response.data);

        let result = json.response.data.map(item => {
            let date = luxon.DateTime.fromISO(item.localDate);
            let data = {
                x: date.valueOf(),
                o: item.openPrice,
                h: item.highPrice,
                l: item.lowPrice,
                c: item.closePrice
            };
            return data;
        });
        renderChart(result);
    });
}

const load_oversea_StockOrder=id=>{
    getJson("/oversea_ask/"+id).then(json=>{
        let result=[]
        json.sellInfo.forEach((item,k)=>{
            result.push([item.count,item.price,""])
        })
        json.buyInfos.forEach((item,k)=>{
            result.push(["",item.price,item.count])
        })
        renderOrder(result)
    })
}

const load_oversea_StockCurrent=id=>{
    getJson("/oversea_basic/"+id).then(json=>{
        renderInfo(json.stockName,id,Number(json.closePrice.replaceAll(",","")),Number(json.fluctuationsRatio)*0.01)
    })
}