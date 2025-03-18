from utils.minilm_utils import train_model

if __name__ == "__main__":
    # Path to your labeled CSV file
    csv_path = "labeled_emails.csv"  
    
    # Train and get accuracy
    accuracy = train_model(csv_path)
    
    print(f"\nTraining complete! Final validation accuracy: {accuracy:.2%}")
    print("Model artifacts saved to:")
    print("- status_classifier.joblib")
    print("- label_encoder.joblib")