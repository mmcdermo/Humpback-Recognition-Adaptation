"""
  Script to replace training data with some fraction of itself
  Usage: python rw_subset.py <fraction>

  Assumes original images are in ../origImages/ and that original training data is in
  ../origData/
"""

import sys
import os
import csv
import random
import math
import shutil
import glob
import sh
import subprocess

origImages = "../origImages/"
origData = "../origData/"
outputData = "../data/"
outputImages = "../orig/"

# Generate a random subset of CSV rows and image IDs, ensuring that
#  every image ID present in the CSV is present in the image ID selection
# TODO: If necessary, we can first pick a subset of whales, and then
#       include images for that subset of whales. 
def subset(csv, imageIDs, fraction):
    imgMap = {}
    sample_size = int(math.ceil(fraction * len(csv)))
    csvSubset = [ csv[i] for i in sorted(random.sample(xrange(len(csv)), sample_size)) ]
    finalCSVSubset = []
    imgSubset = []
    for row in csvSubset:
        img = row[0] + ".jpg"
        if img in imageIDs:
            # Only include this row if we have the corresponding image available
            imgSubset.append(row[0]+".jpg")
            finalCSVSubset.append(row)

    return finalCSVSubset, imgSubset
def usage():
    print("Usage: python rw_subset.py <fraction>")

# Reads trainLabels.csv from `origData` folder and prints new version to `outputData`
def generateTrainingCSV(csvSubset):
    with open(outputData + "trainLabels.csv", 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["image", "level"])
        for row in csvSubset:
            writer.writerow(row)

# Moves a random subset of images from `origImages` to `outputImages`
def moveTrainingImages(imageNames):
    # Clear out current folder
    files = glob.glob(outputImages+'*')
    print("Deleting "+str(len(files))+" old training images")
    if len(files) > 0:
        sh.rm(files)
    
    # Move images over
    i = 0
    print("Copying "+str(len(imageNames))+" images")
    for image in imageNames:
        i += 1
        if i % 200 == 0:
            print(".")
        shutil.copyfile(origImages+image, outputImages+image)
        #cmd = ["cp", origImages+image, outputImages+image]
        #proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
def main():
    if len(sys.argv) != 2:
        usage()
        exit(1)
    try:
        fraction = float(sys.argv[1])
    except:
        usage()
        exit(1)

    print(fraction)
    # Read the CSV and get a list of all available images
    csvl = []
    with open(origData + "trainLabels.csv", 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in reader:
            csvl.append(row)
    images = os.listdir(origImages)

    print("Found "+str(len(images))+" images")
    print("Found "+str(len(csvl))+" training labels")

    # Determine the subset we want
    csvSubset, imgsSubset = subset(csvl, images, fraction)

    # Write it out
    generateTrainingCSV(csvSubset)
    moveTrainingImages(imgsSubset)

if __name__ == "__main__":
    main()
