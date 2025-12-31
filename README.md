# 🎁 Gift Card Store - Perplexity AI + PayPal POC

A proof-of-concept conversational commerce application that combines **Perplexity AI** for natural language interactions with **PayPal** for secure instant checkout.

## 🌟 Features

- 💬 **AI-Powered Shopping Assistant** - Natural conversation flow using Perplexity AI
- 💳 **Instant PayPal Checkout** - Secure payment processing with PayPal Orders API
- 🎯 **Function Calling with Fallback** - Robust implementation with text parsing backup
- 🛍️ **Gift Card Catalog** - Multiple denominations ($25, $50, $100)
- 📱 **Responsive UI** - Clean, modern chat interface
- 🔐 **Sandbox Ready** - Test mode for safe development

## 🏗️ Architecture

```
User → Frontend (HTML/JS) → Backend (Flask) → Perplexity AI
                                ↓
                           PayPal API → Checkout
```

## 📋 Prerequisites

- Python 3.7+
- Perplexity API Key
- PayPal Developer Account (Sandbox)

## 🚀 Quick Start

### 1. Clone or Download the Project

```bash
# Your project structure should look like:
perplexity-paypal-poc/
├── app.py           # Flask backend
├── index.html       # Frontend interface
├── .env            # Environment variables (create this)
├── .gitignore      # Git ignore file
└── README.md       # This file
```

### 2. Install Dependencies

```bash
pip install flask flask-cors requests python-dotenv
```

### 3. Get API Keys

#### **Perplexity API Key**
1. Visit: https://www.perplexity.ai/settings/api
2. Sign in or create an account
3. Generate a new API key
4. Copy the key (starts with `pplx-`)

#### **PayPal Sandbox Credentials**
1. Visit: https://developer.paypal.com/dashboard/
2. Sign in with your PayPal account
3. Go to **"Apps & Credentials"** tab
4. Ensure you're on **"Sandbox"** mode
5. Create a new app or use the default one
6. Copy the **Client ID** and **Secret**

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Perplexity API Configuration
PERPLEXITY_API_KEY=pplx-your-actual-key-here

# PayPal API Configuration
PAYPAL_CLIENT_ID=your-paypal-client-id-here
PAYPAL_CLIENT_SECRET=your-paypal-client-secret-here
PAYPAL_MODE=sandbox

# Optional: Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
```

### 5. Run the Backend

```bash
python3 app.py
```

You should see:
```
============================================================
🔍 Checking Environment Variables...
============================================================
✅ PERPLEXITY_API_KEY: Found
✅ PAYPAL_CLIENT_ID: Found
✅ PAYPAL_CLIENT_SECRET: Found
✅ PAYPAL_MODE: sandbox
============================================================
✅ All environment variables loaded successfully!
🚀 Starting Flask server...
============================================================
```

### 6. Open the Frontend

Open `index.html` in your browser, or serve it with:

```bash
# Option 1: Direct file
open index.html

# Option 2: Simple HTTP server
python3 -m http.server 3000
# Then visit: http://localhost:3000
```

## 💬 Usage

### Sample Conversations

**Browsing Products:**
```
You: What gift cards do you have?
AI: We have $25, $50, and $100 gift cards available...
```

**Making a Purchase:**
```
You: I want to buy a $50 gift card
AI: Great! I'll create the PayPal checkout...
[PayPal Button Appears]
```

**Quick Purchase:**
```
You: Give me the $100 one
AI: Perfect choice! Click the button below...
[PayPal Button Appears]
```

## 🧪 Testing PayPal Payments

### Create Test Accounts

1. Go to: https://developer.paypal.com/dashboard/accounts
2. You'll see auto-generated sandbox accounts:
   - **Business Account** (seller)
   - **Personal Account** (buyer)
3. Click "View/Edit Account" to see credentials

### Test the Flow

1. Click the PayPal button in the chat
2. You'll be redirected to PayPal sandbox
3. Login with your **sandbox buyer account**
4. Complete the payment (no real money!)
5. You'll be redirected back to the success page

### Sandbox Test Cards

PayPal sandbox provides test accounts with virtual funds. No credit cards needed!

## 📁 Project Structure

```
.
├── app.py                 # Flask backend server
│   ├── API endpoints
│   ├── Perplexity AI integration
│   ├── PayPal API integration
│   └── Function calling logic
│
├── index.html            # Frontend chat interface
│   ├── Chat UI components
│   ├── Message handling
│   └── PayPal button rendering
│
├── .env                  # Environment variables (DO NOT COMMIT)
├── .gitignore           # Git ignore rules
└── README.md            # This documentation
```

## 🔌 API Endpoints

### `POST /chat`
Handle chat messages and AI interactions

**Request:**
```json
{
  "message": "I want to buy a $50 gift card",
  "session_id": "session_123"
}
```

**Response:**
```json
{
  "response": "Great! Click the PayPal button below...",
  "checkout_url": "https://www.sandbox.paypal.com/checkoutnow?token=...",
  "session_id": "session_123"
}
```

### `POST /capture-payment`
Capture completed PayPal payment

**Request:**
```json
{
  "order_id": "8JU12345678901234"
}
```

**Response:**
```json
{
  "success": true,
  "order_id": "8JU12345678901234",
  "status": "COMPLETED"
}
```

### `GET /health`
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "paypal_mode": "sandbox"
}
```

