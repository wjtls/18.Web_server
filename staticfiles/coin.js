
const coinList = [
    "KRW-BTC",
    "KRW-ETH",
    "KRW-XRP",
    "KRW-QTUM",
    "KRW-STRAX",
    "KRW-STRK"
]
let coinNameList = {}
const loadCoinList = ()=>{
    return fetch("https://api.upbit.com/v1/market/all").then(res=>res.json()).then(json=>{
        json.forEach(item=>{
            coinNameList[item.market]=item.korean_name
        })
    })
}
const loadCoinCurrent = (id)=>{
    getJson("https://api.upbit.com/v1/ticker?markets="+id).then(json=>{
        const item = json[0]
        renderInfo(coinNameList[id],id,item.trade_price,item.signed_change_rate)
    })
}

const loadCoinOrder = (id)=>{

    getJson(`https://api.upbit.com/v1/orderbook?markets=${id}`)
        .then(json=>{
            let target = json[0].orderbook_units.splice(0,5)

            let result=[]
            target.forEach((item,k)=>{
                result[5+k]=["",item.bid_price.toLocaleString(),item.bid_size.toLocaleString()]
                result[4-k]=[item.ask_size.toLocaleString(),item.ask_price.toLocaleString(),""]
            })
            renderOrder(result)
        })
}
const loadCoinCandle = (id,unit = 'day')=>{
    getJson(`https://api.upbit.com/v1/candles/${unit}s?market=${id}&count=200`)
        .then(json=>{
            let result = json.map(item=>{
                let date = luxon.DateTime.fromMillis(item.timestamp)
                return {
                    x: date.valueOf(),
                    o: item.opening_price,
                    h: item.high_price,
                    l: item.low_price,
                    c: item.trade_price
                }
            })
            renderChart(result)
        })
}
const loadCoin = (id)=>{
    loadCoinCandle(id)
    loadCoinOrder(id)
    loadCoinCurrent(id)
    toggleCoin()
    document.getElementById("identify").value=id
    ("day")
}

const toggleCoin = ()=>{
    const marketCodes = encodeURI(coinList.join(","))
    getJson("https://api.upbit.com/v1/ticker?markets="+marketCodes)
        .then(json=>{
            let coin_list = document.getElementById("coin_list")
            let tbody = coin_list.getElementsByTagName("tbody")[0]
            tbody.innerHTML=""
            json.map(item=>{
                let tr = document.createElement("tr")
                tr.addEventListener("click",()=>{
                    loadCoin(item.market)
                })

                let td1 = document.createElement("td")
                td1.innerText=coinNameList[item.market]
                let td2 = document.createElement("td")
                td2.innerText=item.trade_price.toLocaleString()
                td2.setAttribute("style","text-align:right;font-weight:bold;")
                let td3 = document.createElement("td")
                let td3style = "text-align:right;"
                let td3value = Math.round(item.signed_change_rate*10000)/100+"%"
                if(item.signed_change_rate<0){
                    td3style+="color:#0A6CFF;"
                }else if(item.signed_change_rate>0){
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
