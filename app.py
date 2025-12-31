"""
Perplexity AI + PayPal Instant Checkout POC
Similar to OpenAI + Stripe implementation
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from datetime import datetime
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

# API Configuration
PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY')
PAYPAL_CLIENT_ID = os.getenv('PAYPAL_CLIENT_ID')
PAYPAL_CLIENT_SECRET = os.getenv('PAYPAL_CLIENT_SECRET')
PAYPAL_MODE = os.getenv('PAYPAL_MODE', 'sandbox')  # 'sandbox' or 'live'

# PayPal API Base URLs
PAYPAL_API_BASE = {
    'sandbox': 'https://api-m.sandbox.paypal.com',
    'live': 'https://api-m.paypal.com'
}

# Product Catalog
PRODUCTS = {
    'gc_25': {
        'id': 'gc_25',
        'name': '$25 Gift Card',
        'description': 'Perfect for small purchases',
        'price': 25.00,
        'currency': 'USD'
    },
    'gc_50': {
        'id': 'gc_50',
        'name': '$50 Gift Card',
        'description': 'Most popular choice',
        'price': 50.00,
        'currency': 'USD'
    },
    'gc_100': {
        'id': 'gc_100',
        'name': '$100 Gift Card',
        'description': 'Best value for frequent shoppers',
        'price': 100.00,
        'currency': 'USD'
    }
}

# Store conversation history per session
conversations = {}

# Tool definitions for Perplexity function calling
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_gift_cards",
            "description": "Get a list of available gift cards with prices and descriptions. Call this when user asks what gift cards are available.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_paypal_checkout",
            "description": "Create a PayPal checkout session for purchasing a gift card. ONLY use the product_id parameter. Available product IDs are: gc_25 (for $25 card), gc_50 (for $50 card), gc_100 (for $100 card). Do NOT invent other parameters.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {
                        "type": "string",
                        "description": "The product ID - must be exactly one of: 'gc_25', 'gc_50', or 'gc_100'",
                        "enum": ["gc_25", "gc_50", "gc_100"]
                    }
                },
                "required": ["product_id"]
            }
        }
    }
]

def get_paypal_access_token():
    """Get PayPal OAuth access token"""
    url = f"{PAYPAL_API_BASE[PAYPAL_MODE]}/v1/oauth2/token"
    
    print(f"\n{'='*60}")
    print(f"🔐 Getting PayPal Access Token")
    print(f"{'='*60}")
    print(f"🌍 PayPal Mode: {PAYPAL_MODE}")
    print(f"🔗 Token URL: {url}")
    print(f"👤 Client ID: {PAYPAL_CLIENT_ID[:20]}...")
    
    headers = {
        "Accept": "application/json",
        "Accept-Language": "en_US",
    }
    data = {"grant_type": "client_credentials"}
    
    response = requests.post(
        url,
        headers=headers,
        data=data,
        auth=(PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET)
    )
    
    print(f"📥 Response Status: {response.status_code}")
    
    if response.status_code == 200:
        token = response.json()['access_token']
        print(f"✅ Access Token Received: {token[:30]}...")
        print(f"{'='*60}\n")
        return token
    else:
        error_msg = f"Failed to get PayPal token: {response.text}"
        print(f"❌ {error_msg}")
        print(f"{'='*60}\n")
        raise Exception(error_msg)

def list_gift_cards():
    """Function to list available gift cards"""
    return json.dumps({
        "products": list(PRODUCTS.values())
    })

def create_paypal_checkout(product_id):
    """Create PayPal order for instant checkout"""
    print(f"\n{'='*60}")
    print(f"🛒 Creating PayPal checkout for product: {product_id}")
    print(f"{'='*60}")
    
    try:
        if product_id not in PRODUCTS:
            error_msg = f"Invalid product ID: {product_id}"
            print(f"❌ {error_msg}")
            return json.dumps({"error": error_msg})
        
        product = PRODUCTS[product_id]
        print(f"✅ Product found: {product['name']} - ${product['price']}")
        
        access_token = get_paypal_access_token()
        
        api_base = PAYPAL_API_BASE[PAYPAL_MODE]
        url = f"{api_base}/v2/checkout/orders"
        
        print(f"\n{'~'*60}")
        print(f"📦 Creating PayPal Order")
        print(f"{'~'*60}")
        print(f"🌐 API Base URL: {api_base}")
        print(f"🔗 Full API URL: {url}")
        print(f"💰 Amount: ${product['price']} {product['currency']}")
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        
        order_data = {
            "intent": "CAPTURE",
            "purchase_units": [{
                "reference_id": product_id,
                "description": product['description'],
                "amount": {
                    "currency_code": product['currency'],
                    "value": str(product['price'])
                },
                "custom_id": f"gift_card_{datetime.now().timestamp()}"
            }],
            "application_context": {
                "brand_name": "Gift Card Store",
                "landing_page": "NO_PREFERENCE",
                "user_action": "PAY_NOW",
                "return_url": "http://localhost:3000/success",
                "cancel_url": "http://localhost:3000/cancel"
            }
        }
        
        print(f"📤 Sending order to PayPal...")
        response = requests.post(url, headers=headers, json=order_data)
        
        print(f"\n{'*'*60}")
        print(f"📥 PayPal Response")
        print(f"{'*'*60}")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 201:
            order = response.json()
            print(f"✅ Order Created Successfully!")
            print(f"Order ID: {order['id']}")
            print(f"\nAvailable Links:")
            for link in order['links']:
                print(f"  - {link['rel']}: {link['href']}")
            
            # Get approval URL
            approval_url = next(
                link['href'] for link in order['links'] 
                if link['rel'] == 'approve'
            )
            
            result = {
                "success": True,
                "checkout_url": approval_url,
                "order_id": order['id']
            }
            
            print(f"\n{'🎯'*30}")
            print(f"🔗 CHECKOUT URL TO USE:")
            print(f"{'🎯'*30}")
            print(f"{approval_url}")
            print(f"{'🎯'*30}")
            
            # Verify it's a sandbox URL
            if PAYPAL_MODE == 'sandbox' and 'sandbox.paypal.com' not in approval_url:
                print(f"\n⚠️  WARNING: URL does not contain 'sandbox'!")
                print(f"Expected: https://www.sandbox.paypal.com/...")
                print(f"Got: {approval_url}")
            elif PAYPAL_MODE == 'sandbox' and 'sandbox.paypal.com' in approval_url:
                print(f"\n✅ Correct! This is a SANDBOX URL")
            
            print(f"{'='*60}\n")
            
            return json.dumps(result)
        else:
            error_msg = f"PayPal API error ({response.status_code}): {response.text}"
            print(f"❌ {error_msg}")
            print(f"Response Body: {response.text}")
            print(f"{'='*60}\n")
            return json.dumps({"error": error_msg})
            
    except Exception as e:
        error_msg = f"Exception: {str(e)}"
        print(f"❌ {error_msg}")
        print(f"{'='*60}\n")
        return json.dumps({"error": error_msg})

# Function mapping
FUNCTION_MAP = {
    "list_gift_cards": list_gift_cards,
    "create_paypal_checkout": create_paypal_checkout
}

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages with Perplexity AI"""
    data = request.json
    user_message = data.get('message', '')
    session_id = data.get('session_id', 'default')
    
    # Initialize or get conversation history
    if session_id not in conversations:
        conversations[session_id] = []
    
    # Add user message to history
    conversations[session_id].append({
        "role": "user",
        "content": user_message
    })
    
    try:
        # Call Perplexity API with function calling
        headers = {
            "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "sonar-pro",
            "messages": [
                {
                    "role": "system",
                    "content": """You are a helpful gift card sales assistant for our Gift Card Store.

AVAILABLE PRODUCTS:
- gc_25: $25 Gift Card ($25.00 USD)
- gc_50: $50 Gift Card ($50.00 USD)  
- gc_100: $100 Gift Card ($100.00 USD)

CRITICAL INSTRUCTIONS:
1. When user asks what's available, use the list_gift_cards function
2. When user wants to buy ANY gift card, you MUST immediately call the create_paypal_checkout function
3. DO NOT just talk about calling the function - ACTUALLY CALL IT
4. Use ONLY the product_id parameter with values: gc_25, gc_50, or gc_100
5. After the function returns a checkout URL, tell user to click the button

Example correct behavior:
User: "I want the $50 card"
You: [CALL create_paypal_checkout function with product_id="gc_50"]
Then: "Great! Please click the PayPal button below to complete your purchase."

DO NOT output JSON in your response. Just call the function directly."""
                }
            ] + conversations[session_id],
            "tools": TOOLS,
            "tool_choice": "auto",
            "temperature": 0.1
        }
        
        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers=headers,
            json=payload
        )
        
        if response.status_code != 200:
            return jsonify({
                "error": f"Perplexity API error: {response.text}"
            }), 500
        
        response_data = response.json()
        assistant_message = response_data['choices'][0]['message']
        
        print(f"\n{'📨'*30}")
        print(f"AI Response received")
        print(f"{'📨'*30}")
        print(f"Has tool_calls: {bool(assistant_message.get('tool_calls'))}")
        print(f"Content: {assistant_message.get('content', '')[:200]}")
        print(f"{'📨'*30}\n")
        
        # Initialize checkout_url
        checkout_url = None
        
        # Check if function calling is needed
        if assistant_message.get('tool_calls'):
            tool_call = assistant_message['tool_calls'][0]
            function_name = tool_call['function']['name']
            
            print(f"\n{'⚙️ '*30}")
            print(f"🔧 Function Call Detected")
            print(f"{'⚙️ '*30}")
            print(f"Function: {function_name}")
            print(f"Raw arguments: {tool_call['function']['arguments']}")
            
            try:
                function_args = json.loads(tool_call['function']['arguments'])
                print(f"Parsed arguments: {function_args}")
            except json.JSONDecodeError as e:
                print(f"❌ Failed to parse arguments: {e}")
                return jsonify({"error": "Invalid function arguments from AI"}), 500
            
            # Validate arguments for create_paypal_checkout
            if function_name == 'create_paypal_checkout':
                if 'product_id' not in function_args:
                    print(f"❌ Missing required parameter: product_id")
                    print(f"⚠️  AI tried to use wrong parameters!")
                    
                    # Try to map common mistakes
                    if 'amount' in function_args or 'product' in function_args:
                        # Try to infer the correct product_id
                        amount = function_args.get('amount', 0)
                        if amount >= 90:
                            function_args = {'product_id': 'gc_100'}
                        elif amount >= 40:
                            function_args = {'product_id': 'gc_50'}
                        else:
                            function_args = {'product_id': 'gc_25'}
                        print(f"🔄 Auto-corrected to: {function_args}")
                    else:
                        return jsonify({
                            "error": "AI used wrong function parameters. Please try again.",
                            "response": "I apologize, there was an error. Please tell me which gift card you'd like: $25, $50, or $100?"
                        }), 200
            
            print(f"✅ Calling function with: {function_args}")
            print(f"{'⚙️ '*30}\n")
            
            # Execute function
            function_response = FUNCTION_MAP[function_name](**function_args)
            print(f"✅ Function response: {function_response}")
            
            # Add function call and response to history
            conversations[session_id].append(assistant_message)
            conversations[session_id].append({
                "role": "tool",
                "tool_call_id": tool_call['id'],
                "content": function_response
            })
            
            # Get final response from Perplexity
            payload['messages'] = [
                {
                    "role": "system",
                    "content": """You are a helpful gift card sales assistant. You can:
1. Show available gift cards when asked
2. Help users purchase gift cards by creating PayPal checkout sessions
3. Answer questions about the products

IMPORTANT: When you receive a checkout URL from the create_paypal_checkout function,
you MUST include that EXACT URL in your response. Do not modify it or create your own URL.
Tell the user to click the PayPal button that will appear below your message.

Be friendly and guide users through the purchase process."""
                }
            ] + conversations[session_id]
            
            response = requests.post(
                "https://api.perplexity.ai/chat/completions",
                headers=headers,
                json=payload
            )
            
            if response.status_code != 200:
                return jsonify({
                    "error": f"Perplexity API error: {response.text}"
                }), 500
            
            response_data = response.json()
            assistant_message = response_data['choices'][0]['message']
            
            # Parse the function response to extract checkout URL
            function_result = json.loads(function_response)
            checkout_url = function_result.get('checkout_url')
            print(f"🔗 Checkout URL extracted: {checkout_url}")
        else:
            # Fallback: Parse text response for product mentions
            print(f"\n⚠️  No tool_calls detected. Trying text parsing fallback...")
            content = assistant_message.get('content', '').lower()
            
            # Check if user wants to buy and which product
            if 'gc_50' in content or '$50' in content or '50' in content:
                print(f"💡 Detected $50 gift card request in text")
                function_response = create_paypal_checkout('gc_50')
                function_result = json.loads(function_response)
                checkout_url = function_result.get('checkout_url')
            elif 'gc_100' in content or '$100' in content or '100' in content:
                print(f"💡 Detected $100 gift card request in text")
                function_response = create_paypal_checkout('gc_100')
                function_result = json.loads(function_response)
                checkout_url = function_result.get('checkout_url')
            elif 'gc_25' in content or '$25' in content or '25' in content:
                print(f"💡 Detected $25 gift card request in text")
                function_response = create_paypal_checkout('gc_25')
                function_result = json.loads(function_response)
                checkout_url = function_result.get('checkout_url')
            else:
                print(f"❌ Could not detect product selection")
                checkout_url = None
        
        return jsonify({
            "response": assistant_message['content'],
            "checkout_url": checkout_url,
            "session_id": session_id
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/capture-payment', methods=['POST'])
def capture_payment():
    """Capture PayPal payment after user approval"""
    data = request.json
    order_id = data.get('order_id')
    
    try:
        access_token = get_paypal_access_token()
        
        url = f"{PAYPAL_API_BASE[PAYPAL_MODE]}/v2/checkout/orders/{order_id}/capture"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        
        response = requests.post(url, headers=headers)
        
        if response.status_code in [200, 201]:
            capture_data = response.json()
            
            # TODO: Save order to database
            # TODO: Generate and send gift card code
            # TODO: Send confirmation email
            
            return jsonify({
                "success": True,
                "order_id": order_id,
                "status": capture_data['status']
            })
        else:
            return jsonify({
                "error": f"Capture failed: {response.text}"
            }), 400
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "paypal_mode": PAYPAL_MODE
    })

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🔍 Checking Environment Variables...")
    print("="*60)
    
    # Check if .env file exists
    import os.path
    env_file_exists = os.path.isfile('.env')
    print(f"📄 .env file exists: {'✅ Yes' if env_file_exists else '❌ No'}")
    
    if env_file_exists:
        print(f"📍 .env file location: {os.path.abspath('.env')}")
    
    # Validate API keys
    errors = []
    
    if not PERPLEXITY_API_KEY:
        errors.append("PERPLEXITY_API_KEY")
        print("❌ PERPLEXITY_API_KEY: Not found")
    else:
        print(f"✅ PERPLEXITY_API_KEY: Found ({PERPLEXITY_API_KEY[:10]}...)")
    
    if not PAYPAL_CLIENT_ID:
        errors.append("PAYPAL_CLIENT_ID")
        print("❌ PAYPAL_CLIENT_ID: Not found")
    else:
        print(f"✅ PAYPAL_CLIENT_ID: Found ({PAYPAL_CLIENT_ID[:15]}...)")
    
    if not PAYPAL_CLIENT_SECRET:
        errors.append("PAYPAL_CLIENT_SECRET")
        print("❌ PAYPAL_CLIENT_SECRET: Not found")
    else:
        print(f"✅ PAYPAL_CLIENT_SECRET: Found ({PAYPAL_CLIENT_SECRET[:10]}...)")
    
    print(f"✅ PAYPAL_MODE: {PAYPAL_MODE}")
    
    if errors:
        print("\n" + "="*60)
        print("❌ ERROR: Missing environment variables:")
        for err in errors:
            print(f"   - {err}")
        print("\nPlease add them to your .env file:")
        print("="*60)
        print("\nExample .env file content:")
        print("-" * 60)
        print("PERPLEXITY_API_KEY=pplx-your-key-here")
        print("PAYPAL_CLIENT_ID=your-client-id")
        print("PAYPAL_CLIENT_SECRET=your-secret")
        print("PAYPAL_MODE=sandbox")
        print("-" * 60)
        exit(1)
    
    print("="*60)
    print("✅ All environment variables loaded successfully!")
    print("🚀 Starting Flask server...")
    print("="*60 + "\n")
    
    app.run(debug=True, port=5000)