import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  # Add this line

import tkinter as tk
from camera.camera_stream import start_camera_stream

def start_app():
    # Initialize the Tkinter window
    root = tk.Tk()
    root.title("Book Recognition App")

    # Create a label to display the recognized book
    book_info_label = tk.Label(root, text="Recognized Book: None", font=("Arial", 16), padx=20, pady=20)
    book_info_label.pack()

    # Create a canvas to show the camera feed
    canvas = tk.Canvas(root, width=1040, height=780)
    canvas.pack()

    # Start the camera stream
    metadata_label = tk.Label(root, text="Book Details:", font=("Arial", 11), justify=tk.CENTER, width=100, wraplength=500)
    metadata_label.pack()


# Start the camera stream and pass in the labels
    start_camera_stream(book_info_label, canvas, root, metadata_label)

    # Start the Tkinter main loop
    root.mainloop()

if __name__ == '__main__':
    start_app()

