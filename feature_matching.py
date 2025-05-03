from keras_facenet import FaceNet
import numpy as np
import os
import cv2
import time
import re

embedder = FaceNet()

def extract_face_features(img_path):
    print(f"Processing image: {img_path}")
    img = cv2.imread(img_path)
    img = cv2.resize(img, (160, 160))  # FaceNet expects 160x160
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    print("Extracting facial features...")
    embeddings = embedder.embeddings([img])  # returns list of embeddings
    print("Feature extraction complete")
    return embeddings[0]

def get_all_criminal_features(criminal_folder='static/dataset/photos'):
    print(f"Loading criminal database from {criminal_folder}")
    features_db = {}
    total_files = len([f for f in os.listdir(criminal_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
    processed = 0

    start_time = time.time()
    print(f"Found {total_files} criminal images to process")

    for filename in os.listdir(criminal_folder):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            full_path = os.path.join(criminal_folder, filename)
            criminal_id = extract_id_from_filename(filename)
            print(f"Processing criminal ID: {criminal_id} ({processed+1}/{total_files})")
            features = extract_face_features(full_path)
            features_db[filename] = features
            processed += 1
            print(f"✓ Completed {processed}/{total_files} criminals ({processed/total_files*100:.1f}%)")

    elapsed = time.time() - start_time
    print(f"Database loading complete. Processed {processed} criminals in {elapsed:.2f} seconds")
    print(f"Average processing time per criminal: {elapsed/processed:.2f} seconds")
    return features_db

def extract_id_from_filename(filename):
    # Extract numeric ID from filename (e.g., "123.jpg" -> "123")
    match = re.search(r'(\d+)', filename)
    if match:
        return match.group(1)
    return "Unknown"

def find_best_matches(query_image_path, criminal_folder='static/dataset/photos', top_k=3):
    print(f"\n===== MATCHING PROCESS STARTED =====")
    print(f"Query image: {query_image_path}")

    print("\n[1/4] Extracting features from query image...")
    start_time = time.time()
    query_features = extract_face_features(query_image_path)
    print(f"✓ Query feature extraction completed in {time.time() - start_time:.2f} seconds")

    print("\n[2/4] Loading criminal database...")
    db_start_time = time.time()
    db_features = get_all_criminal_features(criminal_folder)
    print(f"✓ Database loading completed in {time.time() - db_start_time:.2f} seconds")

    print(f"\n[3/4] Comparing query with {len(db_features)} criminals...")
    compare_start_time = time.time()
    similarities = []
    total = len(db_features)

    for i, (filename, features) in enumerate(db_features.items()):
        if i % 10 == 0 or i == total - 1:
            print(f"Comparing {i+1}/{total} ({(i+1)/total*100:.1f}%)...")

        similarity = np.dot(query_features, features) / (np.linalg.norm(query_features) * np.linalg.norm(features))
        criminal_id = extract_id_from_filename(filename)
        similarities.append((filename, similarity, criminal_id))

    print(f"✓ Comparison completed in {time.time() - compare_start_time:.2f} seconds")

    print("\n[4/4] Sorting results...")
    similarities.sort(key=lambda x: x[1], reverse=True)
    top_matches = similarities[:top_k]

    print(f"\n===== MATCHING PROCESS COMPLETED =====")
    print(f"Found {len(top_matches)} potential matches out of {total} criminals")
    print("\nTOP MATCHES:")
    for i, (filename, similarity, criminal_id) in enumerate(top_matches):
        print(f"Match #{i+1}: Criminal ID {criminal_id} (Filename: {filename})")

    total_time = time.time() - start_time
    print(f"\nTotal processing time: {total_time:.2f} seconds")

    return top_matches
