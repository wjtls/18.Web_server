async function fetchNewsData() {
    try {
        const response = await fetch('/oversea_news/'); // 서버 API 호출
        const result = await response.json();

        if (result.status) {
            renderNews(result.response.data); // 성공 시 데이터 렌더링
        } else {
            console.error('뉴스 데이터를 가져오지 못했습니다.');
        }
    } catch (error) {
        console.error('API 요청 중 오류 발생:', error);
    }
}

// 뉴스 데이터를 렌더링하는 함수
function renderNews(data) {
    const main_container = document.getElementById('news-main_container');
    main_container.innerHTML = ''; // 기존 내용을 초기화

    data.forEach((item, index) => {
        const avatarColor = index % 2 === 0 ? 'var(--Color-Accent-Purple)' : 'var(--Color-Accent-Yellow)';
        const avatarTextColor = index % 2 === 0 ? '#fff' : '#333';

        // --- HTML 태그 제거 처리 ---
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = item.content; // 임시 div에 HTML로 삽입하여 브라우저가 파싱하도록 함
        const plainTextContent = tempDiv.textContent || tempDiv.innerText || ""; // 순수 텍스트만 추출
        // --------------------------

        const newsHTML = `
            <div class="chat-message">
                <span class="avatar" style="background-color: ${avatarColor}; color: ${avatarTextColor};">${String.fromCharCode(65 + index)}</span>
                <div class="message-content">
                    <b>${item.title} ${item.datetime.split(' ')[0]}</b>
                    <p>${plainTextContent}</p>
                    <a href="${item.url}" target="_blank" style="display: block; margin-top: 5px; color: var(--Color-Accent-Purple); text-decoration: none;">뉴스 링크</a>
                    <span class="timestamp">${item.datetime}</span>
                </div>
            </div>
        `;
        main_container.innerHTML += newsHTML;
    });
}

function makeLinks(text) {
    const urlRegex = /(https?:\/\/[^\s]+)/g;
    // 링크에 스타일 추가
    return text.replace(urlRegex, (url) => `<a href="${url}" target="_blank" style="color: var(--Color-Text-Accent); text-decoration: underline;">${url}</a>`);
}


let lastData = null;
const reportmain_Container = document.getElementById('report-main_container');

