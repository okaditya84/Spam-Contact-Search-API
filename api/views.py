from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from django.db.models import Count
from .models import CustomUser, Contact, SpamReport
from .serializers import (
    UserRegistrationSerializer, 
    UserSerializer, 
    LoginSerializer, 
    SearchResultSerializer, 
    SpamReportSerializer
)

# Registration endpoint – allows new users to register.
class RegisterView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

# Login endpoint – authenticates the user and returns a token.
class LoginView(views.APIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Search by name – returns results from both registered users and contacts.
class SearchByNameView(views.APIView):
    def get(self, request):
        query = request.query_params.get('q', '')
        if not query:
            return Response({'detail': 'Query parameter "q" is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Calculate spam counts per phone number
        spam_counts = SpamReport.objects.values('phone_number').annotate(count=Count('id'))
        spam_dict = {item['phone_number']: item['count'] for item in spam_counts}

        # Registered users: names starting with query, then names containing query
        users_start = CustomUser.objects.filter(name__istartswith=query)
        users_contain = CustomUser.objects.filter(name__icontains=query).exclude(id__in=users_start)
        
        # Contacts: names starting with query then containing query
        contacts_start = Contact.objects.filter(name__istartswith=query)
        contacts_contain = Contact.objects.filter(name__icontains=query).exclude(id__in=contacts_start)

        results = []

        # Add registered users to results
        for user in list(users_start) + list(users_contain):
            spam_count = spam_dict.get(user.phone_number, 0)
            result = {
                'id': user.id,
                'name': user.name,
                'phone_number': user.phone_number,
                'spam_count': spam_count,
                'is_registered': True,
                'email': None  # Email is shown only in detail view if allowed.
            }
            results.append(result)

        # Add contacts to results
        for contact in list(contacts_start) + list(contacts_contain):
            spam_count = spam_dict.get(contact.phone_number, 0)
            result = {
                'id': contact.id,
                'name': contact.name,
                'phone_number': contact.phone_number,
                'spam_count': spam_count,
                'is_registered': False,
                'email': None
            }
            results.append(result)

        serializer = SearchResultSerializer(results, many=True)
        return Response(serializer.data)

# Search by phone number – if the number is registered, return that user only; otherwise, return all matching contacts.
class SearchByPhoneView(views.APIView):
    def get(self, request):
        query = request.query_params.get('q', '')
        if not query:
            return Response({'detail': 'Query parameter "q" is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        spam_counts = SpamReport.objects.values('phone_number').annotate(count=Count('id'))
        spam_dict = {item['phone_number']: item['count'] for item in spam_counts}

        results = []
        try:
            user = CustomUser.objects.get(phone_number=query)
            spam_count = spam_dict.get(user.phone_number, 0)
            result = {
                'id': user.id,
                'name': user.name,
                'phone_number': user.phone_number,
                'spam_count': spam_count,
                'is_registered': True,
                'email': None
            }
            results.append(result)
        except CustomUser.DoesNotExist:
            contacts = Contact.objects.filter(phone_number=query)
            for contact in contacts:
                spam_count = spam_dict.get(contact.phone_number, 0)
                result = {
                    'id': contact.id,
                    'name': contact.name,
                    'phone_number': contact.phone_number,
                    'spam_count': spam_count,
                    'is_registered': False,
                    'email': None
                }
                results.append(result)
        serializer = SearchResultSerializer(results, many=True)
        return Response(serializer.data)

# Detailed person view – shows full details and spam likelihood.
# For registered users, the email is only returned if the requester is in that user’s contact list.
class PersonDetailView(views.APIView):
    def get(self, request, identifier):
        spam_counts = SpamReport.objects.values('phone_number').annotate(count=Count('id'))
        spam_dict = {item['phone_number']: item['count'] for item in spam_counts}
        try:
            # Try to find a registered user by id.
            user = CustomUser.objects.get(id=identifier)
            spam_count = spam_dict.get(user.phone_number, 0)
            # Check if the requester is in the user's contact list.
            include_email = Contact.objects.filter(owner=user, phone_number=request.user.phone_number).exists()
            result = {
                'id': user.id,
                'name': user.name,
                'phone_number': user.phone_number,
                'spam_count': spam_count,
                'is_registered': True,
                'email': user.email if include_email else None
            }
            return Response(result)
        except CustomUser.DoesNotExist:
            try:
                # Otherwise, try to find a contact.
                contact = Contact.objects.get(id=identifier)
                spam_count = spam_dict.get(contact.phone_number, 0)
                result = {
                    'id': contact.id,
                    'name': contact.name,
                    'phone_number': contact.phone_number,
                    'spam_count': spam_count,
                    'is_registered': False,
                    'email': None
                }
                return Response(result)
            except Contact.DoesNotExist:
                return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

# Endpoint to mark a phone number as spam.
class SpamReportView(views.APIView):
    def post(self, request):
        phone_number = request.data.get('phone_number')
        if not phone_number:
            return Response({'detail': 'phone_number is required.'}, status=status.HTTP_400_BAD_REQUEST)
        # Ensure a user can only report a number once.
        spam_report, created = SpamReport.objects.get_or_create(phone_number=phone_number, reported_by=request.user)
        if created:
            return Response({'detail': f'Phone number {phone_number} marked as spam.'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'detail': f'You have already reported {phone_number} as spam.'}, status=status.HTTP_200_OK)
