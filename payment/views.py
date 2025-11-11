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
		print(f"[Initiate] Received initiate request from user={getattr(request, 'user', None)}")
		serializer = InitiatePaymentSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		data = serializer.validated_data
		print(f"[Initiate] Validated data: {data}")

		amount = data['amount']
		product_code = data.get('product_code', 'EPAYTEST')
		tx_uuid = data.get('transaction_uuid') or str(uuid.uuid4())
		success_url = data.get('success_url') or getattr(settings, 'ESEWA_SUCCESS_URL', 'https://furlink-backend.vercel.app/payment/success/')
		failure_url = data.get('failure_url') or getattr(settings, 'ESEWA_FAILURE_URL', 'https://furlink-backend.vercel.app/payment/failure/')

		transaction_defaults = {
			'user': request.user,
			'amount': amount,
			'currency': data.get('currency', 'NPR'),
			'status': Transaction.STATUS_PENDING,
		}

		transaction, created = Transaction.objects.get_or_create(tx_uuid=tx_uuid, defaults=transaction_defaults)
		print(f"[Initiate] get_or_create tx_uuid={tx_uuid} created={created}")
		# if transaction already existed, ensure we attach user/amount when appropriate
		if not created:
			updated = False
			if (not transaction.user) and request.user:
				transaction.user = request.user
				updated = True
			print(f"[Initiate] existing transaction before update: user={transaction.user} amount={transaction.amount}")
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
				print(f"[Initiate] updated transaction saved: user={transaction.user} amount={transaction.amount}")

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
		print(f"[Initiate] signature generated: {signature}")

		form_html = ''
		try:
			form_html = payment.generate_form()
		except Exception:
			form_html = ''

		transaction.signature = signature
		transaction.raw_response = {'form_html_present': bool(form_html)}
		transaction.save()
		print(f"[Initiate] transaction saved: id={transaction.id} signature_present={bool(signature)} form_html_len={len(form_html) if form_html else 0}")

		return Response({
			'tx_uuid': tx_uuid,
			'signature': signature,
			'form_html': form_html,
			'esewa_action': 'https://rc-epay.esewa.com.np/api/epay/main/v2/form',
		}, status=status.HTTP_201_CREATED)
		print(f"[Initiate] Responding with tx_uuid={tx_uuid}")


class EsewaCallbackAPIView(APIView):

	permission_classes = [AllowAny]

	def post(self, request):
		print(f"[Callback] Received callback request from {request.META.get('REMOTE_ADDR')}")
		payload = request.data.dict() if hasattr(request.data, 'dict') else request.data
		print(f"[Callback] Raw payload: {payload}")
		tx_uuid = payload.get('transaction_uuid') or payload.get('pid') or payload.get('oid')
		if not tx_uuid:
			return Response({'detail': 'transaction identifier (transaction_uuid/pid/oid) required'}, status=status.HTTP_400_BAD_REQUEST)

		tx = Transaction.objects.filter(tx_uuid=tx_uuid).first()
		if not tx:
			tx = Transaction.objects.create(tx_uuid=tx_uuid, amount=0, status=Transaction.STATUS_PENDING)
		print(f"[Callback] Loaded transaction: id={getattr(tx, 'id', None)} tx_uuid={tx.tx_uuid} user={getattr(tx, 'user', None)} status={tx.status}")

		# preserve previous status to avoid double-crediting
		previous_status = tx.status
		print(f"[Callback] previous_status={previous_status}")
		# store raw payload
		tx.raw_response = payload

		# determine new status
		# Treat several possible success markers from gateways (e.g. SUCCESS, COMPLETE)
		is_success = (
			str(payload.get('status', '')).upper() in ('SUCCESS', 'COMPLETE', 'COMPLETED')
			or payload.get('rid')
			or payload.get('refId')
		)
		print(f"[Callback] is_success evaluated as {is_success}")
		if is_success:
			tx.status = Transaction.STATUS_COMPLETED
			print("[Callback] Marking tx as COMPLETED")
		else:
				if payload.get('status') in ('FAILED', 'failed', 'ERROR'):
					tx.status = Transaction.STATUS_FAILED
					print("[Callback] Marking tx as FAILED")

		# If transaction just moved to completed, credit the user's account
		# Only credit if transaction moved to completed, hasn't been credited before,
		# and the transaction has an associated user (the initiator).
		if (
			tx.status == Transaction.STATUS_COMPLETED
			and previous_status != Transaction.STATUS_COMPLETED
			and not getattr(tx, 'credited', False)
			and tx.user
		):
			print(f"[Callback] Transaction eligible for crediting to user={tx.user}")
			# find amount to credit: prefer stored tx.amount, else try payload fields
			amount_to_credit = None
			if getattr(tx, 'amount', None) and Decimal(tx.amount) > Decimal('0'):
				amount_to_credit = Decimal(tx.amount)
				print(f"[Callback] Using stored transaction amount: {amount_to_credit}")
			else:
				# common eSewa field names: 'tAmt', 'amt', 'amount', 'total_amount'
				# include common amount keys like total_amount which some gateways send
				for key in ('tAmt', 'amt', 'amount', 'total_amount', 'totalAmount', 'tamount'):
					val = payload.get(key)
					if val:
						try:
							amount_to_credit = Decimal(str(val))
							print(f"[Callback] Found amount in payload key={key} value={val} parsed={amount_to_credit}")
							break
						except (InvalidOperation, TypeError, ValueError):
							print(f"[Callback] Failed to parse amount from payload key={key} value={val}")
							continue

			if amount_to_credit:
				account = getattr(tx.user, 'account', None)
				print(f"[Callback] amount_to_credit={amount_to_credit} account_found={bool(account)}")
				if account:
					try:
						account.topup(amount_to_credit)
						tx.raw_response = {**(tx.raw_response or {}), 'credited_amount': str(amount_to_credit)}
						tx.credited = True
						tx.save(update_fields=['raw_response', 'credited', 'updated_at'])
						print(f"[Callback] Credited amount {amount_to_credit} to user {tx.user}. Marked credited=True")
					except Exception as exc:
						print(f"[Callback] Error crediting account: {exc}")
						tx.raw_response = {**(tx.raw_response or {}), 'credit_error': str(exc)}
						print("[Callback] Recorded credit_error in tx.raw_response")

		tx.save()
		print(f"[Callback] Finished processing tx_uuid={tx.tx_uuid} status={tx.status} credited={tx.credited}")
		return Response({'detail': 'callback recorded', 'tx_uuid': tx.tx_uuid}, status=status.HTTP_200_OK)



class TransactionDetailAPIView(APIView):
	permission_classes = [IsAuthenticated]

	def get(self, request, tx_uuid):
		print(f"[TransactionDetail] GET called by user={request.user} for tx_uuid={tx_uuid}")
		tx = get_object_or_404(Transaction, tx_uuid=tx_uuid)
		if tx.user and tx.user != request.user and not request.user.is_staff:
			print(f"[TransactionDetail] Permission denied: tx.user={tx.user} request.user={request.user}")
			return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
		serializer = TransactionSerializer(tx)
		print(f"[TransactionDetail] Returning transaction id={tx.id} status={tx.status} credited={tx.credited}")
		return Response(serializer.data)