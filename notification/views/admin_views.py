from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from notification.serializers.admin_serializers import ANotificationSerializer
from service.schemas import COMMON_RESPONSES
from users.permissions import IsAdminStaff


@extend_schema(
    request=ANotificationSerializer,
    responses={
        201: OpenApiResponse(
            response=None,
            examples=[
                OpenApiExample(
                    "Successful",
                    value={
                        "detail": "Notification sent to all online users",
                    }
                )
            ]
        ),
        **COMMON_RESPONSES
    }
)
class ANotificationCreateAPIView(APIView):
    permission_classes = [IsAdminStaff]

    def post(self, request, *args, **kwargs):
        serializer = ANotificationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Notification sent to all online users"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
