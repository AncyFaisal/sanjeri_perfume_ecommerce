from django.db import models
from django.conf import settings
from .product import Product
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Avg

class ProductReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # One user can leave only one review per product
        unique_together = ('product', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return f"Review by {self.user.username} for {self.product.name} ({self.rating}/5)"

# Signals to automatically update product average rating and count
@receiver(post_save, sender=ProductReview)
@receiver(post_delete, sender=ProductReview)
def update_product_rating(sender, instance, **kwargs):
    product = instance.product
    reviews = product.reviews.all()
    
    if reviews.exists():
        product.rating_count = reviews.count()
        # Calculate the average rating and round to 2 decimal places
        avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
        product.avg_rating = round(avg_rating, 2)
    else:
        product.rating_count = 0
        product.avg_rating = 0.0
        
    product.save(update_fields=['rating_count', 'avg_rating'])
