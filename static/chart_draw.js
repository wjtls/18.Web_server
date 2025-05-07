// buyAveragePriceLinePlugin: 현재 종목의 매수 평균가를 차트에 그리는 Chart.js 플러그인
const buyAveragePriceLinePlugin = {
    id: 'buyAveragePriceLine', // 플러그인 ID
    afterDraw(chart, args, options) {
        const {ctx, chartArea: {left, right, top, bottom}, scales: {x, y}} = chart;

        // 현재 심볼과 포트폴리오 정보 가져오기
        const currentSymbol = document.getElementById('identify')?.value; // 현재 차트의 심볼 ID
        const holding = portfolio.holdings[currentSymbol]; // 해당 심볼의 보유 정보

        // 종목을 보유하고 있고, 수량이 0보다 크고, 평균 매수 가격이 유효한 숫자인 경우에만 선을 그림
        if (holding && holding.quantity > 0 && typeof holding.avgPrice === 'number' && !isNaN(holding.avgPrice)) {
            const avgPrice = holding.avgPrice;
            const yCoord = y.getPixelForValue(avgPrice); // 평균 매수 가격을 Y축 픽셀 좌표로 변환

            // 차트 영역 내에 있을 때만 그림
            if (yCoord >= top && yCoord <= bottom) {
                 ctx.save(); // 현재 그리기 상태 저장

                 // 매수 평균가 라인 그리기 설정 (빨간색 점선)
                 ctx.strokeStyle = 'red';
                 ctx.lineWidth = 1;
                 ctx.setLineDash([5, 5]); // [선 길이, 공백 길이]

                 ctx.beginPath(); // 새 경로 시작
                 // 차트 왼쪽 끝에서 오른쪽 끝까지 수평선 그리기
                 ctx.moveTo(left, yCoord);
                 ctx.lineTo(right, yCoord);
                 ctx.stroke(); // 선 그리기

                 ctx.restore(); // 저장된 그리기 상태 복원
                 // console.log(`평균 매수 가격 라인 그림: ${currentSymbol}, 가격: ${avgPrice}`); // 디버그 로그
            }
        } else {
             // console.log(`평균 매수 가격 라인 그리지 않음: ${currentSymbol}, 보유: ${holding?.quantity || 0}`); // 디버그 로그
        }
    }
};