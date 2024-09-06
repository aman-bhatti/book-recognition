import cv2
import tkinter as tk
from PIL import Image, ImageTk
from backend.book_recognition import recognize_book_cover, load_book_covers
import threading
import time

# This will store the result of the recognition
recognized_book = "No book detected"
metadata = None
box_coords = (0, 0, 0, 0)
last_recognition_time = 0
recognition_cooldown = 1.5  # seconds

# Book recognition thread function
def run_book_recognition(frame, book_info_label, metadata_label):
    global recognized_book, metadata, box_coords, last_recognition_time
    
    current_time = time.time()
    if current_time - last_recognition_time < recognition_cooldown:
        return  # Skip recognition if it's too soon

    recognized_book, metadata, box_coords = recognize_book_cover(frame)
    last_recognition_time = current_time

    # Update recognized book label and metadata in the main thread
    if recognized_book != "No book detected":
        book_info_label.config(text=f"Recognized Book: {recognized_book}")
        if metadata:
            details = f"Title: {metadata.get('title', 'Unknown')}\n"
            details += f"Author: {metadata.get('author', 'Unknown')}\n"
            details += f"Genre: {metadata.get('genre', 'Unknown')}\n"
            details += f"Year: {metadata.get('year', 'Unknown')}\n"
            details += f"Description: {metadata.get('description', 'Unknown')}"
            metadata_label.config(text=details)
        else:
            metadata_label.config(text="No details found via API")
    else:
        # Show "No book detected" and clear metadata
        book_info_label.config(text="No book detected")
        metadata_label.config(text="Please show a book cover to the camera")

def start_camera_stream(book_info_label, canvas, root, metadata_label):
    cam = cv2.VideoCapture(0)

    if not cam.isOpened():
        print("Error: Could not open camera.")
        return

    # Load book covers and metadata
    load_book_covers()

    frame_counter = 0
    recognition_thread = None

    def update_frame():
        nonlocal frame_counter, recognition_thread

        # Capture frame from camera
        ret, frame = cam.read()
        if not ret:
            print("Error: unable to capture camera feed")
            return

        small_frame = cv2.resize(frame, (640, 480))  # Increase the resolution


        # Every 30 frames, run recognition in a separate thread
        if frame_counter % 30 == 0 and (recognition_thread is None or not recognition_thread.is_alive()):
            recognition_thread = threading.Thread(target=run_book_recognition, args=(small_frame, book_info_label, metadata_label))
            recognition_thread.start()

        # Draw bounding box on recognized books
        if recognized_book != "No book detected":
            x, y, w, h = box_coords
            if w > 0 and h > 0:
                # Scale the box coordinates back to the original frame size
                x, y, w, h = x * 2, y * 2, w * 2, h * 2
                # Green box for recognized book
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Convert the frame to RGB for Tkinter
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_rgb = cv2.resize(img_rgb, (canvas.winfo_width(), canvas.winfo_height()))  # Resize to fit the canvas
        img = Image.fromarray(img_rgb)
        imgtk = ImageTk.PhotoImage(image=img)

        # Update the canvas with the live feed
        canvas.create_image(0, 0, anchor="nw", image=imgtk)
        canvas.image = imgtk  # Keep a reference to prevent garbage collection

        # Increment frame counter and call this function again after 20 milliseconds
        frame_counter += 1
        root.after(20, update_frame)

    # Start the frame update loop
    update_frame()

    # Make sure to release the camera when the window is closed
    root.protocol("WM_DELETE_WINDOW", lambda: (cam.release(), root.destroy()))