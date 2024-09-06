import os
import stripe

stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

def get_stripe_publishable_key():
    return os.environ.get('STRIPE_PUBLISHABLE_KEY')

def create_stripe_checkout_session(product):
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': product.name,
                },
                'unit_amount': int(product.price * 100),
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=url_for('marketplace', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=url_for('marketplace', _external=True),
    )
    return session
