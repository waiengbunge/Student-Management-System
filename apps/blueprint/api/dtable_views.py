from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import StudentSerializer, CourseSerializer
from ..models import Student, Course


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 200


class StudentListAPI(generics.ListAPIView):
    queryset = Student.objects.all().order_by('student_number')
    serializer_class = StudentSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'program__id']
    search_fields = ['student_number', 'first_name', 'last_name']
    ordering_fields = ['student_number', 'first_name', 'last_name']


class CourseListAPI(generics.ListAPIView):
    queryset = Course.objects.all().order_by('code')
    serializer_class = CourseSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['program__id']
    search_fields = ['code', 'name']
    ordering_fields = ['code', 'name']
