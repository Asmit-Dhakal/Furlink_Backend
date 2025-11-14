from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db import transaction
from decimal import Decimal

from .models import Order, ShopPayment
from .serializers import ShopTransactionSerializer
from authuser.models import Account
class PayWithAccountAPIView(APIView):

	permission_classes = [IsAuthenticated]

	def post(self, request):
		order_id = request.data.get('order_id')
		if not order_id:
			return Response({'detail': 'order_id required'}, status=status.HTTP_400_BAD_REQUEST)

		order = get_object_or_404(Order, pk=order_id)
		if order.user != request.user:
			return Response({'detail': 'not allowed'}, status=status.HTTP_403_FORBIDDEN)

		if order.status == Order.STATUS_PAID:
			return Response({'detail': 'Order already paid'}, status=status.HTTP_200_OK)

		try:
			with transaction.atomic():
				acct = Account.objects.select_for_update().get(user=request.user)
				order_locked = Order.objects.select_for_update().get(pk=order.pk)

				amount = Decimal(order_locked.total_amount)
				if not acct.can_charge(amount):
					return Response({'detail': 'Insufficient funds in Account'}, status=status.HTTP_400_BAD_REQUEST)

				acct.charge(amount)

				order_locked.status = Order.STATUS_PAID
				order_locked.save(update_fields=['status'])

				tx = ShopPayment.objects.create(
					order=order_locked,
					user=request.user,
					amount=amount,
					currency=order_locked.currency or 'USD',
					description=f'Order {order_locked.id} paid with account balance',
				)

		except Account.DoesNotExist:
			return Response({'detail': 'account not found'}, status=status.HTTP_400_BAD_REQUEST)
		except Exception as exc:
			return Response({'detail': 'failed to process payment', 'error': str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

		serializer = ShopTransactionSerializer(tx)
		return Response({'detail': 'order paid', 'transaction': serializer.data}, status=status.HTTP_200_OK)



# class InitiateShopPaymentAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         """Initiate a shop-scoped payment for an order.

#         Expected body: { "order_id": int, "success_url": str?, "failure_url": str?, "product_code": str? }
#         """
#         order_id = request.data.get('order_id')
#         if not order_id:
#             return Response({'detail': 'order_id required'}, status=status.HTTP_400_BAD_REQUEST)

#         order = get_object_or_404(Order, pk=order_id)
#         # ownership check
#         if order.user != request.user and not request.user.is_staff:
#             return Response({'detail': 'not allowed'}, status=status.HTTP_403_FORBIDDEN)

#         if order.status != Order.STATUS_PENDING:
#             return Response({'detail': 'order not pending', 'order_status': order.status}, status=status.HTTP_400_BAD_REQUEST)

#         # create ShopPayment
#         tx_uuid = str(uuid.uuid4())
#         amount = order.total_amount
#         currency = order.currency or 'NPR'

#         payment = ShopPayment.objects.create(
#             order=order,
#             user=request.user,
#             tx_uuid=tx_uuid,
#             amount=amount,
#             currency=currency,
#             status=ShopPayment.STATUS_PENDING,
#             raw_response={'order_id': order.id},
#         )

#         # prepare eSewa
#         product_code = request.data.get('product_code') or 'EPAYTEST'
#         success_url = request.data.get('success_url') or getattr(settings, 'ESEWA_SUCCESS_URL', None)
#         failure_url = request.data.get('failure_url') or getattr(settings, 'ESEWA_FAILURE_URL', None)

#         esewa = EsewaPayment(
#             product_code=product_code,
#             success_url=success_url,
#             failure_url=failure_url,
#             amount=amount,
#             total_amount=amount,
#             transaction_uuid=tx_uuid,
#             secret_key=getattr(settings, 'ESEWA_SECRET_KEY', None),
#         )

#         signature = None
#         try:
#             signature = esewa.create_signature()
#         except Exception:
#             signature = None

#         form_html = ''
#         try:
#             form_html = esewa.generate_form()
#         except Exception:
#             form_html = ''

#         payment.signature = signature
#         payment.raw_response = {**(payment.raw_response or {}), 'form_html_present': bool(form_html)}
#         payment.save()

#         return Response({
#             'tx_uuid': tx_uuid,
#             'signature': signature,
#             'form_html': form_html,
#             'esewa_action': 'https://rc-epay.esewa.com.np/api/epay/main/v2/form',
#         }, status=status.HTTP_201_CREATED)


# class ShopPaymentCallbackAPIView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         payload = request.data.dict() if hasattr(request.data, 'dict') else request.data
#         tx_uuid = payload.get('transaction_uuid') or payload.get('pid') or payload.get('oid')
#         if not tx_uuid:
#             return Response({'detail': 'transaction identifier required'}, status=status.HTTP_400_BAD_REQUEST)

#         payment = ShopPayment.objects.filter(tx_uuid=tx_uuid).first()
#         if not payment:
#             # create placeholder if needed
#             payment = ShopPayment.objects.create(tx_uuid=tx_uuid, order=None, amount=0, status=ShopPayment.STATUS_PENDING)

#         prev_status = payment.status
#         payment.raw_response = payload

#         is_success = (str(payload.get('status', '')).upper() in ('SUCCESS', 'COMPLETE', 'COMPLETED') or payload.get('rid') or payload.get('refId'))
#         if is_success:
#             payment.status = ShopPayment.STATUS_COMPLETED
#         else:
#             if payload.get('status') in ('FAILED', 'failed', 'ERROR'):
#                 payment.status = ShopPayment.STATUS_FAILED

#         # mark order paid when moving to completed
#         if payment.status == ShopPayment.STATUS_COMPLETED and prev_status != ShopPayment.STATUS_COMPLETED and payment.order:
#             try:
#                 payment.order.status = Order.STATUS_PAID
#                 payment.order.save(update_fields=['status'])
#                 payment.credited = True
#                 payment.save(update_fields=['credited', 'raw_response', 'status'])
#             except Exception:
#                 payment.raw_response = {**(payment.raw_response or {}), 'order_update_error': 'failed to set order paid'}
#                 payment.save()
#         else:
#             payment.save()

#         return Response({'detail': 'shop callback recorded', 'tx_uuid': payment.tx_uuid}, status=status.HTTP_200_OK)