function fetchAndUpdateData() {
    fetch('/run_fin_RAG/?t=' + new Date().getTime()) // 캐시 방지
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
         })
        .then(data => {
            if (JSON.stringify(data) !== JSON.stringify(lastData)) { // 데이터 변경 확인
                lastData = data;
                reportmain_Container.innerHTML = ''; // 컨테이너 초기화

                // 중요 단어 강조 함수
                function emphasizeKeywords(text) {
                    const keywords = ['매수', '매도', '상승', '하락', '주의', '관망', '분할', '중요', '리스크', '기회']; // 키워드 추가/수정 가능
                    keywords.forEach(keyword => {
                        // 정규식 수정: 단어 경계를 포함하여 정확한 단어만 강조 (\b 사용)
                        const regex = new RegExp(`\\b(${keyword})\\b`, 'g');
                        // 스타일 직접 적용 대신 CSS 변수 사용
                        text = text.replace(regex, `<strong style="color: var(--Color-Accent-Green); font-weight: var(--font-weight-semibold);">$1</strong>`);
                    });
                    return text;
                }

                // # 또는 *로 시작하는 줄 처리 함수
                function processSpecialFormatting(text) {
                    const lines = text.split('\n');
                    let lastLevel = 0;
                    return lines.map((line, index) => {
                        const trimmedLine = line.trim();
                        const hashCount = (trimmedLine.match(/^#+/) || [''])[0].length;
                        const starCount = (trimmedLine.match(/^\*+/) || [''])[0].length;
                        const level = Math.max(hashCount, starCount);

                        let extraSpace = '';
                        if (level > 0) {
                            // 들여쓰기와 스타일 조정
                            const fontSize = `${0.9 + level * 0.1}rem`; // 레벨에 따라 크기 조정
                            const marginTop = level === 1 ? 'var(--space-md)' : 'var(--space-sm)'; // 첫 레벨은 간격 더 주기
                            const fontWeight = level <= 2 ? 'var(--font-weight-semibold)' : 'var(--font-weight-medium)'; // 낮은 레벨은 더 굵게
                            const color = level === 1 ? 'var(--Color-Text-Primary)' : 'var(--Color-Text-Secondary)'; // 첫 레벨은 주 텍스트 색상
                            lastLevel = level;
                            // 인라인 스타일 사용 최소화, 클래스 사용 권장하나 기존 로직 유지
                            return `<p style="font-weight: ${fontWeight}; font-size: ${fontSize}; margin-top: ${marginTop}; margin-bottom: var(--space-xs); color: ${color}; padding-left: ${level * 10}px;">${makeLinks(trimmedLine.replace(/^#+|^\*+/, '').trim())}</p>`;
                        }
                        lastLevel = 0;
                        // 일반 텍스트 스타일 통일
                        return `<p style="margin-bottom: var(--space-xs); color: var(--Color-Text-Secondary); font-size: 0.9rem;">${makeLinks(trimmedLine)}</p>`;
                    }).join('');
                }

                 if (data.chat_history && Array.isArray(data.chat_history)) {
                    data.chat_history.forEach(item => {
                        const div = document.createElement('div');
                        div.className = 'report-item';

                        // 날짜 형식 개선 (Luxon 사용 가능하면 더 좋음)
                        const formattedDate = item.datetime ? new Date(item.datetime).toLocaleString('ko-KR', { dateStyle: 'short', timeStyle: 'short'}) : '시간 정보 없음';

                        div.innerHTML = `
                            <h3>AI 금융 보고서 (${formattedDate})</h3>
                            <div>${processSpecialFormatting(emphasizeKeywords(item.response || '내용 없음'))}</div>
                        `; // item.response null 체크 추가
                        reportmain_Container.appendChild(div);
                    });
                } else {
                    reportmain_Container.innerHTML = '<p>수신된 보고서 데이터가 없습니다.</p>';
                }
            }
        })
        .catch(error => {
            console.error('Error fetching or processing report data:', error);
            reportmain_Container.innerHTML = `<p style="color: var(--Color-Accent-Red);">보고서 로딩 중 오류가 발생했습니다: ${error.message}</p>`;
            lastData = null; // 오류 발생 시 lastData 초기화하여 다음 시도 가능하게 함
        });
}



function fetchData(trader_id) {
    const sliderValue = parseInt(slider.value, 10); // 슬라이더 값 가져오기
    fetch(`/api/${trader_id}/data/?value=${sliderValue}`)  // 슬라이더 값을 쿼리 파라미터로 추가  // 서버의 API 엔드포인트
        .then(response => response.json())
        .then(data => {
            const priceData = data.price.slice(-sliderValue); // 주가 데이터
            const pvData = data.pv.slice(-sliderValue); // PV 데이터
            const pv_return_data = data.pv_return.slice(-sliderValue) //
            const labels = data.date.slice(-sliderValue); // 날짜 데이터
            const actionData = data.action.slice(-sliderValue); // 매수/매도 시점 데이터
            const action_ratio =data.action_ratio.slice(-sliderValue); // 매매 비중 데이터

            // *********차트에 수익률 표시 ****************
            const total_profit = data.real_profit
            const monthly_profit = data.month_profit //여기서 받아온뒤 html에 표시

             // 1. 한달 수익률 표시 업데이트
            const monthlyProfitSpan = document.querySelector(`.strategy-item[data-strategy-id="${trader_id}"] .monthly-profit`);

            if (monthlyProfitSpan && monthly_profit !== undefined && monthly_profit !== null) {
                const formattedMonthlyProfit = parseFloat(monthly_profit).toFixed(1);
                monthlyProfitSpan.textContent = `${formattedMonthlyProfit} %`;
                // 색상 로직은 수익/손실 따라 accent-red/blue
                monthlyProfitSpan.classList.remove('accent-red', 'accent-blue');
                if (parseFloat(monthly_profit) > 0) { monthlyProfitSpan.classList.add('accent-red'); }  //수익
                else if (parseFloat(monthly_profit) < 0) { monthlyProfitSpan.classList.add('accent-blue'); }  //손실
            } else if (monthlyProfitSpan) {
                 monthlyProfitSpan.textContent = '- %';
                 monthlyProfitSpan.classList.remove('accent-red', 'accent-blue');
                 console.warn(`전략 "${trader_id}" : 한달 수익률 데이터 유효하지 않음. 기본값 표시.`);
            } else {
                console.error(`전략 ID "${trader_id}": .monthly-profit 요소를 찾을 수 없음. HTML 구조 확인 필요.`);
            }
            // --- 2. 전체 수익률 표시할 요소 찾기 및 업데이트 (이 부분 새로 추가) ---

            // 전체 수익률 표시업데이트
            const totalProfitSpan = document.querySelector(`.strategy-item[data-strategy-id="${trader_id}"] .total-profit`);

            // 해당 span 요소가 존재하고, 전체 수익률 데이터도 유효하면 업데이트
            if (totalProfitSpan && total_profit !== undefined && total_profit !== null) {
                // 전체 수익률 값을 소수점 첫째 자리까지 표시 (예시)
                const formattedTotalProfit = parseFloat(total_profit).toFixed(1);

                // span의 텍스트 내용을 업데이트
                totalProfitSpan.textContent = `${formattedTotalProfit} %`;

                // 수익률 값에 따라 글자 색상 변경 (선택 사항)
                // accent-red (손실), accent-blue (수익) 클래스 사용
                totalProfitSpan.classList.remove('accent-red', 'accent-blue'); // 기존 색상 클래스 제거
                if (parseFloat(total_profit) > 0) {
                    totalProfitSpan.classList.add('accent-red'); // (수익)
                } else if (parseFloat(total_profit) < 0) {
                    totalProfitSpan.classList.add('accent-blue'); // (손실)
                }
                 // 0%일 때는 색상 변경 안 함

                 console.log(`전략 "${trader_id}" : 전체 수익률 "${formattedTotalProfit} %" 표시 완료.`);

            } else if (totalProfitSpan) {
                 // totalProfitSpan은 찾았는데 total_profit 값이 유효하지 않은 경우
                 totalProfitSpan.textContent = '- %';
                 totalProfitSpan.classList.remove('accent-red', 'accent-blue');
                 console.warn(`전략 "${trader_id}" : 전체 수익률 데이터 유효하지 않음. 기본값("- %") 표시.`);
            } else {
                // 해당 요소를 아예 찾지 못한 경우 (HTML 문제)
                 console.error(`전략 ID "${trader_id}": 해당하는 .total-profit 요소를 찾을 수 없음. HTML 구조 확인 필요.`);
            }
            // --- 전체 수익률 표시 코드 끝 ---




            // 가격 차트 업데이트
            if (priceChart) {
                priceChart.destroy(); // 기존 차트 삭제
            }

            // priceData의 최소값과 최대값 계산
            const minPrice = Math.min(...priceData);
            const maxPrice = Math.max(...priceData);

            // y축의 최소값과 최대값 설정
            const yMin = minPrice - 5 ; // 최소값에서 -5
            const yMax = maxPrice + 5; // 최대값에서 +5


            priceChart = new Chart(priceCtx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: '주가',
                        data: priceData,
                        borderColor: 'rgb(44,255,0)',
                        borderWidth: 1, // 선 굵기 조정
                        fill: false,
                        pointRadius: 0.1
                    }]
                },
                options: {
                    maintainAspectRatio: false, // 그래프 갱신해도 비율 유지 설정
                    scales: {
                        x: {
                            type: 'category', // 카테고리 타입
                            grid: { display: false },
                            ticks: {
                                color: '#ffffff',
                                font: { size: 12 },
                                maxRotation: 45,
                                autoSkip: true,
                                maxTicksLimit: 10,
                                callback: function(value, index, values) {
                                    // 원하는 형식으로 가공
                                    const dateTime = labels[index]; // labels 배열에서 값 가져오기
                                    return dateTime
                                }
                            }
                        },
                        y: {
                            beginAtZero: true,
                            min: yMin,
                            max: yMax,
                            grid: {
                                display: false // y축 그리드 제거
                            },
                            ticks: {
                                color: '#ffffff', // y축 레이블 색상
                                font: {
                                    size: 14 // y축 레이블 크기
                                }
                            }
                        }
                    },
                    plugins: {
                        zoom: {
                            pan: {
                                enabled: true,
                                mode: 'xy'
                            },
                            zoom: {
                                enabled: true,
                                mode: 'xy'
                            }
                        },
                        annotation: {
                            annotations: []
                        }
                    }
                }
            });

            // 매수 및 매도 시점 표시
            actionData.forEach((action, index) => {

                if (action === '2') { // 매수 시점
                    priceChart.options.plugins.annotation.annotations.push({
                        type: 'point',
                        xValue: labels[index],
                        yValue: priceData[index],
                        backgroundColor: 'rgb(255,0,0)',
                        borderColor: 'rgb(255,0,0)',
                        borderWidth: 1,
                        pointStyle: 'rectRot',
                        radius: 1.5, //크기조절
                        rotation: 1,
                        label: {
                            content: `매수 비율(강도): ${action_ratio[index]}%`,
                            enabled: true,
                            position: 'top'
                        }
                    });
                } else if (action === '0') { // 매도 시점
                    priceChart.options.plugins.annotation.annotations.push({
                        type: 'point',
                        xValue: labels[index],
                        yValue: priceData[index],
                        backgroundColor: 'rgb(0,119,255)',
                        borderColor: 'rgb(0,81,255)',
                        borderWidth: 1,
                        pointStyle: 'rectRot',
                        radius: 1.5,
                        rotation: 225,
                        label: {
                            content: `매도 비율(강도): ${action_ratio[index]}%`,
                            enabled: true,
                            position: 'top'
                        }
                    });
                }
            });

            priceChart.update(); // 차트 업데이트

            // 주석의 x축과 y축 값 출력
            //priceChart.options.plugins.annotation.annotations.forEach((annotation, index) => {
            //    console.log(`주석 ${index}: x축 = ${annotation.xValue}, y축 = ${annotation.yValue}`);
            //});


            // pvData의 최소값과 최대값 계산
            const pv_minPrice = Math.min(...pv_return_data);
            const pv_maxPrice = Math.max(...pv_return_data);

            // y축의 최소값과 최대값 설정
            const y_pv_Min = pv_minPrice - 5; // 최소값에서 -5
            const y_pv_Max = pv_maxPrice + 5; // 최대값에서 +5

            // PV 차트 업데이트
            if (pvChart) {
                pvChart.destroy(); // 기존 차트 삭제
            }

            pvChart = new Chart(pvCtx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: '수익률 그래프(%)',
                        data: pv_return_data,
                        borderColor: 'rgb(44,255,0)',
                        borderWidth: 1, // 선 굵기 조정
                        fill: false,
                        pointRadius: 0.1
                    }]
                },
                options: {
                    maintainAspectRatio: false, // 그래프 갱신해도 비율 유지 설정
                    scales: {
                        x: {
                            type: 'category', // 카테고리 타입
                            grid: { display: false },
                            ticks: {
                                color: '#ffffff',
                                font: { size: 12 },
                                maxRotation: 45,
                                autoSkip: true,
                                maxTicksLimit: 10,
                                callback: function(value, index, values) {
                                    // 원하는 형식으로 가공
                                    const dateTime = labels[index]; // labels 배열에서 값 가져오기
                                    return dateTime
                                }
                            }
                        },
                        y: {
                            beginAtZero: true,
                            min:y_pv_Min,
                            max:y_pv_Max,
                            grid: {
                                display: false // x축 그리드 제거
                            },
                            ticks: {
                                color: '#ffffff', // y축 레이블 색상
                                font: {
                                    size: 14 // y축 레이블 크기
                                }
                            }
                        }
                    },
                    plugins: {
                        zoom: {
                            pan: {
                                enabled: true,
                                mode: 'xy'
                            },
                            zoom: {
                                enabled: true,
                                mode: 'xy'
                            }
                        }
                    }
                }
            });
        })
        .catch(error => {
            console.error('데이터를 가져오는 중 오류 발생:', error);
        });
}
