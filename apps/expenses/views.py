from typing import Any
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from .serializers import ExpenseSerializer, ExpenseCreateSerializer
from .permissions import IsOwnerOrAdmin
from .pagination import UserExpensePagination, AdminExpensePagination
from .filters import ExpenseFilter
from .services import ExpenseService, ExpenseNotFoundError, ExpenseActionConflictError


class ExpenseListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    filterset_class = ExpenseFilter
    pagination_class = UserExpensePagination

    def get_serializer_class(self) -> Any:
        if self.request.method == "POST":
            return ExpenseCreateSerializer
        return ExpenseSerializer

    def get_queryset(self) -> Any:
        # pass GET params as filters
        filters = dict(self.request.query_params.items())
        return ExpenseService.list_for_user(self.request.user, filters)

    def perform_create(self, serializer: Any) -> None:
        # serializer.create will call ExpenseService.create_expense
        expense = serializer.save()
        return expense

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        expense = serializer.save()
        out_serializer = ExpenseSerializer(expense, context={"request": request})
        return Response(out_serializer.data, status=status.HTTP_201_CREATED)


class ExpenseDetailView(generics.RetrieveDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    serializer_class = ExpenseSerializer

    def get_object(self) -> Any:
        pk = self.kwargs.get("pk")
        try:
            expense = ExpenseService.get_by_id(int(pk), user=self.request.user)
        except ExpenseNotFoundError:
            raise generics.Http404
        return expense

    def destroy(self, request, *args, **kwargs) -> Response:
        pk = self.kwargs.get("pk")
        try:
            ExpenseService.delete_expense(int(pk), request.user)
        except ExpenseNotFoundError:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ExpenseApproveView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, pk: int) -> Response:
        try:
            expense = ExpenseService.approve_expense(int(pk), request.user)
        except ExpenseNotFoundError:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except ExpenseActionConflictError:
            return Response(status=status.HTTP_409_CONFLICT)
        serializer = ExpenseSerializer(expense, context={"request": request})
        return Response(serializer.data)


class ExpenseRejectView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, pk: int) -> Response:
        reason = request.data.get("reason")
        try:
            expense = ExpenseService.reject_expense(int(pk), request.user, reason)
        except ExpenseNotFoundError:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except ExpenseActionConflictError:
            return Response(status=status.HTTP_409_CONFLICT)
        serializer = ExpenseSerializer(expense, context={"request": request})
        return Response(serializer.data)


class AdminExpenseListView(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = ExpenseSerializer
    filterset_class = ExpenseFilter
    pagination_class = AdminExpensePagination

    def get_queryset(self) -> Any:
        filters = dict(self.request.query_params.items())
        return ExpenseService.list_for_admin(filters)
