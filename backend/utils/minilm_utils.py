import logging
from sentence_transformers import SentenceTransformer, util

# Initialize logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Load the MiniLM model
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Define the possible job application statuses
job_application_statuses = [
    "rejected",
    "no response",
    "request for availability",
    "interview scheduled",
    "offer",
]

# Define example sentences for each status
status_examples = {
    "rejected": ["We regret to inform you", "Unfortunately, we have decided"],
    "no response": [
        "Thank you for your application",
        "We have received your application",
    ],
    "request for availability": [
        "Please provide your availability",
        "Could you let us know your availability",
    ],
    "interview scheduled": [
        "Your interview is scheduled",
        "We have scheduled your interview",
    ],
    "offer": ["We are pleased to offer you", "Congratulations, you have been selected"],
}

# Encode the example sentences once and cache the embeddings
status_embeddings = {
    status: model.encode(examples, convert_to_tensor=True)
    for status, examples in status_examples.items()
}


def process_email(email_text):
    # Encode the email text
    email_embedding = model.encode(email_text, convert_to_tensor=True)

    # Find the best matching status
    best_status = None
    best_score = -1
    for status, embeddings in status_embeddings.items():
        # Compute cosine similarity
        cosine_scores = util.pytorch_cos_sim(email_embedding, embeddings)
        max_score = cosine_scores.max().item()
        if max_score > best_score:
            best_score = max_score
            best_status = status

    # Create the response JSON
    response_json = {"application_status": best_status}

    logger.info("Processed email: %s", response_json)
    return response_json
