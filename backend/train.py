from utils.minilm_utils import train_model

if __name__ == "__main__":
    accuracy = train_model("labeled_emails.csv")
    
    print(f"\nTraining complete! Final validation accuracy: {accuracy:.2%}")
    print("Model artifacts saved to:")
    print("- status_classifier.joblib")
    print("- label_encoder.joblib")
