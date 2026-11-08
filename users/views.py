from rest_framework import generics
from rest_framework.permissions import AllowAny

from .serializers import RegisterSerializer

from rest_framework.response import Response
from rest_framework import status
from .serializers import LogoutSerializer


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]



class LogoutView(generics.GenericAPIView):

    serializer_class = LogoutSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {'detail': 'Successfully logged out.'},
            status=status.HTTP_205_RESET_CONTENT
        )


