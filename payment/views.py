# Create your views here.

from django_esewa import EsewaPayment
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from .serializers import InitiatePaymentSerializer, TransactionSerializer
from decimal import Decimal, InvalidOperation
from .models import Transaction
from django.conf import settings
from django.shortcuts import get_object_or_404
import uuid


class InitiateEsewaPaymentAPIView(APIView):

	permission_classes = [IsAuthenticated]

	def post(self, request):
		serializer = InitiatePaymentSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		data = serializer.validated_data

		amount = data['amount']
		product_code = data.get('product_code', 'EPAYTEST')
		tx_uuid = data.get('transaction_uuid') or str(uuid.uuid4())
		success_url = data.get('success_url') or getattr(settings, 'ESEWA_SUCCESS_URL', 'http://localhost:8009/payment/success/')
		failure_url = data.get('failure_url') or getattr(settings, 'ESEWA_FAILURE_URL', 'http://localhost:8009/payment/failure/')

		transaction_defaults = {
			'user': request.user,
			'amount': amount,
			'currency': data.get('currency', 'NPR'),
			'status': Transaction.STATUS_PENDING,
		}

		transaction, created = Transaction.objects.get_or_create(tx_uuid=tx_uuid, defaults=transaction_defaults)
		# if transaction already existed, ensure we attach user/amount when appropriate
		if not created:
			updated = False
			if (not transaction.user) and request.user:
				transaction.user = request.user
				updated = True
			# if incoming amount differs and stored amount is zero (e.g., callback-created placeholder), update it
			try:
				if (not transaction.amount or Decimal(transaction.amount) == Decimal('0')) and Decimal(amount) > Decimal('0'):
					transaction.amount = amount
					updated = True
			except Exception:
				# be conservative if parsing fails
				pass
			if updated:
				transaction.save()

		payment = EsewaPayment(
			product_code=product_code,
			success_url=success_url,
			failure_url=failure_url,
			amount=amount,
			total_amount=amount,
			transaction_uuid=tx_uuid,
			secret_key=getattr(settings, 'ESEWA_SECRET_KEY', None),
		)

		try:
			signature = payment.create_signature()
		except Exception:
			signature = None

		form_html = ''
		try:
			form_html = payment.generate_form()
		except Exception:
			form_html = ''

		transaction.signature = signature
		transaction.raw_response = {'form_html_present': bool(form_html)}
		transaction.save()

		return Response({
			'tx_uuid': tx_uuid,
			'signature': signature,
			'form_html': form_html,
			'esewa_action': 'https://rc-epay.esewa.com.np/api/epay/main/v2/form',
		}, status=status.HTTP_201_CREATED)


class EsewaCallbackAPIView(APIView):

	permission_classes = [AllowAny]

	def post(self, request):
		payload = request.data.dict() if hasattr(request.data, 'dict') else request.data
		tx_uuid = payload.get('transaction_uuid') or payload.get('pid') or payload.get('oid')
		if not tx_uuid:
			return Response({'detail': 'transaction identifier (transaction_uuid/pid/oid) required'}, status=status.HTTP_400_BAD_REQUEST)

		tx = Transaction.objects.filter(tx_uuid=tx_uuid).first()
		if not tx:
			tx = Transaction.objects.create(tx_uuid=tx_uuid, amount=0, status=Transaction.STATUS_PENDING)

		# preserve previous status to avoid double-crediting
		previous_status = tx.status
		# store raw payload
		tx.raw_response = payload

		# determine new status
		is_success = payload.get('status') in ('SUCCESS', 'success') or payload.get('rid') or payload.get('refId')
		if is_success:
			tx.status = Transaction.STATUS_COMPLETED
		else:
			if payload.get('status') in ('FAILED', 'failed', 'ERROR'):
				tx.status = Transaction.STATUS_FAILED

		# If transaction just moved to completed, credit the user's account
		if tx.status == Transaction.STATUS_COMPLETED and previous_status != Transaction.STATUS_COMPLETED:
			# find amount to credit: prefer stored tx.amount, else try payload fields
			amount_to_credit = None
			if getattr(tx, 'amount', None) and Decimal(tx.amount) > Decimal('0'):
				amount_to_credit = Decimal(tx.amount)
			else:
				# common eSewa field names: 'tAmt', 'amt', 'amount', 'total_amount'
				for key in ('tAmt', 'amt', 'amount', 'total_amount', 'totalAmount', 'tamount'):
					val = payload.get(key)
					if val:
						try:
							amount_to_credit = Decimal(str(val))
							break
						except (InvalidOperation, TypeError, ValueError):
							continue

			if amount_to_credit and tx.user:
				account = getattr(tx.user, 'account', None)
				if account:
					try:
						account.topup(amount_to_credit)
						tx.raw_response = {**(tx.raw_response or {}), 'credited_amount': str(amount_to_credit)}
					except Exception as exc:
						# attach error to raw_response for debugging
						tx.raw_response = {**(tx.raw_response or {}), 'credit_error': str(exc)}

		tx.save()
		return Response({'detail': 'callback recorded', 'tx_uuid': tx.tx_uuid}, status=status.HTTP_200_OK)



class TransactionDetailAPIView(APIView):
	permission_classes = [IsAuthenticated]

	def get(self, request, tx_uuid):
		tx = get_object_or_404(Transaction, tx_uuid=tx_uuid)
		if tx.user and tx.user != request.user and not request.user.is_staff:
			return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
		serializer = TransactionSerializer(tx)
		return Response(serializer.data)