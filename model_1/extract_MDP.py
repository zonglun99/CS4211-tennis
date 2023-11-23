import os
import re
import numpy as np
import csv

def extract_mean_probabilities(file_path):
    # Read the content of the file
    with open(file_path, 'r') as file:
        content = file.read()

    # Use regular expressions to extract the probabilities
    probabilities = re.findall(r'is Valid with Probability\s*\[(.*?)\]', content)[0].split(',')

    # Convert the extracted probabilities to floats
    probabilities = [float(prob) for prob in probabilities]

    # Calculate and return the mean probability of the 2 float values
    mean_probability = np.mean(probabilities)
    return mean_probability

def process_files_in_directory(directory_path):
    # Get a list of all files in the specified directory
    file_list = [f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]

    # Process each file and extract mean probabilities
    results = []
    for file_name in file_list:
        file_path = os.path.join(directory_path, file_name)
        mean_probability = extract_mean_probabilities(file_path)

        # Extract information from the file name
        parts = file_name.split('_')
        date = parts[2]
        player1 = parts[3].replace('-', ' ')
        player2 = parts[4].split('.')[0].replace('-', ' ')

        # Calculate 1 - probability for winning probability of the other player
        complement_probability = 1 - mean_probability

        results.append([date, player1, player2, mean_probability, complement_probability])

    return results

# Set pcsp_out as the path to all txt files
directory_path = 'pcsp_out'
result = process_files_in_directory(directory_path)
# Create new file named output.csv to store date, names and prob
csv_file_path = 'output.csv'

# Write results to CSV
with open(csv_file_path, 'w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    # Write header
    csv_writer.writerow(['date', 'P1Name', 'P2Name', 'P1WinProb', 'P2WinProb'])
    # Write data
    csv_writer.writerows(result)

print(f"Results written to {csv_file_path}")

