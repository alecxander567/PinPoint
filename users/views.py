from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import User, PasswordResetToken
from .serializers import UserSerializer
import bcrypt
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import EmailMessage
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


# Sign Up
@api_view(["POST"])
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {"message": "User created successfully"}, status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Log In
@api_view(["POST"])
def login(request):
    email = request.data.get("email")
    password = request.data.get("password")

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response(
            {"error": "Invalid email or password"}, status=status.HTTP_401_UNAUTHORIZED
        )

    if bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8")):
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user_id": str(user.id),
                "name": user.name,
            }
        )

    return Response(
        {"error": "Invalid email or password"}, status=status.HTTP_401_UNAUTHORIZED
    )


# Log Out
@api_view(["POST"])
def logout(request):
    return Response({"message": "Logout successful, delete the token on client side."})


# Forgot Password
@api_view(["POST"])
def forgot_password(request):
    email = request.data.get("email")

    if not email:
        return Response(
            {"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user = User.objects.get(email=email)

        # Invalidate old unused tokens
        PasswordResetToken.objects.filter(user=user, used=False).delete()

        # Create new reset token
        reset_token = PasswordResetToken.objects.create(user=user)

        reset_link = f"{settings.FRONTEND_URL}/reset-password?token={reset_token.token}"

        email_message = EmailMessage(
            subject="Reset your Item Finder password",
            body=(
                f"Hi {user.name},\n\n"
                f"Click the link below to reset your password. "
                f"This link expires in 1 hour.\n\n"
                f"{reset_link}\n\n"
                f"If you didn't request this, you can safely ignore this email."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        email_message.send()

        logger.info(f"Password reset link sent to {email} | Token: {reset_token.token}")

    except User.DoesNotExist:
        logger.info(f"Password reset requested for non-existent email: {email}")
        pass

    return Response(
        {"message": "If that email is registered, a reset link has been sent."}
    )


@api_view(["POST", "OPTIONS"])
def reset_password(request):
    if request.method == "OPTIONS":
        return Response(status=status.HTTP_200_OK)

    token_str = request.data.get("token")
    new_password = request.data.get("password")

    if not token_str:
        return Response({"error": "Token is required."}, status=400)

    if not new_password:
        return Response({"error": "Password is required."}, status=400)

    if len(new_password) < 8:
        return Response(
            {"error": "Password must be at least 8 characters."}, status=400
        )

    try:
        reset_token = PasswordResetToken.objects.get(token=token_str)
    except PasswordResetToken.DoesNotExist:
        return Response({"error": "Invalid or expired reset link."}, status=400)

    if not reset_token.is_valid():
        return Response(
            {"error": "This reset link has expired or already been used."}, status=400
        )

    try:
        hashed_password = bcrypt.hashpw(
            new_password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

        reset_token.user.password = hashed_password
        reset_token.user.save()

        reset_token.used = True
        reset_token.save()

        return Response({"message": "Password reset successful. You can now log in."})
    except Exception as e:
        print("Unexpected error during reset:", str(e))
        return Response({"error": "Server error during password reset."}, status=500)
