import requests

from django.conf import settings
from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from orders.models import Order

from .models import Payment
from .serializers import PaymentSerializer
from .services import (
    create_payment_attempt,
    mark_payment_failed,
    mark_payment_successful,
)


class PaymentStartView(APIView):
    # Only authenticated users can start a payment.
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):

        # Check whether the gateway credentials are configured.
        if (
            not settings.ZARINPAL_MERCHANT_ID
            or settings.ZARINPAL_MERCHANT_ID == 'your_sandbox_merchant_id'
        ):
            return Response(
                {'detail': 'Zarinpal Merchant ID is not configured.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        try:
            # Create a payment attempt for the logged-in user's order.
            # The service checks ownership, order status, and amount.
            payment = create_payment_attempt(
                user=request.user,
                order_id=order_id,
            )

        except Order.DoesNotExist:
            return Response(
                {'detail': 'Order not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        except DjangoValidationError as exc:
            return Response(
                {'detail': exc.messages},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Convert Toman to Rial because Zarinpal expects Rial.
        amount_in_rial = int(payment.amount) * 10

        # Prepare the payment request for Zarinpal.
        payload = {
            'merchant_id': settings.ZARINPAL_MERCHANT_ID,
            'amount': amount_in_rial,
            'callback_url': settings.ZARINPAL_CALLBACK_URL,
            'description': (
                f'Payment for order {payment.order.order_number}'
            ),
            'metadata': {
                'mobile': payment.order.phone_number,
            },
        }

        try:
            # Send the payment request to Zarinpal.
            gateway_response = requests.post(
                settings.ZARINPAL_REQUEST_URL,
                json=payload,
                headers={
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                },
                timeout=15,
            )

            gateway_response.raise_for_status()
            result = gateway_response.json()

        except (requests.RequestException, ValueError):
            # Mark the attempt as failed if the gateway request fails.
            mark_payment_failed(payment.id)

            return Response(
                {'detail': 'Could not contact the payment gateway.'},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        # Extract the response data from Zarinpal.
        data = result.get('data') or {}
        authority = data.get('authority')

        # Code 100 means the payment request was created successfully.
        if data.get('code') != 100 or not authority:

            mark_payment_failed(payment.id)

            return Response(
                {
                    'detail': 'Zarinpal could not create the payment request.',
                    'gateway_code': data.get('code'),
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        # Save the authority for later payment verification.
        payment.authority = authority
        payment.save(
            update_fields=['authority', 'updated_at']
        )

        # Return the payment details and gateway URL to the client.
        return Response(
            {
                'payment': PaymentSerializer(payment).data,
                'payment_url': (
                    f'{settings.ZARINPAL_STARTPAY_URL}{authority}'
                ),
            },
            status=status.HTTP_201_CREATED,
        )


class PaymentVerifyView(APIView):
    # The gateway callback does not carry the user's API token.
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):

        # Read the callback parameters sent by Zarinpal.
        authority = request.query_params.get('Authority')
        gateway_status = request.query_params.get('Status')

        if not authority:
            return Response(
                {'detail': 'Missing payment authority.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Find the payment using its saved authority.
            payment = Payment.objects.select_related('order').get(
                authority=authority
            )

        except Payment.DoesNotExist:
            return Response(
                {'detail': 'Payment not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Handle cancelled or unsuccessful payments.
        if gateway_status != 'OK':

            try:
                mark_payment_failed(payment.id)

            except DjangoValidationError:
                # Never change a successful payment to failed.
                pass

            payment.refresh_from_db()

            return Response(
                {
                    'detail': 'Payment was cancelled or not completed.',
                    'payment_status': payment.status,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Avoid verifying an already successful payment again.
        if payment.status == Payment.Status.SUCCESSFUL:
            return Response(
                {
                    'detail': 'Payment was already verified.',
                    'payment': PaymentSerializer(payment).data,
                },
                status=status.HTTP_200_OK,
            )

        # Prepare the verification request.
        payload = {
            'merchant_id': settings.ZARINPAL_MERCHANT_ID,
            'amount': int(payment.amount) * 10,
            'authority': authority,
        }

        try:
            # Ask Zarinpal to verify the transaction.
            gateway_response = requests.post(
                settings.ZARINPAL_VERIFY_URL,
                json=payload,
                headers={
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                },
                timeout=15,
            )

            gateway_response.raise_for_status()
            result = gateway_response.json()

        except (requests.RequestException, ValueError):
            # Keep the payment pending if verification cannot be completed.
            return Response(
                {'detail': 'Could not verify payment with the gateway.'},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        data = result.get('data') or {}
        verification_code = data.get('code')

        # Code 100 means newly verified; 101 means already verified.
        if verification_code in (100, 101):

            ref_id = data.get('ref_id')

            if ref_id is None:
                return Response(
                    {
                        'detail': (
                            'Gateway response did not include a reference ID.'
                        )
                    },
                    status=status.HTTP_502_BAD_GATEWAY,
                )

            try:
                # Update payment and order through the existing service.
                payment = mark_payment_successful(
                    payment.id,
                    str(ref_id),
                )

            except DjangoValidationError as exc:
                return Response(
                    {'detail': exc.messages},
                    status=status.HTTP_409_CONFLICT,
                )

            return Response(
                {
                    'detail': 'Payment verified successfully.',
                    'payment': PaymentSerializer(payment).data,
                },
                status=status.HTTP_200_OK,
            )

        # Mark the payment as failed if verification was rejected.
        try:
            payment = mark_payment_failed(payment.id)

        except DjangoValidationError:
            payment.refresh_from_db()

        return Response(
            {
                'detail': 'Payment verification failed.',
                'payment_status': payment.status,
                'gateway_code': verification_code,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )