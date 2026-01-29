import json
import numpy as np
import matplotlib.pyplot as plt
import base64
import pickle
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from scipy.spatial.distance import pdist, squareform
import os

# --- CONFIGURATION ---
METADATA_PATH = "employees_metadata.json"
PLOT_OUTPUT = "ai_health_check_tsne.png"
MIN_SAMPLES_PER_CLASS_FOR_PLOT = 3  # Only plot classes with at least N images
MAX_CLASSES_TO_PLOT = 20  # Limit colors to keep plot readable

def load_data():
    print(f"📂 Loading data from {METADATA_PATH}...")
    if not os.path.exists(METADATA_PATH):
        print(f"❌ File not found: {METADATA_PATH}")
        return None, None

    with open(METADATA_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    X = []
    y = []
    
    # Statistics
    class_counts = {}

    for emp_code, info in data.items():
        embeddings = info.get('embeddings', [])
        valid_embeddings = []
        
        for emb in embeddings:
            # Handle Base64+Pickle encoded numpy arrays (Legacy format)
            if isinstance(emb, str):
                try:
                    decoded = base64.b64decode(emb)
                    arr = pickle.loads(decoded)
                    valid_embeddings.append(arr)
                except Exception as e:
                    print(f"⚠️ Failed to decode embedding for {emp_code}: {e}")
                    continue
            # Handle list format (New standard)
            elif isinstance(emb, list):
                valid_embeddings.append(np.array(emb))
        
        if not valid_embeddings:
            continue
            
        class_counts[emp_code] = len(valid_embeddings)
        for emb in valid_embeddings:
            X.append(emb)
            y.append(emp_code)

    X = np.array(X)
    y = np.array(y)
    
    # Ensure X is float32
    if len(X) > 0:
        X = X.astype(np.float32)

    print(f"✅ Loaded {len(X)} vectors from {len(set(y))} identities.")
    return X, y, class_counts

def step_1_visualize_tsne(X, y, class_counts):
    print("\n🎨 STEP 1: Generative t-SNE Visualization...")
    
    # Filter top N classes for cleaner plot
    sorted_classes = sorted(class_counts.items(), key=lambda item: item[1], reverse=True)
    top_classes = [c[0] for c in sorted_classes[:MAX_CLASSES_TO_PLOT]]
    
    indices = [i for i, label in enumerate(y) if label in top_classes]
    X_subset = X[indices]
    y_subset = y[indices]
    
    print(f"   Plotting top {len(top_classes)} classes ({len(X_subset)} samples) to '{PLOT_OUTPUT}'...")

    # PCA first to reduce noise (Optional but recommended for high dim)
    pca = PCA(n_components=50)
    X_pca = pca.fit_transform(X_subset)
    
    # t-SNE
    tsne = TSNE(n_components=2, perplexity=min(30, len(X_subset) - 1), random_state=42)
    X_tsne = tsne.fit_transform(X_pca)

    # Plot
    plt.figure(figsize=(14, 10))
    unique_labels = np.unique(y_subset)
    colors = plt.cm.rainbow(np.linspace(0, 1, len(unique_labels)))

    for i, label in enumerate(unique_labels):
        mask = (y_subset == label)
        plt.scatter(X_tsne[mask, 0], X_tsne[mask, 1], label=label, alpha=0.7, s=60)
        
        # Add centroid label
        centroid = np.mean(X_tsne[mask], axis=0)
        plt.text(centroid[0], centroid[1], label, fontsize=8, fontweight='bold', 
                 bbox=dict(facecolor='white', alpha=0.6, edgecolor='none'))

    plt.title(f"t-SNE Visualization of Top {len(unique_labels)} Face Classes\n(Closer points = Similar Faces)", fontsize=16)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(PLOT_OUTPUT)
    print(f"✅ Saved t-SNE plot to {PLOT_OUTPUT}")

def step_2_benchmark_models(X, y):
    print("\n⚔️ STEP 2: Benchmarking SVM vs KNN...")
    
    # Filter classes with < 2 samples (required for stratification)
    unique, counts = np.unique(y, return_counts=True)
    valid_classes = unique[counts >= 2]
    mask = np.isin(y, valid_classes)
    
    X_filtered = X[mask]
    y_filtered = y[mask]
    
    print(f"   ℹ️ Filtered {len(X) - len(X_filtered)} samples (single-image classes). Remaining: {len(X_filtered)}")
    
    if len(X_filtered) < 5:
        print("   ❌ Not enough data for benchmark.")
        return

    # Split Data
    X_train, X_test, y_train, y_test = train_test_split(X_filtered, y_filtered, test_size=0.2, random_state=42, stratify=y_filtered)
    
    # 1. Train KNN (Baseline)
    knn = KNeighborsClassifier(n_neighbors=1, metric='euclidean')
    knn.fit(X_train, y_train)
    knn_acc = knn.score(X_test, y_test)
    print(f"   🔹 KNN Accuracy (k=1): {knn_acc*100:.2f}%")
    
    # 2. Train SVM (Current approach)
    svm = SVC(kernel='linear', probability=True, class_weight='balanced')
    svm.fit(X_train, y_train)
    svm_acc = svm.score(X_test, y_test)
    print(f"   🔹 SVM Accuracy (Linear): {svm_acc*100:.2f}%")
    
    # Analysis
    if abs(svm_acc - knn_acc) < 0.05 and svm_acc < 0.8:
        print("   ⚠️ CONCLUSION: Both models perform poorly. -> Likely DATA/FEATURE ISSUE (MobileNet).")
    elif knn_acc > svm_acc + 0.1:
        print("   ⚠️ CONCLUSION: KNN is much better. -> Likely SVM PARAMETER ISSUE.")
    else:
        print("   ✅ CONCLUSION: Models are performing comparably.")

def step_3_distance_analysis(X, y):
    print("\nmjlj STEP 3: Distance Analysis (Intra vs Inter class)...")
    
    intra_distances = []
    inter_distances = []
    
    # Sample random subset to avoid O(N^2) explosion if dataset is huge
    if len(X) > 1000:
        indices = np.random.choice(len(X), 1000, replace=False)
        X_sample = X[indices]
        y_sample = y[indices]
    else:
        X_sample = X
        y_sample = y

    dists = squareform(pdist(X_sample, metric='euclidean'))
    
    for i in range(len(X_sample)):
        for j in range(i + 1, len(X_sample)):
            d = dists[i, j]
            if y_sample[i] == y_sample[j]:
                intra_distances.append(d)
            else:
                inter_distances.append(d)
                
    avg_intra = np.mean(intra_distances) if intra_distances else 0
    avg_inter = np.mean(inter_distances) if inter_distances else 0
    
    print(f"   🔹 Avg Distance SAME person (Intra): {avg_intra:.4f} (Lower is better)")
    print(f"   🔹 Avg Distance DIFF people (Inter): {avg_inter:.4f} (Higher is better)")
    
    ratio = avg_intra / avg_inter if avg_inter > 0 else 0
    print(f"   🔹 Ratio (Intra/Inter): {ratio:.4f}")
    
    if ratio > 0.8:
        print("   ⚠️ WARNING: Clusters are very overlapping. embeddings are not discriminative enough!")
    elif ratio < 0.5:
        print("   ✅ GOOD: Clear separation between identities.")
    else:
        print("   ℹ️ OK: Acceptable separation.")

if __name__ == "__main__":
    import sys
    # Redirect stdout to a file to avoid encoding errors in Windows terminal
    with open("health_report.txt", "w", encoding="utf-8") as f:
        sys.stdout = f
        
        X, y, class_counts = load_data()
        if X is not None and len(X) > 0:
            step_1_visualize_tsne(X, y, class_counts)
            step_2_benchmark_models(X, y)
            step_3_distance_analysis(X, y)
            print("\n✅ Health Check Complete. Please open 'ai_health_check_tsne.png' to view clusters.")
    
    # Restore stdout
    sys.stdout = sys.__stdout__
    print("✅ Report written to health_report.txt")
