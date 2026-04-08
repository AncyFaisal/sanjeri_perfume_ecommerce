import re
import traceback

try:
    with open('d:/first_project/sanjeri_perfume/sanjeri_project/templates/homepage.html', 'r', encoding='utf-8') as f:
        html = f.read()

    js_search = r'''if \(isInWishlist\) \{\s*icon\.className = \'fas fa-heart\';\s*icon\.style\.color = \'#dc3545\';\s*button\.classList\.add\(\'in-wishlist\'\);\s*\}'''
    js_replace = r'''if (isInWishlist) {
                            icon.className = 'fas fa-heart text-danger';
                            icon.style.color = '#dc3545';
                            button.classList.add('in-wishlist');
                            localStorage.setItem(`wishlist_${productId}`, 'true');
                        } else {
                            icon.className = 'far fa-heart';
                            icon.style.color = '';
                            button.classList.remove('in-wishlist');
                            localStorage.removeItem(`wishlist_${productId}`);
                        }'''
    html = re.sub(js_search, js_replace, html)

    card_html = r'''<div class="product-item position-relative">
              <!-- Volume Badge -->
              <span class="badge bg-info variant-badge">
                {{ variant.volume_ml }}ml
              </span>

              <!-- Wishlist Button -->
              {% include 'includes/wishlist_button.html' with product=variant.product is_in_wishlist=variant.product.is_in_wishlist %}

              <figure class="text-center mb-2">
                <a href="{% url 'product_detail' variant.product.id %}" title="{{ variant.product.name }}">
                  {% if variant.variant_image %}
                    <img src="{{ variant.variant_image.url }}" class="img-fluid product-img-sm" alt="{{ variant.product.name }} - {{ variant.volume_ml }}ml" style="height: 180px; width: 100%; object-fit: cover; border-radius: 4px;">
                  {% elif variant.product.main_image %}
                    <img src="{{ variant.product.main_image.url }}" class="img-fluid product-img-sm" alt="{{ variant.product.name }} - {{ variant.volume_ml }}ml" style="height: 180px; width: 100%; object-fit: cover; border-radius: 4px;">
                  {% else %}
                    <div class="image-placeholder" style="height: 180px; width: 100%; background: #f8f9fa; display: flex; align-items: center; justify-content: center; color: #6c757d; border-radius: 4px;">
                      <div class="text-center">
                        <i class="fas fa-perfume-bottle fa-3x text-muted mb-2"></i>
                        <p class="small text-muted">No Image</p>
                      </div>
                    </div>
                  {% endif %}
                </a>
              </figure>
              
              <div class="product-card-body-sm" style="padding: 12px; text-align: left;">
                <h4 class="product-title-sm" style="font-size: 0.95rem; font-weight: 600; color: var(--primary-color); margin-bottom: 6px; line-height: 1.3; height: 2.6em; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;">{{ variant.product.name }}</h4>
                
                <div class="product-details-sm mb-1" style="margin-bottom: 6px;">
                  <span class="product-type-sm text-muted" style="font-size: 0.8rem;">
                    {{ variant.product.fragrance_type|default:"Eau de Parfum" }}
                  </span>
                </div>
                
                <div class="product-rating-sm mb-1" style="display: flex; align-items: center; margin-bottom: 6px;">
                  <div class="star-rating-sm" style="color: #ffc107; margin-right: 4px; font-size: 0.8rem;">
                    {% if variant.product.avg_rating %}
                      {% for i in "12345" %}
                        {% if forloop.counter <= variant.product.avg_rating %}
                          <i class="fas fa-star"></i>
                        {% elif forloop.counter|add:"-0.5" <= variant.product.avg_rating %}
                          <i class="fas fa-star-half-alt"></i>
                        {% else %}
                          <i class="far fa-star"></i>
                        {% endif %}
                      {% endfor %}
                    {% else %}
                      <i class="fas fa-star"></i>
                      <i class="fas fa-star"></i>
                      <i class="fas fa-star"></i>
                      <i class="fas fa-star"></i>
                      <i class="fas fa-star-half-alt"></i>
                    {% endif %}
                  </div>
                  <span class="rating-count-sm" style="font-size: 0.75rem; color: #6c757d;">({{ variant.product.rating_count|default:"4.2" }})</span>
                </div>

                <!-- Price Section with Offer -->
                <div class="price-section-sm mb-1" style="margin-bottom: 4px;">
                    {% with best_offer=variant.product|get_best_offer %}
                        {% if best_offer %}
                            {% with discount=variant.price|get_offer_discount:variant.product %}
                                {% with offer_price=variant.price|subtract:discount %}
                                    <div class="d-flex align-items-center flex-wrap">
                                        <span class="current-price-sm fw-bold text-danger" style="font-size: 1rem;">₹{{ offer_price|floatformat:0 }}</span>
                                        <small class="text-muted ms-2 text-decoration-line-through">₹{{ variant.price|floatformat:0 }}</small>
                                        <span class="badge bg-danger ms-2">{{ best_offer.discount_percentage }}% OFF</span>
                                    </div>
                                {% endwith %}
                            {% endwith %}
                        {% elif variant.discount_price and variant.discount_price < variant.price %}
                            <div class="d-flex align-items-center flex-wrap">
                                <span class="current-price-sm fw-bold" style="font-size: 1rem; color: var(--primary-color);">₹{{ variant.discount_price|floatformat:0 }}</span>
                                <small class="text-muted ms-2 text-decoration-line-through">₹{{ variant.price|floatformat:0 }}</small>
                                {% with discount_amount=variant.price|subtract:variant.discount_price %}
                                  {% with discount_percent=discount_amount|divide:variant.price|multiply:100 %}
                                    <span class="badge bg-success ms-2">{{ discount_percent|floatformat:0 }}% OFF</span>
                                  {% endwith %}
                                {% endwith %}
                            </div>
                        {% else %}
                            <span class="current-price-sm fw-bold" style="font-size: 1rem; color: var(--primary-color);">₹{{ variant.price|floatformat:0 }}</span>
                        {% endif %}
                    {% endwith %}
                    <small class="text-muted d-block" style="font-size: 0.75rem; margin-top: 4px;">{{ variant.gender }} • SKU: {{ variant.sku }}</small>
                </div>

                <div class="stock-status-sm mb-2" style="font-size: 0.75rem;">
                  {% if variant.stock > 10 %}
                    <span class="badge bg-success small"><i class="fas fa-check me-1"></i>In Stock ({{ variant.stock }})</span>
                  {% elif variant.stock > 0 %}
                    <span class="badge bg-warning small"><i class="fas fa-exclamation me-1"></i>Only {{ variant.stock }} left</span>
                  {% else %}
                    <span class="badge bg-danger small"><i class="fas fa-times me-1"></i>Out of Stock</span>
                  {% endif %}
                </div>

                <div class="d-flex justify-content-center mt-2">
                  {% if variant.stock > 0 %}
                    <button class="btn btn-add-cart-sm add-to-cart-btn" 
                      data-variant-id="{{ variant.id }}"
                      data-product-id="{{ variant.product.id }}" style="background-color: maroon; color: white; border: none; border-radius: 20px; padding: 5px 12px; font-size: 0.8rem; width: 100%;">
                      <i class="fas fa-shopping-cart me-1"></i> Add to Cart
                    </button>
                  {% else %}
                    <button class="btn btn-secondary btn-sm" disabled style="width: 100%; border-radius: 20px;">
                      <i class="fas fa-times me-1"></i> Out of Stock
                    </button>
                  {% endif %}
                </div>
              </div>
            </div>'''
            
    for name in ["featured_products", "mens_products", "womens_products", "unisex_products"]:
        pattern = re.compile(rf"\{{% for product in {name} %}}(.*?)\{{% empty %}}", re.DOTALL)
        old_html = html
        html = pattern.sub(f"{{% for variant in {name} %}}\n            <div class=\"swiper-slide\">\n              {card_html}\n            </div>\n            {{% empty %}}", html)
        if html == old_html:
            print(f"Failed to match {name}")
            
    with open('d:/first_project/sanjeri_perfume/sanjeri_project/templates/homepage.html', 'w', encoding='utf-8') as f:
        f.write(html)
        
    print("Done patching.")
except Exception as e:
    traceback.print_exc()
