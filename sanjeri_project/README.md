# Sanjeri Perfumes Ecommerce Platform ✨

Welcome to the **Sanjeri Perfumes** repository! This is a fully-featured, production-ready e-commerce platform built specifically for a premium perfume brand. It handles everything from intricate product variant mappings (volume, gender, stock) to integrated wallets, Razorpay checkout, and secure async email verification.

---

## 🚀 Key Features

* **Advanced Product Management:** Multi-variant inventory handling (e.g., 50ml, 100ml) with dynamic imagery and stock depletion logic.
* **Authentication & Security:** 
  * Custom User Model with email-based authentication.
  * Google OAuth2 integration for social logins.
  * Lightning-fast, asynchronous OTP email delivery powered by **Resend API**.
* **E-Commerce Essentials:**
  * Persistent Shopping Cart and Wishlist management.
  * Complex cart logic including dynamic discount calculations and coupon validation.
* **Payment & Wallet System:**
  * Fully integrated **Razorpay** checkout (Credit Card, UPI, Netbanking).
  * Built-in Customer Web Wallet for seamless processing of refunds and promotional credits.
* **Order Tracking & Returns:** User-facing dynamic order tracking, invoice generation, and an automated item-level return workflow.
* **Dynamic Offer Module:** Flexible discount system including targeted referral links and seasonal platform-wide sale toggles.

## 🛠️ Technology Stack

* **Backend:** Python + Django (v5+)
* **Database:** PostgreSQL (Production) / SQLite3 (Local)
* **Frontend:** HTML5, modern vanilla CSS, responsive Bootstrap architecture, dynamic JavaScript interactions
* **Server & Deployment:**
  * Nginx (Reverse Proxy & Static/Media Serving)
  * Gunicorn (WSGI Application Server)
  * Cloud Server VPS deployment
* **APIs & Tooling:** Razorpay API (Payments), Resend API (Emails), Pillow (Image Optimization)

## 💻 Local Setup & Installation

If you wish to run a local instance of the platform for development:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/AncyFaisal/sanjeri_perfume_ecommerce.git
   cd sanjeri_perfume_ecommerce/sanjeri_project
   ```

2. **Set up the virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Linux/Mac
   venv\Scripts\activate     # On Windows
   ```

3. **Install exact dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables:**
   Create a `.env` file in the same directory as `settings.py` and supply the required keys:
   ```env
   DEBUG=True
   SECRET_KEY=your_secret_key
   DB_NAME=your_db_name
   RESEND_API_KEY=your_resend_api_key
   DEFAULT_FROM_EMAIL=your_email@domain.com
   RAZORPAY_KEY_ID=your_razorpay_key
   RAZORPAY_KEY_SECRET=your_razorpay_secret
   SOCIAL_AUTH_GOOGLE_OAUTH2_KEY=your_google_key
   SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET=your_google_secret
   ```

5. **Database Setup & Run:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py runserver
   ```

## 🔒 Architecture Notes

This platform follows Django best practices:
* **Media Handling:** Media files (product images) are ignored via `.gitignore` to prevent repository bloat. In production, images are dynamically optimized on upload and served natively by Nginx rather than Gunicorn to drastically maximize speed.
* **Threaded Processes:** Network-bound API calls (like sending OTP emails) are handled securely in background `daemon` threads to prevent WSGI server timeouts (`504 Gateway errors`) and ensure instantaneous UI navigation.

---

*Prepared by Ancy Faisal.*
