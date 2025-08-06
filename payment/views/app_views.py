from django.db import transaction
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from rest_framework import permissions, status, views
from rest_framework.response import Response
from balance.models import OrderBuy, Buy, Currency
from django.shortcuts import get_object_or_404
from payment.utils import generate_url
from users.models import User
from service.schemas import COMMON_RESPONSES
from decimal import Decimal


@extend_schema(
    responses={
        200: {
            'type': 'object',
            'properties': {
                'message': {'type': 'string'},
            }
        },
        **COMMON_RESPONSES
    },
)
class PaymentEncodeAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, buy_id, *args, **kwargs):
        user = request.user
        buy = get_object_or_404(Buy, pk=buy_id)
        s_currency = Currency.objects.filter(is_active=True).first()

        if not s_currency:
            return Response({"detail": "Active currency not found."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        price = Decimal(s_currency.som) * Decimal(buy.price)
        order = OrderBuy.objects.create(buy=buy, user=user, coin=buy.coin, price=price)

        param = generate_url(user, buy, order)
        return Response({"message": f"https://checkout.paycom.uz/{param}"}, status=status.HTTP_201_CREATED)


@extend_schema(
    parameters=[
        OpenApiParameter("order_id", str, OpenApiParameter.QUERY, required=True)
    ],
    responses={
        200: {
            'type': 'object',
            'properties': {
                'result': {'type': 'boolean'},
            }
        },
        **COMMON_RESPONSES
    }
)
class CheckOderBuyAPIView(views.APIView):

    def get(self, request, *args, **kwargs):
        order_id = request.query_params.get('order_id')
        if not order_id:
            return Response({"detail": "order_id kiritilmagan!"}, status=status.HTTP_400_BAD_REQUEST)

        order = get_object_or_404(OrderBuy, pk=order_id)

        return Response({
            "result": True,
            "user_id": order.user.id,
            "amount": float(order.price * 100),  # Decimal to float
            "is_paid": order.is_paid
        }, status=status.HTTP_200_OK)


@extend_schema(
    parameters=[
        OpenApiParameter("order_id", str, OpenApiParameter.QUERY, required=True)
    ],
    responses={
        200: {
            'type': 'object',
            'properties': {
                'result': {'type': 'boolean'},
            }
        },
        **COMMON_RESPONSES
    }
)
class PaymentPaidAPIView(views.APIView):

    def post(self, request, *args, **kwargs):
        order_id = self.request.query_params.get('order_id')
        if not order_id:
            return Response({"detail": "order_id kiritilmagan!"}, status=status.HTTP_400_BAD_REQUEST)

        order = get_object_or_404(OrderBuy, pk=order_id, is_paid=False)

        with transaction.atomic():
            order.is_paid = True
            order.save()
            balance_obj = order.user.user_balance
            if not balance_obj:
                return Response({"detail": "User balance object not found."},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            balance_obj.balance += order.coin
            balance_obj.save()
        return Response({"result": True}, status=status.HTTP_200_OK)
