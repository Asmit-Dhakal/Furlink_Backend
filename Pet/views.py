
from rest_framework import viewsets, permissions, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Pet, Adoption, Category, AdoptionPrice
from .serializers import (
    PetSerializer, AdoptionSerializer,
    CategorySerializer, AdoptionPriceSerializer
)
from decimal import Decimal
from rest_framework.exceptions import ValidationError
from django.db import transaction
 


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class PetViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Pet.objects.all()
    serializer_class = PetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
 
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        queryset =Pet.objects.all()
        user=self.request.user
        if user.is_authenticated:
            queryset=queryset.exclude(owner=user)
        return queryset

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def adopt(self, request, pk=None):
        pet = self.get_object()

        if not pet.is_available_for_adoption:
            return Response({'error': 'This pet has already been adopted.'}, status=400)

        days = int(pet.adoption_days or 1)
        if pet.custom_price is not None and days > 1:
            price = (Decimal(pet.custom_price) * Decimal(days)).quantize(Decimal('0.01'))
        else:
            price = pet.adoption_price

        if pet.owner == request.user:
            return Response({'error': 'You cannot adopt your own pet.'}, status=400)

        adopter_account = getattr(request.user, 'account', None)
        owner_account = getattr(pet.owner, 'account', None)

        if not adopter_account:
            return Response({'error': 'Adopter has no account.'}, status=400)
        if not owner_account:
            return Response({'error': 'Owner has no account to receive funds.'}, status=400)

        try:
            if not owner_account.can_charge(Decimal(price)):
                return Response({'error': 'Owner has insufficient funds to pay the adopter.'}, status=400)
        except Exception:
            return Response({'error': 'Unable to verify owner account balance.'}, status=400)

        try:
            with transaction.atomic():
                # charge owner and credit adopter
                owner_account.charge(Decimal(price))
                adopter_account.topup(Decimal(price))

                adoption = Adoption.objects.create(
                    pet=pet,
                    adopter=request.user,
                    is_confirmed=True,
                    price_paid=price,
                )

                pet.is_available_for_adoption = False
                pet.save()

        except Exception as exc:
            return Response({'error': f'Payment transfer failed: {str(exc)}'}, status=500)

        return Response(AdoptionSerializer(adoption).data, status=201)


class AdoptionViewSet(viewsets.ModelViewSet):
    queryset = Adoption.objects.all()
    serializer_class = AdoptionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class AdoptionPriceViewSet(viewsets.ModelViewSet):
    queryset = AdoptionPrice.objects.all()
    serializer_class = AdoptionPriceSerializer
    permission_classes = [permissions.IsAdminUser]

class MyPetViewSet(viewsets.ModelViewSet):
    serializer_class = PetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Pet.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        custom_price = serializer.validated_data.get('custom_price')
        category = serializer.validated_data.get('category')
        days_provided = 'adoption_days' in serializer.validated_data
        days = int(serializer.validated_data.get('adoption_days', 1) or 1)

        intent_to_list = False
        new_pet_price = Decimal('0.00')

        if custom_price is not None:
            intent_to_list = True
            new_pet_price = Decimal(custom_price)
        elif category is not None and days_provided:
            intent_to_list = True
            price_obj = AdoptionPrice.objects.filter(category=category).order_by('-created_at').first()
            if price_obj:
                new_pet_price = (price_obj.price * Decimal(days)).quantize(Decimal('0.01'))

        if intent_to_list: 
            account = getattr(self.request.user, 'account', None)
            # sum existing available pets' adoption_price
            existing_pets = Pet.objects.filter(owner=self.request.user, is_available_for_adoption=True)
            existing_sum = sum((p.adoption_price for p in existing_pets), Decimal('0.00'))
            required = (existing_sum + new_pet_price).quantize(Decimal('0.01'))
            if not account or not account.can_charge(required):
                raise ValidationError({
                    'detail': f'Insufficient account balance to list pet(s) for adoption. Required: {required} {serializer.validated_data.get("currency", "USD")}'
                })

        serializer.save(owner=self.request.user)

    def perform_update(self, serializer):
        pet = self.get_object()
        if pet.owner != self.request.user:
            raise permissions.PermissionDenied("You can only update your own pets.")
        will_be_available = serializer.validated_data.get('is_available_for_adoption', pet.is_available_for_adoption)
        if not pet.is_available_for_adoption and will_be_available:
            custom_price = serializer.validated_data.get('custom_price', pet.custom_price)
            days = int(serializer.validated_data.get('adoption_days', pet.adoption_days) or 1)
            category = serializer.validated_data.get('category', pet.category)

            if custom_price is not None:
                total = Decimal(custom_price)
            else:
                price_obj = (AdoptionPrice.objects.filter(category=category).order_by('-created_at').first()
                             if category else None)
                total = Decimal('0.00') if not price_obj else (price_obj.price * Decimal(days)).quantize(Decimal('0.01'))

            account = getattr(self.request.user, 'account', None)
            if not account or not account.can_charge(total):
                raise ValidationError({'detail': f'Insufficient account balance to list pet for adoption. Required: {total} {serializer.validated_data.get("currency", pet.currency)}'})

        serializer.save()

    def perform_destroy(self, instance):
        if instance.owner != self.request.user:
            raise permissions.PermissionDenied("You can only delete your own pets.")
        instance.delete()