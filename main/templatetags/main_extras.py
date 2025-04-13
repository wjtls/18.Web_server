# main/templatetags/main_extras.py

from django import template
# from django.contrib.humanize.templatetags.humanize import intcomma # 쉼표 추가를 위해 필요하다면

register = template.Library()

@register.filter(name='currency') # 필터 이름 지정
def format_currency_django(value):
    """
    값을 통화 형식(예: 세 자리마다 쉼표 추가)으로 변환
    """
    try:
        # 숫자로 변환 시도
        amount = float(value)
        # 세 자리마다 쉼표와 소수점 두 자리로 포맷팅
        # 참고: locale 설정을 사용하거나 더 복잡한 포맷팅 라이브러리를 사용
        formatted_value = "{:,.2f}".format(amount) # 예: 12345.67 -> "12,345.67"
        # 만약 intcomma를 사용한다면:
        # amount_int = int(amount)
        # formatted_value = intcomma(amount_int) + "{:.2f}".format(amount % 1)[1:] # 정수부에만 쉼표 추가 후 소수점 결합
        return formatted_value
    except (ValueError, TypeError, ArithmeticError):
        # 변환 실패 시 원래 값 또는 기본값 반환
        return value # 또는 '0.00' 등 기본값
