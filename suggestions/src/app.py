import sys
import os
import grpc
import random
from concurrent import futures

FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
proto_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/suggestions'))
sys.path.insert(0, proto_path)

import suggestions_pb2 as pb2
import suggestions_pb2_grpc as pb2_grpc

class SuggestionsService(pb2_grpc.SuggestionsServiceServicer):
    def __init__(self):
        self.books = [
            {"bookId": "101", "title": "The Great Gatsby", "author": "F. Scott Fitzgerald"},
            {"bookId": "102", "title": "1984", "author": "George Orwell"},
            {"bookId": "103", "title": "The Hobbit", "author": "J.R.R. Tolkien"},
            {"bookId": "104", "title": "Brave New World", "author": "Aldous Huxley"},
            {"bookId": "105", "title": "The Catcher in the Rye", "author": "J.D. Salinger"}
        ]

    def GetSuggestions(self, request, context):
        # Return a random sample based on request count
        sample_size = min(request.count, len(self.books))
        selected = random.sample(self.books, sample_size)
        
        book_objs = [pb2.Book(**b) for b in selected]
        return pb2.SuggestionResponse(books=book_objs)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_SuggestionsServiceServicer_to_server(SuggestionsService(), server)
    server.add_insecure_port("[::]:50053")
    server.start()
    print("Suggestions Service started on port 50053")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()