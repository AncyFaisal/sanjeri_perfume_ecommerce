# import os
# import django

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sanjeri_project.settings')
# django.setup()

# from sanjeri_app.models import Product, ProductVariant, ProductImage

# print('=== Checking Current Image Paths ===')
# print()

# # Check Product main images
# products = Product.objects.all()
# print('Product Main Images:')
# for product in products:
#     if product.main_image:
#         print(f'  {product.name}: {product.main_image.name}')
# print()

# # Check ProductVariant images
# variants = ProductVariant.objects.all()
# print('Product Variant Images:')
# for variant in variants:
#     if variant.variant_image:
#         print(f'  {variant.product.name} - {variant.volume_ml}ml: {variant.variant_image.name}')
# print()

# # Check ProductImage gallery
# gallery = ProductImage.objects.all()
# print('Product Gallery Images:')
# for img in gallery:
#     print(f'  {img.product.name}: {img.image.name}')
# print()

# # Check what files actually exist in media/
# print('Files in media/products/:')
# if os.path.exists('media/products/'):
#     files = os.listdir('media/products/')[:10]
#     for f in files:
#         print(f'  {f}')
# else:
#     print('  media/products/ folder does not exist')
# test_razorpay_debug.py
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sanjeri_project.settings')
django.setup()

import razorpay
from django.conf import settings

print("="*60)
print("RAZORPAY DEBUG CHECK")
print("="*60)

# 1. Check keys
print("\n1. Checking Razorpay Keys:")
print(f"   Key ID: {settings.RAZORPAY_KEY_ID}")
print(f"   Key ID valid: {'rzp_test' in str(settings.RAZORPAY_KEY_ID)}")
print(f"   Key Secret exists: {bool(settings.RAZORPAY_KEY_SECRET)}")

# 2. Test connection
try:
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    
    # Test creating order
    order = client.order.create({
        "amount": 10000,  # ₹100
        "currency": "INR",
        "payment_capture": "1",
        "receipt": "DEBUG_001"
    })
    
    print("\n2. Razorpay Connection: ✅ SUCCESS")
    print(f"   Order ID: {order['id']}")
    print(f"   Amount: {order['amount']} paise")
    print(f"   Status: {order['status']}")
    
except Exception as e:
    print(f"\n2. Razorpay Connection: ❌ FAILED")
    print(f"   Error: {e}")

# 3. Check wallet model
from sanjeri_app.models.wallet import Wallet, WalletTransaction
from django.contrib.auth import get_user_model

User = get_user_model()
try:
    user = User.objects.first()
    print(f"\n3. User Check: ✅ Found {user.email if user else 'No user'}")
    
    wallet, created = Wallet.objects.get_or_create(user=user)
    print(f"   Wallet: ID={wallet.id}, Balance=₹{wallet.balance}")
    
    # Check transactions
    txn_count = WalletTransaction.objects.filter(wallet=wallet).count()
    print(f"   Transactions: {txn_count}")
    
except Exception as e:
    print(f"\n3. User/Wallet Check: ❌ FAILED")
    print(f"   Error: {e}")

print("\n" + "="*60)



