import logging
import joblib
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Initialize model and components
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
label_encoder = LabelEncoder()
classifier = make_pipeline(
    # No preprocessing needed as we're using raw embeddings
    LogisticRegression(max_iter=1000, multi_class='multinomial')
)

def train_model(csv_path='data/labeled_emails.csv'):
    """Train classification model using labeled data"""
    try:
        # Read CSV file with error handling
        df = pd.read_csv(csv_path, on_bad_lines='skip')
        
        # Log the DataFrame to check its contents
        logger.info(f"DataFrame head:\n{df.head()}")
        logger.info(f"DataFrame columns: {df.columns}")
        
        # Ensure the 'status_label' column exists
        if 'status_label' not in df.columns:
            raise ValueError("The 'status_label' column is missing from the CSV file.")
        
        texts = df['email_text'].values
        labels = label_encoder.fit_transform(df['status_label'])
        
        # Generate embeddings
        logger.info("Generating text embeddings...")
        embeddings = model.encode(texts, convert_to_numpy=True)
        
        # Train/test split
        X_train, X_test, y_train, y_test = train_test_split(
            embeddings, labels, test_size=0.2, random_state=42
        )
        
        # Train classifier
        logger.info("Training classifier...")
        classifier.fit(X_train, y_train)
        
        # Evaluate
        train_acc = classifier.score(X_train, y_train)
        test_acc = classifier.score(X_test, y_test)
        logger.info(f"Training accuracy: {train_acc:.2%}")
        logger.info(f"Validation accuracy: {test_acc:.2%}")
        
        # Save artifacts
        joblib.dump(classifier, 'status_classifier.joblib')
        joblib.dump(label_encoder, 'label_encoder.joblib')
        
        return test_acc
        
    except Exception as e:
        logger.error(f"Training failed: {str(e)}")
        raise

def process_email(email_text):
    """Predict application status from email text"""
    try:
        global classifier, label_encoder
        # Generate embedding
        embedding = model.encode(email_text, convert_to_numpy=True)
        
        # Load artifacts if not already loaded
        if not hasattr(classifier.steps[0][1], 'coef_'):
            classifier = joblib.load('status_classifier.joblib')
            label_encoder = joblib.load('label_encoder.joblib')
        
        # Predict
        prediction = classifier.predict(embedding.reshape(1, -1))
        decoded_label = label_encoder.inverse_transform(prediction)[0]
        
        logger.info(f"Predicted status: {decoded_label}")
        return {"application_status": decoded_label}
        
    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}")
        return {"error": str(e)}