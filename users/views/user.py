from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Q, Sum
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from main.permissions import IsSuperUser
from users.models import TransactionHistory
from users.serializers.user import CheckDestinationAccountSerializer, SendCreditSerializer, TransactionHistorySerializer

User = get_user_model()


class CheckDestinationAccount(APIView):
    def post(self, request):
        serializer = CheckDestinationAccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)


class SendCredit(APIView):
    def post(self, request):
        serializer = SendCreditSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        user = User.objects.get(username=data['username'])
        user.credit += data['amount']
        user.save()
        user_origin = request.user
        user_origin.credit -= data['amount']
        user_origin.save()
        TransactionHistory.objects.create(
            user_sender=user_origin,
            user_receiver=user,
            price=data['amount'],
            transaction_type='TT',
            status=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class IncreaseCreditCardNumberViewSet(viewsets.ModelViewSet):
    queryset = TransactionHistory.objects.all()
    serializer_class = TransactionHistorySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'date': ['lt', 'gt'],
        'status': ['exact'],
    }

    def get_queryset(self):
        if not self.request.user.is_superuser:
            return self.queryset.filter(Q(user_receiver=self.request.user) | Q(user_sender=self.request.user))
        return self.queryset

    def perform_create(self, serializer):
        serializer.save(user_receiver=self.request.user, transaction_type='CAV', status=False)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return response

    def perform_update(self, serializer):
        result = serializer.save(status=True)
        user = result.user_receiver
        user.credit += result.price
        user.save()

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'create','information']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsSuperUser]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if self.request.method == 'PUT':
            serializer_class.Meta.read_only_fields = (
                'user_sender', 'document', 'date', 'transaction_type', 'user_receiver', 'description', 'price')
        elif self.request.method == 'POST':
            serializer_class.Meta.read_only_fields = (
                'user_sender', 'status', 'date', 'transaction_type', 'user_receiver')

        return serializer_class

    @action(detail=False, methods=['get'])
    def information(self, request, *args, **kwargs):
        user = self.request.user
        credit_in_the_month = self.queryset.filter(date__month__exact=1).aggregate(Sum('price'))
        credit_blocked = self.queryset.filter(status=False).aggregate(Sum('price'))
        count_all = self.queryset.aggregate(Sum('price'))
        if user.is_superuser:
            debt = User.objects.filter(credit__lte=0).aggregate(Sum('credit'))

        else:
            debt = abs(user.credit) if user.credit < 0 else 0
        return Response({
            'debt': debt,
            'credit_in_the_month': credit_in_the_month,
            'credit_blocked': credit_blocked,
            'count_all': count_all,

        })


class IncreaseCreditCardNumberShow(APIView):
    def get(self, request):
        return Response({'card_number': settings.CARD_NUMBER, 'owner_name': settings.OWNER_NAME})
