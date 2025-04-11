
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
    const container = document.getElementById('news-container');
    container.innerHTML = ''; // 기존 내용을 초기화

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
        container.innerHTML += newsHTML;
    });
}