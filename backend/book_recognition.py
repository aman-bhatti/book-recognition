import cv2
import os
import requests
import numpy as np

# Load the ORB detector algorithm with more features and a higher scale factor
orb = cv2.ORB_create(nfeatures=8000, scaleFactor=1.1, WTA_K=2)

# Dictionary to store book titles, ORB descriptors, and their metadata
book_features = {}

# Precompute ORB descriptors for each book cover
def load_book_covers(covers_folder="data/covers"):
    global book_features
    for book_name in os.listdir(covers_folder):
        book_path = os.path.join(covers_folder, book_name)
        if os.path.isdir(book_path):
            for cover_image in os.listdir(book_path):
                img_path = os.path.join(book_path, cover_image)
                img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                if img is not None:
                    keypoints, descriptors = orb.detectAndCompute(img, None)
                    if descriptors is not None:
                        book_features[book_name] = (keypoints, descriptors, img.shape)
                        print(f"Loaded descriptors for {book_name}")
                    else:
                        print(f"No descriptors found for {book_name}")
    print(f"Loaded book covers: {list(book_features.keys())}")


def fetch_book_details(book_title):
    api_url = f"https://www.googleapis.com/books/v1/volumes?q=intitle:{book_title}"
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            if "items" in data and len(data["items"]) > 0:
                book_data = data["items"][0]["volumeInfo"]
                title = book_data.get("title", "Unknown")
                author = ", ".join(book_data.get("authors", ["Unknown"]))
                genre = ", ".join(book_data.get("categories", ["Unknown"]))
                published_date = book_data.get("publishedDate", "Unknown")
                description = book_data.get("description", "No description available")  # Fetch the description

                return {
                    "title": title,
                    "author": author,
                    "genre": genre,
                    "year": published_date,
                    "description": description  # Add the description to the return
                }
            else:
                return None
        else:
            print(f"Error fetching book details: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching book details: {e}")
        return None


# Function to recognize a book based on the live camera frame
def recognize_book_cover(frame):
    # Convert the frame to grayscale
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    keypoints_frame, descriptors_frame = orb.detectAndCompute(gray_frame, None)

    if descriptors_frame is None or len(descriptors_frame) < 100:  # Minimum number of descriptors
        return "No book detected", None, (0, 0, 0, 0)

    # Cap the number of descriptors to avoid overwhelming the confidence score calculation
    if len(descriptors_frame) > 1000:  # Limit the number of keypoints to consider
        descriptors_frame = descriptors_frame[:1000]

    # Use BFMatcher to match features
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

    best_match = None
    best_matches_count = 0
    box_coords = (0, 0, 0, 0)
    confidence = 0  # Initialize confidence score

    # Compare live frame descriptors to each book cover's descriptors
    for book_name, (keypoints_book, descriptors_book, shape) in book_features.items():
        matches = bf.match(descriptors_book, descriptors_frame)
        good_matches = [m for m in matches if m.distance < 50]  # Filter for good matches

        if len(good_matches) > best_matches_count:
            best_matches_count = len(good_matches)
            best_match = book_name

            # Calculate bounding box coordinates based on keypoints matches
            h, w = shape
            scale_factor = 0.6
            w = int(w * scale_factor)
            h = int(h * scale_factor)

            for m in good_matches:
                x, y = keypoints_frame[m.trainIdx].pt
                box_coords = (int(x - w // 2), int(y - h // 2), w, h)

    # Adjusted confidence formula
    # Confidence based on both ratio of good matches to total descriptors and absolute good match count
    if len(descriptors_frame) > 0:
        confidence = (best_matches_count / len(descriptors_frame)) + (best_matches_count / 1000)  # Adjust as needed

    # Only return the recognized book if the number of good matches exceeds the threshold and confidence is reasonable
    if best_match and best_matches_count > 50 and confidence > 0.4:  # Adjust confidence threshold
        metadata = fetch_book_details(best_match)
        print(f"Recognized Book: {best_match} with {best_matches_count} good matches and confidence {confidence:.2f}")
        return best_match, metadata, box_coords
    else:
        print(f"No reliable match found. Matches: {best_matches_count}, Confidence: {confidence:.2f}")
        return "No book detected", None, (0, 0, 0, 0)


