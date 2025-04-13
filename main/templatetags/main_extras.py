def format_currency(value):
    try:
        # 숫자로 변환 시도
        amount = float(value)
        # 세 자리마다 쉼표 추가
        return amount
    except (ValueError, TypeError):
        # 변환 실패 시 원래 값 또는 빈 문자열 반환
        return value # 또는 ''

app.jinja_env.filters['currency'] = format_currency
