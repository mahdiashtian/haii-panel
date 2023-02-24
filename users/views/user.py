from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Q, Sum
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from main.permissions import IsSuperUser
from users.models import TransactionHistory
from users.serializers import CheckDestinationAccountSerializer, SendCreditSerializer, TransactionHistorySerializer

User = get_user_model()


class CheckDestinationAccountAV(APIView):
    def post(self, request):
        serializer = CheckDestinationAccountSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)


class SendCreditAV(APIView):
    def post(self, request):
        serializer = SendCreditSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        user = User.objects.get(username=data['username'])
        user_origin = request.user
        TransactionHistory.objects.create(
            user_sender=user_origin,
            user_receiver=user,
            price=data['amount'],
            transaction_type='TT',
            status="AC",
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class CreditCardNumberShowAP(APIView):
    def get(self, request):
        return Response(
            {'card_number': settings.CARD_NUMBER, 'owner_name': settings.OWNER_NAME, 'credit': request.user.credit})


class IncreaseCreditCardNumberVS(viewsets.ModelViewSet):
    queryset = TransactionHistory.objects.all()
    serializer_class = TransactionHistorySerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['user_receiver__username', 'description']
    pagination_class = PageNumberPagination

    filterset_fields = {
        'date': ['lt', 'gt'],
        'status': ['exact'],
    }

    def get_queryset(self):
        if not self.request.user.is_superuser:
            return self.queryset.filter(Q(user_receiver=self.request.user))
        return self.queryset

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_superuser:
            status = 'AC'
        else:
            status = 'WA'
        serializer.save(user_receiver=self.request.user, status=status)

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'create', 'information']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsSuperUser]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if self.action in ['update', 'partial_update']:
            serializer_class.Meta.read_only_fields = (
                'user_sender', 'document', 'date', 'transaction_type', 'user_receiver', 'description', 'price')
        elif self.action == 'create':
            serializer_class.Meta.read_only_fields = (
                'user_sender', 'status', 'date', 'user_receiver')

        return serializer_class

    @action(detail=False, methods=['get'])
    def information(self, request, *args, **kwargs):
        user = self.request.user
        queryset = self.get_queryset()
        credit_in_the_month = queryset.filter(date__month__exact=1, status="AC").aggregate(Sum('price'))
        credit_blocked = queryset.filter(status="RE").aggregate(Sum('price'))
        count_all = queryset.aggregate(Sum('price'))
        if user.is_superuser:
            debt = User.objects.filter(credit__lte=0).aggregate(Sum('credit'))
        else:
            debt = abs(user.credit) if user.credit < 0 else 0
        return Response({
            'credit': user.credit,
            'debt': debt,
            'credit_in_the_month': credit_in_the_month,
            'credit_blocked': credit_blocked,
            'count_all': count_all,

        })
