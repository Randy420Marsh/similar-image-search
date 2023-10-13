import cv2
import os
import numpy as np
import argparse
import logging
import sys
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, Listbox
from PIL import Image, ImageTk

# Function to compute the color histogram of an image
def compute_histogram(image_path):
    try:
        image = cv2.imread(image_path, cv2.IMREAD_COLOR)

        if image is None:
            logging.warning(f"Unable to read image '{image_path}'")
            return None

        # Check if the image is grayscale, and convert it to color if necessary
        if len(image.shape) == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

        # Convert the image to the HSV color space
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Calculate the histogram
        hist = cv2.calcHist([hsv], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])

        # Normalize the histogram
        hist = cv2.normalize(hist, hist).flatten()

        return hist
    except Exception as e:
        logging.warning(f"Error while processing '{image_path}': {e}")
        return None

# Function to calculate the similarity score between two histograms
def calculate_similarity_score(hist1, hist2):
    # Use the chi-squared distance as the similarity score
    try:
        score = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CHISQR)
        return 1.0 / (1.0 + score)  # Convert distance to similarity
    except Exception as e:
        logging.warning(f"Error while calculating similarity score: {e}")
        return 0.0

# Function to find visually similar images
def find_similar_images(input_image_path, search_folder, threshold=0.30, num_similar=10, canceled=False):
    input_hist = compute_histogram(input_image_path)
    if input_hist is None:
        return []

    image_paths = []
    image_histograms = []

    try:
        # Iterate through the subfolders and find image histograms
        for root, dirs, files in os.walk(search_folder):
            if canceled:
                break

            for file in files:
                if file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.webp')):
                    image_path = os.path.join(root, file)
                    image_hist = compute_histogram(image_path)

                    if image_hist is not None:
                        image_paths.append(image_path)
                        image_histograms.append(image_hist)
    except Exception as e:
        logging.warning(f"Error while searching for images: {e}")

    if not image_paths:
        return []

    # Calculate the similarity scores
    similarity_scores = [calculate_similarity_score(input_hist, hist) for hist in image_histograms]

    # Find images that meet the similarity threshold
    similar_indices = [i for i, score in enumerate(similarity_scores) if score >= threshold]

    # Sort the images by similarity
    similar_images = [image_paths[i] for i in similar_indices]

    if similar_images:
        print(f"Similar images to '{input_image_path}' (with similarity threshold {threshold * 100}% or higher):")
        for i, image_path in enumerate(similar_images[:num_similar]):
            print(f"{i + 1}. {image_path}")

        # Generate a file name based on the current date and time
        now = datetime.now()
        timestamp = now.strftime("%d-%m-%Y_%H-%M-%S")
        output_file = f"similar-images-{timestamp}.txt"

        # Log command-line options and similar images to the output file
        with open(output_file, 'w', encoding='utf-8') as out_file:
            out_file.write(f"Input image: {input_image_path}\n")
            out_file.write(f"Threshold: {threshold}\n")
            out_file.write(f"Number of similar images: {num_similar}\n\n")
            out_file.write("Similar images:\n")

            for i, image_path in enumerate(similar_images[:num_similar]):
                out_file.write(f"{i + 1}. {image_path}\n")

        print(f"Similar images logged to '{output_file}'")
    
    if canceled:
        return []

    if similar_images:
        return similar_images[:num_similar]
    else:
        return []

class SimilarImageSearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Similar Image Search")

        self.input_image_path = tk.StringVar()
        self.search_folder_path = tk.StringVar()
        self.threshold = tk.DoubleVar()
        self.num_similar = tk.IntVar()
        self.input_image_preview = None
        self.cancel_button = None

        self.create_widgets()

        # Initialize list to hold similar image paths
        self.similar_images = []
        self.canceled = False  # Flag to check if the search is canceled
    
    def create_widgets(self):
        tk.Label(self.root, text="Input Image Path:").pack()
        self.input_image_entry = tk.Entry(self.root, textvariable=self.input_image_path)
        self.input_image_entry.pack()
        tk.Button(self.root, text="Browse", command=self.browse_input_image).pack()
        
        # Display the input image preview
        if self.input_image_preview is not None:
            tk.Label(self.root, image=self.input_image_preview).pack()

        tk.Label(self.root, text="Search Folder:").pack()
        self.search_folder_entry = tk.Entry(self.root, textvariable=self.search_folder_path)
        self.search_folder_entry.pack()
        tk.Button(self.root, text="Browse", command=self.browse_search_folder).pack()
        
        tk.Label(self.root, text="Similarity Threshold:").pack()
        self.threshold_entry = tk.Entry(self.root, textvariable=self.threshold)
        self.threshold_entry.pack()
        self.threshold.set(0.30)

        tk.Label(self.root, text="Number of Similar Images:").pack()
        self.num_similar_entry = tk.Entry(self.root, textvariable=self.num_similar)
        self.num_similar_entry.pack()
        self.num_similar.set(10)

        # Create a Cancel button to stop the search
        self.cancel_button = tk.Button(self.root, text="Cancel", command=self.cancel_search)
        self.cancel_button.pack()

        tk.Button(self.root, text="Find Similar Images", command=self.find_similar_images).pack()

        # Create a Listbox to display similar image paths
        self.listbox = Listbox(self.root, selectmode=tk.SINGLE)
        self.listbox.pack()
        self.listbox.bind('<<ListboxSelect>>', self.show_image_preview)

    def browse_input_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.input_image_path.set(file_path)
            # Display the input image preview
            self.display_input_image_preview(file_path)

    def browse_search_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.search_folder_path.set(folder_path)

    def display_input_image_preview(self, image_path):
        try:
            image = Image.open(image_path)
            image.thumbnail((300, 300))
            self.input_image_preview = ImageTk.PhotoImage(image)

            if self.input_image_preview is not None:
                label = tk.Label(self.root, image=self.input_image_preview)
                label.image = self.input_image_preview
                label.pack()
        except Exception as e:
            logging.warning(f"Error while displaying input image preview: {e}")

    def cancel_search(self):
        self.canceled = True

    def find_similar_images(self):
        self.cancel_button['state'] = tk.NORMAL  # Enable the Cancel button
        input_path = self.input_image_path.get()
        threshold_value = self.threshold.get()
        num_similar_value = self.num_similar.get()
        search_folder_path = self.search_folder_path.get()

        self.listbox.delete(0, tk.END)  # Clear the listbox
        self.canceled = False  # Reset the canceled flag

        self.similar_images = find_similar_images(input_path, search_folder_path, threshold_value, num_similar_value, self.canceled)

        if self.canceled:
            messagebox.showinfo("Canceled", "Similar image search canceled.")
        elif self.similar_images:
            for image_path in self.similar_images:
                self.listbox.insert(tk.END, os.path.basename(image_path))

        self.cancel_button['state'] = tk.DISABLED  # Disable the Cancel button

        if not self.canceled:
            messagebox.showinfo("Success", "Similar images search completed. Results are displayed below.")

    def browse_input_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.input_image_path.set(file_path)
            # Display the input image preview
            self.display_input_image_preview(file_path)

    def display_input_image_preview(self, image_path):
        if self.input_image_preview is not None:
            self.input_image_preview.destroy()  # Destroy the previous preview image widget

            try:
                image = Image.open(image_path)
                image.thumbnail((300, 300))
                image_preview = ImageTk.PhotoImage(image)

                if image_preview is not None:
                    preview_window = tk.Toplevel(self.root)
                    label = tk.Label(preview_window, image=image_preview)
                    label.image = image_preview
                    label.pack()
            except Exception as e:
                logging.warning(f"Error while displaying image preview: {e}")

if __name__ == "__main__":
    # Configure logging to save errors to a file
    logging.basicConfig(filename='errors_log.txt', level=logging.WARNING,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    # Redirect standard error to the errors log file
    sys.stderr = open('errors_log.txt', 'a')
    
    root = tk.Tk()
    app = SimilarImageSearchApp(root)
    root.mainloop()