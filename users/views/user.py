from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from users.serializers.user import CheckDestinationAccountSerializer, SendCreditSerializer

User = get_user_model()


class CheckDestinationAccount(APIView):
    def post(self, request):
        serializer = CheckDestinationAccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)


class SendCredit(APIView):
    def post(self, request):
        serializer = SendCreditSerializer(data=request.data,context={'request': request})
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        user = User.objects.get(username=data['username'])
        user.credit += data['amount']
        user.save()
        user_origin = request.user
        user_origin.credit -= data['amount']
        user_origin.save()
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
