
# 1.
# Install python3:
# then create a batch script called activate.bat with the contents below and run it,
# it will create a virtual python environment for the packages.
# remove the # before each line in the .bat file

# 2.
# install the dependencies
# pip install opencv-python-headless scikit-learn scikit-learn-intelex argparse logging numpy

###############
#activate.bat
###############

#@echo off

#SET current_path=%CD%
#cd %current_path%
#setlocal enabledelayedexpansion
#set "python=python"
#IF exist ./venv (cmd /k call .\venv\scripts\activate.bat)  ELSE (cmd /k python -m venv venv && cmd /k call .\venv\scripts\activate.bat)

###############

# 3.
# Create a script to activate venv and run the script

###############
#run.bat
###############

#@echo off

#setlocal enabledelayedexpansion
#set "PYTHON=python"
#echo "Launching..."
#cd %CD%
#set "USER=%USERNAME%"
#echo Current User = %USER%
#call .\venv\scripts\activate.bat
#echo "venv activated"
#python --version
#python -s similar-image-search.py
#pause

###############

# Required dependencies:
# pip install opencv-python-headless scikit-learn scikit-learn-intelex argparse logging numpy

# update pip:
# python.exe -m pip install --upgrade pip

# Example usage:
# python similar-image-search.py "C:\AI\CHATGPT-3.5-visually-similar-image-search\input.png" "D:\AI_outputs_etc" --threshold 0.005
# finds at least 0.5% similar images

import cv2
import os
import numpy np
import argparse
import logging
import sys
from datetime import datetime

# Function to compute the color histogram of an image
def compute_histogram(image_path):
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

# Function to calculate the similarity score between two histograms
def calculate_similarity_score(hist1, hist2):
    # Use the chi-squared distance as the similarity score
    score = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CHISQR)
    return 1.0 / (1.0 + score)  # Convert distance to similarity

# Function to find visually similar images
def find_similar_images(input_image_path, search_folder, threshold=0.005, num_similar=5):
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
        print(f"Similar images to '{input_image_path}' (with similarity threshold {threshold * 100}% or higher):")
        for i, image_path in enumerate(similar_images[:num_similar]):
            print(f"{i + 1}. {image_path}")

        # Generate a file name based on the current date and time
        now = datetime.now()
        timestamp = now.strftime("%d-%m-%Y_%H-%M-%S")
        output_file = f"similar-images-{timestamp}.txt"

        # Log command-line options and similar images to the output file
        with open(output_file, 'w') as out_file:
            out_file.write(f"Input image: {input_image_path}\n")
            out_file.write(f"Threshold: {threshold}\n")
            out_file.write(f"Number of similar images: {num_similar}\n\n")
            out_file.write("Similar images:\n")

            for i, image_path in enumerate(similar_images[:num_similar]):
                out_file.write(f"{i + 1}. {image_path}\n")

        print(f"Similar images logged to '{output_file}'")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find visually similar images.")
    parser.add_argument("input_image_path", help="Path to the input image")
    parser.add_argument("search_folder", help="Folder to search for similar images")
    parser.add_argument("--threshold", type=float, default=0.005, help="Similarity score threshold (from 0 to 1)")
    parser.add_argument("--num_similar", type=int, default=5, help="Number of similar images to find")

    args = parser.parse_args()

    # Configure logging to save errors to a file
    logging.basicConfig(filename='errors_log.txt', level=logging.WARNING,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    # Redirect standard error to the errors log file
    sys.stderr = open('errors_log.txt', 'a')

    find_similar_images(args.input_image_path, args.search_folder, args.threshold, args.num_similar)
