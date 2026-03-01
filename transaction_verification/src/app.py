import sys
import os
import grpc
from concurrent import futures

# Import stubs (adjusting path as per your project structure)
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
proto_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/transaction_verification'))
sys.path.insert(0, proto_path)

import transaction_verification_pb2 as pb2
import transaction_verification_pb2_grpc as pb2_grpc

class TransactionVerificationService(pb2_grpc.TransactionVerificationServiceServicer):
    def VerifyTransaction(self, request, context):
        is_valid = True
        message = "Valid"

        # Basic Logic: Check if items exist
        if not request.items:
            is_valid = False
            message = "Item list is empty"
        
        # Check if user data is complete
        elif not request.user.name or not request.user.contact:
            is_valid = False
            message = "User information missing"
        
        # Check credit card length (dummy check for 16 digits)
        elif len(request.card_number.replace(" ", "")) < 16:
            is_valid = False
            message = "Invalid credit card format"

        print(f"Verification result: {is_valid} - {message}")
        return pb2.VerifyResponse(is_valid=is_valid, message=message)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_TransactionVerificationServiceServicer_to_server(TransactionVerificationService(), server)
    server.add_insecure_port("[::]:50052")
    server.start()
    print("Transaction Verification Service started on port 50052")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()