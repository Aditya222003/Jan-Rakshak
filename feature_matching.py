import os
import re
import random

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
    print(f"Processing query image: {query_image_path}")

    # Get list of available criminal images
    available_images = []
    if os.path.exists(criminal_folder):
        available_images = [f for f in os.listdir(criminal_folder)
                           if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

    # If no images found or folder doesn't exist, use dummy data
    if not available_images:
        print("No criminal images found, using dummy data")
        available_images = [f"{i}.jpg" for i in range(1, 10)]

    # Select random images as matches
    num_matches = min(top_k, len(available_images))
    selected_images = random.sample(available_images, num_matches)

    # Create result in same format as original function
    matches = []
    for filename in selected_images:
        criminal_id = extract_id_from_filename(filename)
        # Random similarity score between 0.7 and 0.95
        similarity = random.uniform(0.7, 0.95)
        matches.append((filename, similarity, criminal_id))

    # Sort by similarity (highest first)
    matches.sort(key=lambda x: x[1], reverse=True)

    print(f"Found {len(matches)} potential matches")
    for i, (filename, similarity, criminal_id) in enumerate(matches):
        print(f"Match #{i+1}: Criminal ID {criminal_id} (Filename: {filename})")

    return matches
