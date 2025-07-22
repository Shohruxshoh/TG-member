# from django_filters.rest_framework import DjangoFilterBackend
# from rest_framework import viewsets, permissions, serializers, status, mixins
# from rest_framework.decorators import action
# from rest_framework.filters import SearchFilter, OrderingFilter
# from rest_framework.response import Response
# from .models import Order
# from .serializers import OrderSerializer, OrderDetailSerializer
# from .filters import OrderFilter
#
#
# class OrderViewSet(mixins.ListModelMixin,
#                    mixins.RetrieveModelMixin,
#                    mixins.UpdateModelMixin,
#                    mixins.DestroyModelMixin,
#                    viewsets.GenericViewSet):
#     queryset = Order.objects.all()
#     serializer_class = OrderSerializer
#     permission_classes = [permissions.IsAuthenticated]
#
#     # 🔽 Filter va qidiruv sozlamalari
#     filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
#     filterset_class = OrderFilter
#     search_fields = ['status', 'service__category']  # qidiruv uchun
#     ordering_fields = ['created_at', 'price']  # tartiblash
#     ordering = ['-created_at']  # default ordering
#
#     def get_queryset(self):
#         # Foydalanuvchi faqat o‘z buyurtmalarini ko‘radi
#         return Order.objects.filter(user=self.request.user, is_active=True)
#
#     def get_serializer_class(self):
#         if self.action == 'retrieve':
#             return OrderDetailSerializer
#         return OrderSerializer
#
#     def perform_create(self, serializer):
#         user = self.request.user
#         service_price = serializer.validated_data['service_price']
#
#         # Balansni tekshirish (faraz qilamiz: user.balance mavjud)
#         # if user.balance < service_price.price:
#         #     raise serializers.ValidationError("Balansingizda mablag' yetarli emas.")
#         #
#         # # Balansdan yechish va buyurtma yaratish
#         # user.balance -= service_price.price
#         # user.save()
#         serializer.save(user=user, price=service_price.price)
#
#     @action(detail=True, methods=['post'], url_path='complete')
#     def mark_completed(self, request, pk=None):
#         order = self.get_object()
#
#         if order.status != "PENDING":
#             return Response({"detail": "Buyurtma allaqachon yakunlangan yoki muvaffaqiyatsiz."},
#                             status=status.HTTP_400_BAD_REQUEST)
#
#         order.status = "COMPLETED"
#         order.save()
#         return Response({"detail": "Buyurtma muvaffaqiyatli yakunlandi."})
