import cv2
import tkinter as tk
from PIL import Image, ImageTk
from backend.book_recognition import recognize_book_cover, load_book_covers

def start_camera_stream(book_info_label, canvas, root, metadata_label):
    cam = cv2.VideoCapture(0)

    if not cam.isOpened():
        print("Error: Could not open camera.")
        return

    # Load book covers and metadata
    load_book_covers()

    frame_counter = 0  # To control the frequency of book recognition

    def update_frame():
        nonlocal frame_counter
        # Capture frame from camera
        ret, frame = cam.read()
        if not ret:
            print("Error: unable to capture camera feed")
            return

        # Convert the frame to RGB for Tkinter
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_rgb = cv2.resize(img_rgb, (canvas.winfo_width(), canvas.winfo_height()))  # Resize to fit the canvas
        img = Image.fromarray(img_rgb)
        imgtk = ImageTk.PhotoImage(image=img)

        # Update the canvas with the live feed
        canvas.create_image(0, 0, anchor="nw", image=imgtk)
        canvas.image = imgtk  # Keep a reference to prevent garbage collection

        # Run the recognition every 15 frames (~ twice per second)
        if frame_counter % 15 == 0:
            # Run the recognition on the frame
            recognized_book, metadata, box_coords = recognize_book_cover(frame)

            # If a book is recognized, draw a bounding box
            if recognized_book != "Book not found":
                x, y, w, h = box_coords
                if w > 0 and h > 0:
                    # Draw bounding box
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                # Update the book info in the label
                book_info_label.config(text=f"Recognized Book: {recognized_book}")

                # Update metadata if available
                if metadata:
                    details = f"Title: {metadata.get('title', 'Unknown')}\n"
                    details += f"Author: {metadata.get('author', 'Unknown')}\n"
                    details += f"Genre: {metadata.get('genre', 'Unknown')}\n"
                    details += f"Year: {metadata.get('year', 'Unknown')}\n"
                    details += f"Description: {metadata.get('description', 'Unknown')}"
                    metadata_label.config(text=details)
            else:
                book_info_label.config(text="Recognized Book: Book not found")
                metadata_label.config(text="No book details available")

        # Increment frame counter and call this function again after 20 milliseconds
        frame_counter += 1
        root.after(20, update_frame)

    # Start the frame update loop
    update_frame()

    # Make sure to release the camera when the window is closed
    root.protocol("WM_DELETE_WINDOW", lambda: (cam.release(), root.destroy()))

# Tkinter setup
root = tk.Tk()
root.title("Book Recognition App")

# Create a label to display the recognized book
book_info_label = tk.Label(root, text="Recognized Book: None", font=("Arial", 16))
book_info_label.pack()

# Create a canvas to show the camera feed
canvas = tk.Canvas(root, width=640, height=480)
canvas.pack()

# Create a label for metadata
metadata_label = tk.Label(root, text="Metadata: None", font=("Arial", 12))
metadata_label.pack()

# Start the camera stream
start_camera_stream(book_info_label, canvas, root, metadata_label)

# Start the Tkinter main loop
root.mainloop()
