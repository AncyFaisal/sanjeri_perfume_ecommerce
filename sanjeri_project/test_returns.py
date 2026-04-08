import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sanjeri_project.settings')
django.setup()

from django.contrib.auth import get_user_model
from sanjeri_app.models import Order, OrderItem, Product, ProductVariant, Wallet, Coupon
from decimal import Decimal

User = get_user_model()

def run_test():
    print("Running return calculation test...")
    user = User.objects.first()
    admin = User.objects.filter(is_staff=True).first()
    
    if not user or not admin:
        print("Need a user and admin to test.")
        return

    # Ensure wallet exists
    wallet, _ = Wallet.objects.get_or_create(user=user)
    initial_wallet = wallet.balance
    
    product = Product.objects.first()
    variant = ProductVariant.objects.filter(product=product).first()
    if not variant:
        print("No variant found.")
        return
        
    initial_stock = variant.stock

    # Create dummy order
    order = Order.objects.create(
        user=user,
        order_number="TEST_RET_001",
        subtotal=Decimal('1000.00'),
        coupon_discount=Decimal('100.00'), # 10% overall discount
        discount_amount=Decimal('100.00'),
        total_amount=Decimal('900.00'),
        status='delivered',
        payment_status='completed'
    )
    
    # Create item with quantity 2
    item = OrderItem.objects.create(
        order=order,
        variant=variant,
        product_name="Test Product",
        variant_details="50ml",
        quantity=2,
        unit_price=Decimal('500.00'),
        total_price=Decimal('1000.00')
    )
    
    print(f"Created order with subtotal 1000 and coupon 100.")
    print(f"Item quantity: 2, total_price: 1000")
    
    # Request return for 1 quantity
    success, msg = item.request_item_return("Did not like it", quantity=1)
    print(f"Request Return (Qty=1): {success} - {msg}")
    
    item.refresh_from_db()
    print(f"Requested qty: {item.return_requested_quantity}")
    
    # Approve return
    success = item.approve_item_return(admin)
    print(f"Approve Return: {success}")
    
    item.refresh_from_db()
    wallet.refresh_from_db()
    variant.refresh_from_db()
    
    print(f"Returned qty: {item.returned_quantity}")
    print(f"Wallet balance change: {wallet.balance - initial_wallet} (Expected ~450.00)")
    print(f"Stock change: {variant.stock - initial_stock} (Expected 1)")

if __name__ == "__main__":
    run_test()