## 🛠️ Configuration

### Product Catalog

Edit the `PRODUCTS` dictionary in `app.py`:

```python
PRODUCTS = {
    'gc_25': {
        'id': 'gc_25',
        'name': '$25 Gift Card',
        'description': 'Perfect for small purchases',
        'price': 25.00,
        'currency': 'USD'
    },
    # Add more products...
}
```

### PayPal Settings

- **Sandbox Mode**: `PAYPAL_MODE=sandbox` (for testing)
- **Live Mode**: `PAYPAL_MODE=live` (for production - requires live credentials)

### Return URLs

Update in `app.py` → `create_paypal_checkout()`:

```python
"return_url": "http://localhost:3000/success",
"cancel_url": "http://localhost:3000/cancel"
```

## 🐛 Troubleshooting

### Issue: "PERPLEXITY_API_KEY not found"

**Solution:**
- Ensure `.env` file exists in the same directory as `app.py`
- Check there are no spaces around `=` in `.env`
- Verify `python-dotenv` is installed: `pip install python-dotenv`

### Issue: PayPal button not appearing

**Solution:**
- Check browser console (F12) for errors
- Verify terminal logs show "Checkout URL extracted"
- Ensure text parsing fallback is detecting the product

### Issue: PayPal checkout URL not working

**Solution:**
- Verify `PAYPAL_MODE=sandbox` in `.env`
- Check terminal logs show `sandbox.paypal.com` in the URL
- Ensure you're using sandbox credentials, not live ones

### Issue: "Invalid model" error

**Solution:**
- Model name may have changed
- Current valid model: `sonar-pro`
- Check Perplexity docs: https://docs.perplexity.ai/

### Issue: CORS errors in browser

**Solution:**
- Flask-CORS is enabled by default
- If serving frontend from different port, check CORS settings
- Try serving both from same origin

## 🔒 Security Notes

### ⚠️ Important for Production

1. **Never commit `.env` file** - It contains sensitive API keys
2. **Use environment variables** - Not hardcoded secrets
3. **Enable HTTPS** - Required for production PayPal
4. **Validate all inputs** - Sanitize user data
5. **Implement rate limiting** - Prevent API abuse
6. **Add authentication** - Protect user data
7. **Use live PayPal carefully** - Sandbox first, then live

### `.gitignore` Template

```
# Environment variables
.env
.env.local

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/

# IDE
.vscode/
.idea/
*.swp
```

## 🚀 Deployment

### Switch to Production

1. Get **live** PayPal credentials from https://developer.paypal.com/
2. Update `.env`:
   ```bash
   PAYPAL_MODE=live
   PAYPAL_CLIENT_ID=your-live-client-id
   PAYPAL_CLIENT_SECRET=your-live-secret
   ```
3. Update return URLs to your production domain
4. Enable HTTPS (required by PayPal)
5. Test thoroughly in sandbox first!

### Hosting Options

- **Backend**: Heroku, Railway, Render, AWS, DigitalOcean
- **Frontend**: Netlify, Vercel, GitHub Pages, Cloudflare Pages

## 📈 Next Steps

### Recommended Enhancements

- [ ] **Database Integration** - Store orders (PostgreSQL, MongoDB)
- [ ] **Email Notifications** - Send order confirmations (SendGrid, AWS SES)
- [ ] **Gift Card Generation** - Create unique codes
- [ ] **User Authentication** - Login/signup system
- [ ] **Admin Dashboard** - View and manage orders
- [ ] **PayPal Webhooks** - Real-time payment notifications
- [ ] **Order History** - Track past purchases
- [ ] **Receipt Generation** - PDF receipts
- [ ] **Analytics** - Track conversion rates
- [ ] **Multi-currency Support** - International payments

## 📚 Resources

### Documentation

- [Perplexity API Docs](https://docs.perplexity.ai/)
- [PayPal Orders API](https://developer.paypal.com/docs/api/orders/v2/)
- [PayPal Sandbox Guide](https://developer.paypal.com/docs/api-basics/sandbox/)
- [Flask Documentation](https://flask.palletsprojects.com/)

### Support

- **Perplexity**: https://www.perplexity.ai/support
- **PayPal Developer**: https://developer.paypal.com/support
- **Flask**: https://flask.palletsprojects.com/support/

## 🤝 Contributing

This is a POC (Proof of Concept) project. Feel free to:

- Fork and modify for your needs
- Report issues
- Suggest improvements
- Share feedback

## ⚖️ License

This is a demonstration project. Use at your own discretion.

## 🙏 Acknowledgments

- Built with **Perplexity AI** (Sonar models)
- Powered by **PayPal** payment processing
- UI inspired by modern chat interfaces

---

**Built with ❤️ as a POC for conversational commerce**

*Last Updated: December 2024*