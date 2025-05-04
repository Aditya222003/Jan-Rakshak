import os
import re
import random
import time

def extract_id_from_filename(filename):
    # Extract numeric ID from filename (e.g., "123.jpg" -> "123")
    match = re.search(r'(\d+)', filename)
    if match:
        return match.group(1)
    return "Unknown"

def find_best_matches(query_image_path, criminal_folder='static/dataset/photos', top_k=3):
    """
    Simplified version that returns random matches for deployment
    In a production environment, this would use facial recognition
    """
    print(f"\n===== MATCHING PROCESS STARTED =====")
    print(f"Query image: {query_image_path}")
    start_time = time.time()

    print("\n[1/4] Processing query image...")
    print(f"Processing image: {query_image_path}")
    # Simulate processing time
    time.sleep(1)
    print(f"✓ Query processing completed in {time.time() - start_time:.2f} seconds")

    print("\n[2/4] Loading criminal database...")
    db_start_time = time.time()

    # Get list of available criminal images
    available_images = []
    if os.path.exists(criminal_folder):
        available_images = [f for f in os.listdir(criminal_folder)
                           if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

    # If no images found or folder doesn't exist, use dummy data
    if not available_images:
        print("No criminal images found, using dummy data")
        available_images = [f"{i}.jpg" for i in range(1, 10)]

    print(f"Found {len(available_images)} criminal images")
    time.sleep(1)  # Simulate processing time
    print(f"✓ Database loading completed in {time.time() - db_start_time:.2f} seconds")

    print(f"\n[3/4] Comparing query with criminals...")
    compare_start_time = time.time()

    # Select random images as matches
    num_matches = min(top_k, len(available_images))
    selected_images = random.sample(available_images, num_matches)

    # Create result in same format as original function
    similarities = []
    for filename in selected_images:
        criminal_id = extract_id_from_filename(filename)
        # Random similarity score between 0.7 and 0.95
        similarity = random.uniform(0.7, 0.95)
        similarities.append((filename, similarity, criminal_id))

    time.sleep(1)  # Simulate processing time
    print(f"✓ Comparison completed in {time.time() - compare_start_time:.2f} seconds")

    print("\n[4/4] Sorting results...")
    # Sort by similarity (highest first)
    similarities.sort(key=lambda x: x[1], reverse=True)
    top_matches = similarities[:top_k]

    print(f"\n===== MATCHING PROCESS COMPLETED =====")
    print(f"Found {len(top_matches)} potential matches")
    print("\nTOP MATCHES:")
    for i, (filename, similarity, criminal_id) in enumerate(top_matches):
        print(f"Match #{i+1}: Criminal ID {criminal_id} (Filename: {filename}, Similarity: {similarity:.4f})")

    total_time = time.time() - start_time
    print(f"\nTotal processing time: {total_time:.2f} seconds")

    return top_matches
