

const toggle_korea_Stock = ()=>{
    getJson("/list").then(json=>{
        let list = document.getElementById("list")
        let tbody = list.getElementsByTagName("tbody")[0]
        tbody.innerHTML=""
        json.stocks.map(item=>{
            let tr = document.createElement("tr")
            tr.addEventListener("click",()=>{
                loadStock(item.itemCode)
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

const loadStock = (id)=>{
    loadStockOrder(id)
    loadStockCurrent(id)
    toggle_korea_Stock()
    document.getElementById("identify").value=id
    load_korea_Unit("day")
}
const loadStockCandle=(id,unit='day')=>{
    getJson("/api/"+unit+"/"+id).then(json=>{
        let result = json.priceInfos.map(item=>{
            let date = luxon.DateTime.fromISO(item.localDate,"")
            let data = {
                x: date.valueOf(),
                o: item.openPrice,
                h: item.highPrice,
                l: item.lowPrice,
                c: item.closePrice
            }
            return data
        })
        renderChart(result)
    })
}

const loadStockOrder=id=>{
    getJson("/ask/"+id).then(json=>{

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

const loadStockCurrent=id=>{
    getJson("/basic/"+id).then(json=>{
        renderInfo(json.stockName,id,Number(json.closePrice.replaceAll(",","")),Number(json.fluctuationsRatio)*0.01)
    })
}
