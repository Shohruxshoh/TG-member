import base64
from decimal import Decimal, ROUND_HALF_UP


def generate_url(user, buy, order):
    price = (Decimal(order.price) * 100).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    message = f"""m=680b5f75dc05045a2afc8199;ac.user_id={user.id}:{order.pk};a={price}"""
    message_bytes = message.encode('utf-8')  # String -> bytes
    base64_bytes = base64.b64encode(message_bytes)  # base64 encode
    base64_message = base64_bytes.decode('utf-8')

    # base64_message1 = base64_message
    # base64_bytes1 = base64_message1.encode('utf-8')  # string -> bytes
    # message_bytes1 = base64.b64decode(base64_bytes1)  # base64 decode
    # message = message_bytes1.decode('utf-8')  # bytes -> string
    #
    # print(17, message)
    return base64_message
