import logging
from sys import exception
import joblib
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split

# Initialize logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Load the MiniLM model for text embedding
# This model converts email text into an embedding
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Initialize label encoder and classifier pipeline
# LabelEncoder converts text labels (eg. "rejected") to numeric values
# LogisticRegression is used for multi-class classification
label_encoder = LabelEncoder()
classifier = make_pipeline(
    # No preprocessing needed as we're using raw embeddings
    LogisticRegression(max_iter=1000, multi_class='multinomial')
)

def train_model(csv_path='data/labeled_emails.csv'):
    """
    Train classification model using labeled email data.
    
    Args:
        csv_path (str): Path to the CSV file containing training data.
        
    Returns:
        float: Validation accuracy of the trained model.
    """
    try:
        # Read CSV file with error handling
        df = pd.read_csv(csv_path, on_bad_lines='skip')
        
        # Log the first few rows and column names in DataFrame for debugging purposes
        logger.info(f"DataFrame head:\n{df.head()}")
        logger.info(f"DataFrame columns: {df.columns}")
        
        # Ensure the CSV contains the required columns
        required_columns = ['email_text', 'status_label']
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"Missing column: {col} from the CSV file.")

        # Extract email text and labels from the DataFrame
        texts = df['email_text'].values
        labels = label_encoder.fit_transform(df['status_label'])
        
        # Generate embeddings for each email text
        logger.info("Generating text embeddings...")
        embeddings = model.encode(texts, convert_to_numpy=True)
        
        # Split data into training and validation sets (80/20 split)
        X_train, X_test, y_train, y_test = train_test_split(
            embeddings, labels, test_size=0.2, random_state=42
        )
        
        # Train the logistic regression classifier
        logger.info("Training classifier...")
        classifier.fit(X_train, y_train)
        
        # Evaluate the model on training and validation data
        train_acc = classifier.score(X_train, y_train)
        test_acc = classifier.score(X_test, y_test)
        logger.info(f"Training accuracy: {train_acc:.2%}")
        logger.info(f"Validation accuracy: {test_acc:.2%}")
        
        # Save the trained model and label encoder for future use
        joblib.dump(classifier, 'status_classifier.joblib')
        joblib.dump(label_encoder, 'label_encoder.joblib')
        
        return test_acc
        
    except Exception as e:
        logger.error(f"Training failed: {str(e)}")
        raise

def process_email(email_text):
    """
    Predict application status from email text.
    
    Args:
        email_text (str): The content of the email to classify.
        
    Returns:
        dict: Predicted status label or error message.
    """
    try:
        global classifier, label_encoder

        # Generate an embedding for the input email text
        # The model converts the email into an embedding
        embedding = model.encode(email_text, convert_to_numpy=True)
        
        raise exception("This is a test exception")

        # Load the classifier and label encoder if they are not already loaded
        if not hasattr(classifier.steps[0][1], 'coef_'):
            classifier = joblib.load('status_classifier.joblib')
            label_encoder = joblib.load('label_encoder.joblib')
        
        # Predict the label using the trained classifier, logistic regression model
        # Should I use cosine similarity here instead?
        prediction = classifier.predict(embedding.reshape(1, -1))

        # Convert the numeric prediction back to a human-readable label
        decoded_label = label_encoder.inverse_transform(prediction)[0]
        
        logger.info(f"Predicted status: {decoded_label}")
        return {"application_status": decoded_label}
        
    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}")
        return {"error": str(e)}