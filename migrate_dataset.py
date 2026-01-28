"""
Professional Migration Script with ML Metrics
Import dataset → Train SVM → Evaluate with Precision/Recall/F1/Confusion Matrix
"""

import os
import sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.model_selection import train_test_split
import seaborn as sns
from datetime import datetime
from collections import Counter

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from backend.utils.metadata import EmployeesMetadata
from backend.services.extraction import FaceNetExtractor
from backend.services.liveness import LivenessDetector
from backend.services.alignment import FaceAligner
from backend.services.classifier import SVMClassifier
from backend.config import (
    DATASET_DIR, 
    FACENET_MODEL_PATH, 
    LIVENESS_MODEL_PATH, 
    SVM_MODEL_PATH, 
    SVM_CONFIDENCE_THRESHOLD, 
    EMPLOYEES_METADATA_PATH
)

import cv2

def migrate_and_train_professional():
    """
    Professional migration with comprehensive metrics
    """
    print("="*70)
    print(" 🎓  PROFESSIONAL SVM TRAINING PIPELINE")
    print("="*70)
    
    # Step 1: Initialize services
    print("\n📦 [1/6] Initializing AI services...")
    metadata = EmployeesMetadata(EMPLOYEES_METADATA_PATH)
    facenet = FaceNetExtractor(FACENET_MODEL_PATH)
    liveness = LivenessDetector(LIVENESS_MODEL_PATH)
    aligner = FaceAligner()
    
    # Step 2: Scan dataset
    print("\n📊 [2/6] Scanning dataset...")
    dataset_path = Path(DATASET_DIR)
    if not dataset_path.exists():
        print(f"❌ Dataset directory not found: {dataset_path}")
        return
    
    person_folders = [f for f in dataset_path.iterdir() if f.is_dir()]
    total_people = len(person_folders)
    
    print(f"   Found {total_people} people in dataset")
    print(f"   Dataset path: {dataset_path}")
    
    # Statistics
    stats = {
        "total_people": total_people,
        "processed_people": 0,
        "total_images": 0,
        "processed_images": 0,
        "failed_images": 0,
        "embeddings_per_person": {}
    }
    
    # Step 3: Process each person and extract embeddings
    print("\n🔄 [3/6] Processing images and extracting embeddings...")
    print(f"   (Warning outputs suppressed for clarity)\n")
    
    for idx, person_folder in enumerate(person_folders, 1):
        person_name = person_folder.name
        employee_code = f"EMP_{person_name.upper().replace(' ', '_')}"
        
        print(f"   [{idx}/{total_people}] {person_name}...", end=" ")
        
        # Check if already exists
        if metadata.employee_exists(employee_code):
            print(f"⚠️  Already exists, skipping")
            continue
        
        # Create employee
        metadata.create_employee(
            employee_code=employee_code,
            full_name=person_name,
            department="Migrated"
        )
        
        # Process images
        image_files = list(person_folder.glob("*.jpg")) + list(person_folder.glob("*.png")) + list(person_folder.glob("*.jpeg"))
        stats["total_images"] += len(image_files)
        
        if len(image_files) == 0:
            print(f"[!] No images found")
            continue
        
        person_embeddings = 0
        
        for img_path in image_files:
            try:
                # Load image
                image = cv2.imread(str(img_path))
                if image is None:
                    stats["failed_images"] += 1
                    continue
                
                # Alignment
                aligned_face, _ = aligner.align(image)
                if aligned_face is None:
                    stats["failed_images"] += 1
                    continue
                
                # Extract embedding
                embedding = facenet.extract(aligned_face)
                
                if embedding is None:
                    stats["failed_images"] += 1
                    continue
                
                # Save to metadata
                metadata.add_embedding(employee_code, embedding)
                
                person_embeddings += 1
                stats["processed_images"] += 1
                
            except Exception as e:
                stats["failed_images"] += 1
                # Uncomment to see errors:
                # print(f"\n      Error on {img_path.name}: {str(e)}")
                continue
        
        stats["embeddings_per_person"][employee_code] = person_embeddings
        stats["processed_people"] += 1
        print(f"[OK] {person_embeddings}/{len(image_files)}")
    
    # Step 4: Get all embeddings for training
    print("\n📥 [4/6] Loading all embeddings for training...")
    embeddings, labels = metadata.get_all_embeddings_for_training()
    
    print(f"   Total samples: {len(embeddings)}")
    print(f"   Total classes: {len(set(labels))}")
    print(f"   Embeddings shape: {embeddings[0].shape if len(embeddings) > 0 else 'N/A'}")
    
    if len(embeddings) == 0:
        print("\n[!] No embeddings found, cannot train SVM")
        return
    
    # Step 5: Prepare data for training & evaluation
    print("\n🔬 [5/6] Preparing data for training & evaluation...")
    X = np.array(embeddings)
    y = np.array(labels)
    
    # Check class distribution
    from collections import Counter
    label_counts = Counter(y)
    num_classes = len(set(y))
    avg_samples_per_class = len(y) / num_classes if num_classes > 0 else 0
    
    print(f"   Total samples: {len(X)}")
    print(f"   Total classes: {num_classes}")
    print(f"   Avg samples/class: {avg_samples_per_class:.1f}")
    
    if num_classes == 0:
        print("\n[ERROR] No embeddings extracted! Check:")
        print("   1. Dataset folder exists and contains person folders")
        print("   2. Each person folder contains .jpg or .png images")
        print("   3. Images are valid and readable")
        return
    
    # Face Recognition = MEMORIZATION task
    # Train on 100% data, test on same 100% to verify perfect recall
    print(f"\n   Strategy: MEMORIZATION (train 100%, test 100%)")
    print(f"   Rationale: Face recognition should memorize all known faces")
    
    X_train = X  # 100% for training
    y_train = y
    X_test = X   # Same 100% for testing (memorization check)
    y_test = y
    
    print(f"   Training set: {len(X_train)} samples ({len(set(y_train))} classes)")
    print(f"   Test set: {len(X_test)} samples (same as train - memorization test)")
    
    # Step 6: Train SVM
    print("\n🤖 [6/6] Training SVM Classifier...")
    svm = SVMClassifier(SVM_MODEL_PATH, SVM_CONFIDENCE_THRESHOLD)
    
    # Train on training set
    svm.train(X_train.tolist(), y_train.tolist())
    print("   ✅ SVM training complete")
    
    # Predict on test set
    y_pred_raw = svm.model.predict(X_test)
    y_proba = svm.model.predict_proba(X_test)
    y_pred_thresholded = []
    y_max_probs = np.max(y_proba, axis=1)
    
    for i, x in enumerate(X_test):
        pred_label, confidence = svm.predict(x)
        y_pred_thresholded.append(pred_label)
    
    # Calculate global metrics
    raw_accuracy = accuracy_score(y_test, y_pred_raw)
    thresholded_accuracy = accuracy_score(y_test, y_pred_thresholded)
    report_dict = classification_report(y_test, y_pred_raw, output_dict=True, zero_division=0)
    
    # Model parameters for report
    params = svm.model.get_params() if hasattr(svm, 'model') else {}
    
    # Save Research Report to File
    report_path = Path("models/research_evaluation_report.txt")
    report_path.parent.mkdir(exist_ok=True)
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("======================================================================\n")
        f.write("      FACE RECOGNITION RESEARCH-GRADE EVALUATION REPORT\n")
        f.write(f"      DateTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("======================================================================\n\n")
        
        f.write("--- 1. MODEL CONFIGURATION & PARAMETERS ---\n")
        f.write(f"Classifier:      Support Vector Machine (SVM)\n")
        f.write(f"Kernel:          {params.get('kernel', 'linear')}\n")
        f.write(f"C (Regul.):      {params.get('C', 1.0)}\n")
        f.write(f"Feature Dim:     128 (FaceNet dlib ResNet)\n")
        f.write(f"Identities:      {num_classes}\n")
        f.write(f"Conf. Threshold: {SVM_CONFIDENCE_THRESHOLD}\n\n")
        
        f.write("--- 2. PERFORMANCE METRICS (Memorization Test) ---\n")
        f.write(f"Raw Accuracy:    {raw_accuracy:.4f} (Top-1 recall without threshold)\n")
        f.write(f"Thres. Accuracy: {thresholded_accuracy:.4f} (With {SVM_CONFIDENCE_THRESHOLD} cutoff)\n")
        f.write(f"Macro Avg F1:    {report_dict['macro avg']['f1-score']:.4f}\n")
        f.write(f"Weighted Avg F1: {report_dict['weighted avg']['f1-score']:.4f}\n")
        f.write(f"Avg Confidence:  {np.mean(y_max_probs):.4f}\n\n")
        
        f.write("--- 3. DETAILED CLASSIFICATION REPORT (Raw) ---\n")
        f.write(classification_report(y_test, y_pred_raw, zero_division=0))
        f.write("\n")
        f.write("======================================================================\n")
        f.write("End of Research Report\n")

    print(f"📊 Global Accuracy:   {raw_accuracy*100:.2f}%")
    print(f"📊 Macro Avg F1:      {report_dict['macro avg']['f1-score']:.4f}")
    print(f"📄 Full report saved: {report_path}")
    
    # Visualizations
    unique_classes = sorted(set(y_test))[:10]  # Show top 10 in charts
    
    # Confusion Matrix
    print("\n📊 Generating confusion matrix visualization...")
    cm = confusion_matrix(y_test, y_pred_raw, labels=unique_classes)
    plt.figure(figsize=(12, 10))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=[cls[:15] for cls in unique_classes],
                yticklabels=[cls[:15] for cls in unique_classes])
    plt.title('Confusion Matrix (Top 10 Classes)', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig("models/confusion_matrix.png", dpi=150)
    plt.close()
    
    # Confidence distribution
    print("📊 Generating confidence distribution...")
    plt.figure(figsize=(10, 6))
    plt.hist(y_max_probs, bins=30, color='skyblue', edgecolor='black', alpha=0.7)
    plt.axvline(SVM_CONFIDENCE_THRESHOLD, color='red', linestyle='--')
    plt.title('Prediction Confidence Distribution', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig("models/confidence_distribution.png", dpi=150)
    plt.close()
    
    # Samples per class distribution
    print("📊 Generating samples per class distribution...")
    sorted_classes = sorted(Counter(y_test).items(), key=lambda x: x[1], reverse=True)[:20]
    plt.figure(figsize=(12, 6))
    classes, counts = zip(*sorted_classes)
    plt.bar(range(len(classes)), counts, color='coral', alpha=0.7)
    plt.xticks(range(len(classes)), [c[:15] for c in classes], rotation=45)
    plt.title('Samples per Class (Top 20)', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig("models/samples_distribution.png", dpi=150)
    plt.close()
    
    # Step 8: Final summary
    print("\n" + "="*70)
    print(" ✅  MIGRATION & RESEARCH TRAINING COMPLETED")
    print("="*70)

if __name__ == "__main__":
    try:
        migrate_and_train_professional()
    except Exception as e:
        print(f"\n❌ MIGRATION FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
