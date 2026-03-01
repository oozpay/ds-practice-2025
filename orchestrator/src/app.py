import sys
import os
import grpc
import logging
import json
from flask import Flask, request
from flask_cors import CORS
from concurrent.futures import ThreadPoolExecutor

# --- Configuration ---
# Set up logging to print to the console (stdout) for Docker to capture
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [Orchestrator] %(message)s'
)
logger = logging.getLogger(__name__)

# Paths for stubs
FILE = __file__ if '__file__()' in globals() else os.getenv("PYTHONFILE", "")
def get_proto_path(service):
    return os.path.abspath(os.path.join(FILE, f'../../../utils/pb/{service}'))

sys.path.insert(0, get_proto_path('fraud_detection'))
sys.path.insert(0, get_proto_path('transaction_verification'))
sys.path.insert(0, get_proto_path('suggestions'))

import fraud_detection_pb2 as fraud_pb
import fraud_detection_pb2_grpc as fraud_grpc
import transaction_verification_pb2 as verify_pb
import transaction_verification_pb2_grpc as verify_grpc
import suggestions_pb2 as suggest_pb
import suggestions_pb2_grpc as suggest_grpc

app = Flask(__name__)
CORS(app, resources={r'/*': {'origins': '*'}})

# --- gRPC Call Wrappers with Logging ---

def call_fraud_detection(card_number, amount):
    logger.info(f"Initiating Fraud Check | Card: {card_number[:4]}**** | Amount: {amount}")
    try:
        with grpc.insecure_channel('fraud_detection:50051') as channel:
            stub = fraud_grpc.FraudDetectionServiceStub(channel)
            response = stub.CheckFraud(fraud_pb.FraudRequest(card_number=card_number, order_amount=amount))
            logger.info(f"Fraud Check Result: {'FRAUD' if response.is_fraud else 'CLEAR'}")
            return response.is_fraud
    except Exception as e:
        logger.error(f"Fraud Detection Service unreachable: {e}")
        return True # Fail secure

def call_transaction_verification(data):
    logger.info("Initiating Transaction Verification...")
    try:
        with grpc.insecure_channel('transaction_verification:50052') as channel:
            stub = verify_grpc.TransactionVerificationServiceStub(channel)
            user = verify_pb.VerifyRequest.User(name=data['user']['name'], contact=data['user']['contact'])
            items = [verify_pb.VerifyRequest.Item(name=i['name'], quantity=i['quantity']) for i in data['items']]
            
            req = verify_pb.VerifyRequest(user=user, card_number=data['creditCard']['number'], items=items)
            response = stub.VerifyTransaction(req)
            logger.info(f"Transaction Verification Result: {'VALID' if response.is_valid else 'INVALID'} ({response.message})")
            return response.is_valid
    except Exception as e:
        logger.error(f"Verification Service unreachable: {e}")
        return False

def call_suggestions():
    logger.info("Fetching Book Suggestions...")
    try:
        with grpc.insecure_channel('suggestions:50053') as channel:
            stub = suggest_grpc.SuggestionsServiceStub(channel)
            response = stub.GetSuggestions(suggest_pb.SuggestionRequest(count=2))
            logger.info(f"Suggestions received: {len(response.books)} books found.")
            return [{"bookId": b.bookId, "title": b.title, "author": b.author} for b in response.books]
    except Exception as e:
        logger.error(f"Suggestions Service unreachable: {e}")
        return []

# --- Routes ---

@app.route('/checkout', methods=['POST'])
def checkout():
    request_data = json.loads(request.data)
    user_name = request_data.get('user', {}).get('name', 'Unknown')
    logger.info(f"--- Processing Checkout for User: {user_name} ---")
    
    card_info = request_data.get("creditCard", {})
    
    # Concurrent execution
    with ThreadPoolExecutor(max_workers=3) as executor:
        logger.info("Dispatching concurrent gRPC requests...")
        future_fraud = executor.submit(call_fraud_detection, card_info.get("number"), card_info.get("order_amount", 0.0))
        future_verify = executor.submit(call_transaction_verification, request_data)
        future_suggest = executor.submit(call_suggestions)

        is_fraud = future_fraud.result()
        is_valid = future_verify.result()
        suggestions = future_suggest.result()

    # Final Decision Logic
    approved = (not is_fraud) and is_valid
    order_id = 'ORD' + str(os.urandom(2).hex())
    
    status_str = 'APPROVED' if approved else 'DENIED'
    logger.info(f"Final Decision for {order_id}: {status_str}")
    
    return {
        'orderId': order_id,
        'status': 'Order Approved' if approved else 'Order Denied',
        'suggestedBooks': suggestions if approved else []
    }

if __name__ == '__main__':
    logger.info("Orchestrator starting up on port 5000...")
    app.run(host='0.0.0.0', port=5000)