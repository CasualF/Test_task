from rest_framework import generics, permissions
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UserRegistrationSerializer, ActivationSerializer, UserSerializer
from .tasks import send_activation_email
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ModelViewSet
from .permissions import IsOwnerOfProfile


User = get_user_model()


class UserRegistrationView(APIView):
    permission_classes = permissions.AllowAny,

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        if user:
            try:
                send_activation_email.delay(user.email, user.activation_code)
            except:
                return Response({'message': "Registered, but wasn't able to send activation code to email",
                                 'data': serializer.data}, status=201)

        return Response(serializer.data, status=201)


class LogoutView(APIView):
    permission_classes = permissions.IsAuthenticated,

    def post(self, request):
        try:
            data = request.data
            refresh_token = data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
                return Response('You logged out', status=205)

            else:
                return Response("Refresh token wasn't provided", status=400)
        except:
            return Response('Something went wrong', status=400)


class ActivationView(generics.GenericAPIView):
    permission_classes = permissions.AllowAny,
    serializer_class = ActivationSerializer

    # Usually activation done through post request but in order to be able to activate
    # account by simply clicking the link in email get request was made

    def get(self, request):
        code = request.GET.get('c')
        user = get_object_or_404(User, activation_code=code)
        user.is_active = True
        user.activation_code = ''
        user.save()
        return Response('Successful activation', status=200)

    def post(self, request):
        data = request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response('Successful activation', status=200)


class UserView(ModelViewSet):
    # User CRUD for admin just in case
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = permissions.IsAdminUser,


class ProfileView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # I realized afterwords that the custom permission that I made is
    # practically useless but since I had already made it I just kept it
    permission_classes = IsOwnerOfProfile, permissions.IsAuthenticated

    def get_object(self):
        queryset = self.get_queryset()
        user = self.request.user
        obj = get_object_or_404(queryset, email=user.email)

        self.check_object_permissions(self.request, obj)

        return obj
