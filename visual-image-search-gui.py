import cv2
import os
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageFilter
import argparse
from datetime import datetime

# Function to compute the color histogram of an image
def compute_histogram(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_COLOR)

    if image is None:
        messagebox.showerror("Error", f"Unable to read image '{image_path}'")
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

# Function to calculate the similarity score between two histograms
def calculate_similarity_score(hist1, hist2):
    # Use the chi-squared distance as the similarity score
    score = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CHISQR)
    return 1.0 / (1.0 + score)  # Convert distance to similarity

# Function to find visually similar images
def find_similar_images(input_image_path, search_folder, threshold=0.30, num_similar=10):
    input_hist = compute_histogram(input_image_path)
    if input_hist is None:
        return

    image_paths = []
    image_histograms = []

    # Iterate through the subfolders and find image histograms
    for root, dirs, files in os.walk(search_folder):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.webp')):
                image_path = os.path.join(root, file)
                image_hist = compute_histogram(image_path)

                if image_hist is not None:
                    image_paths.append(image_path)
                    image_histograms.append(image_hist)

    if not image_paths:
        return

    # Calculate the similarity scores
    similarity_scores = [calculate_similarity_score(input_hist, hist) for hist in image_histograms]

    # Find images that meet the similarity threshold
    similar_indices = [i for i, score in enumerate(similarity_scores) if score >= threshold]

    # Sort the images by similarity
    similar_images = [image_paths[i] for i in similar_indices]

    if similar_images:
        # Generate a file name based on the current date and time
        now = datetime.now()
        timestamp = now.strftime("%d-%m-YYYY_%H-%M-%S")
        output_file = f"similar-images-{timestamp}.txt"

        # Write similar images to the output file
        with open(output_file, 'w') as out_file:
            out_file.write(f"Input image: {input_image_path}\n")
            out_file.write(f"Threshold: {threshold}\n")
            out_file.write(f"Number of similar images: {num_similar}\n\n")
            out_file.write("Similar images:\n")

            for i, image_path in enumerate(similar_images[:num_similar]):
                out_file.write(f"{i + 1}. {image_path}\n")

        messagebox.showinfo("Success", f"Similar images logged to '{output_file}'")

# Function to open a file dialog for image selection
def select_image():
    file_path = filedialog.askopenfilename()
    if file_path:
        display_image(file_path)
        input_image_path.set(file_path)

# Function to display the selected image in the GUI
def display_image(image_path):
    img = Image.open(image_path)
    # Resize the image while maintaining the correct aspect ratio and using Lanczos resampling
    img.thumbnail((300, 300), Image.LANCZOS)
    img = ImageTk.PhotoImage(img)
    image_label.config(image=img)
    image_label.image = img

# Function to open a file dialog for selecting the search folder
def select_search_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        search_folder_var.set(folder_path)

# Function to find and display similar images
def find_and_display_similar_images():
    input_path = input_image_path.get()
    threshold_value = float(threshold.get())
    num_similar_value = int(num_similar.get())
    find_similar_images(input_path, search_folder_var.get(), threshold_value, num_similar_value)

# Create the main window
window = tk.Tk()
window.title("Visual Image Search")

# Input image selection
input_image_path = tk.StringVar()
input_label = tk.Label(window, text="Select an input image:")
input_label.pack()
input_image_button = tk.Button(window, text="Browse", command=select_image)
input_image_button.pack()

# Display the selected image
image_label = tk.Label(window)
image_label.pack()

# Similarity threshold and number of similar images
threshold = tk.StringVar()
num_similar = tk.StringVar()

threshold_label = tk.Label(window, text="Similarity Threshold:")
threshold_label.pack()
threshold_entry = tk.Entry(window, textvariable=threshold)
threshold_entry.pack()

num_similar_label = tk.Label(window, text="Number of Similar Images:")
num_similar_label.pack()
num_similar_entry = tk.Entry(window, textvariable=num_similar)
num_similar_entry.pack()

# Search folder selection
search_folder_var = tk.StringVar()
search_folder_label = tk.Label(window, text="Select a search folder:")
search_folder_label.pack()
search_folder_button = tk.Button(window, text="Browse", command=select_search_folder)
search_folder_button.pack()

# Find and display similar images button
find_similar_button = tk.Button(window, text="Find Similar Images", command=find_and_display_similar_images)
find_similar_button.pack()

window.mainloop()
