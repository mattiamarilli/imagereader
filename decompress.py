import os
import re
from PIL import Image
from concurrent.futures import ProcessPoolExecutor
import time
import statistics
import csv

# Sequential decompression class
class ImageDecompressorSequential:
    def __init__(self, directory, min_index=1, max_index=10):
        self.directory = directory  # Directory where images are stored
        self.min_index = min_index  # Minimum image index to process
        self.max_index = max_index  # Maximum image index to process

    # Get the paths of the images to decompress
    def get_image_paths(self):
        return [
            os.path.join(self.directory, file_name)  # Full file path
            for file_name in os.listdir(self.directory)  # List of files in the directory
            if (match := re.match(r"image(\d+)\.(jpg|jpeg)", file_name.lower()))  # Match files with the pattern "imageX.jpg/jpeg"
               and self.min_index <= int(match.group(1)) <= self.max_index  # Filter by index range
        ]

    # Decompress the images by converting to RGB format
    def decompress_images(self, image_paths):
        for file_path in image_paths:
            with Image.open(file_path) as img:
                img.convert("RGB")  # Convert image to RGB mode

    # Benchmark the decompression process
    def benchmark(self):
        image_paths = self.get_image_paths()  # Get the paths of the images
        start = time.perf_counter()  # Start timing
        self.decompress_images(image_paths)  # Decompress images
        sequential_time = time.perf_counter() - start  # Calculate elapsed time
        return sequential_time  # Return the time taken for decompression


# Parallel decompression class using multiple processes
class ImageDecompressorParallel:
    def __init__(self, directory, min_index=1, max_index=10, num_processes=None):
        self.directory = directory  # Directory where images are stored
        self.min_index = min_index  # Minimum image index to process
        self.max_index = max_index  # Maximum image index to process
        self.num_processes = num_processes or os.cpu_count()  # Set number of processes, default to CPU count

    # Get the paths of the images to decompress
    def get_image_paths(self):
        return [
            os.path.join(self.directory, file_name)  # Full file path
            for file_name in os.listdir(self.directory)  # List of files in the directory
            if (match := re.match(r"image(\d+)\.(jpg|jpeg)", file_name.lower()))  # Match files with the pattern "imageX.jpg/jpeg"
               and self.min_index <= int(match.group(1)) <= self.max_index  # Filter by index range
        ]

    # Decompress a single image in parallel
    def _decompress_image(self, file_path):
        with Image.open(file_path) as img:
            img.convert("RGB")  # Convert image to RGB mode

    # Decompress all images using a pool of processes
    def decompress_images(self, image_paths):
        with ProcessPoolExecutor(max_workers=self.num_processes) as executor:
            executor.map(self._decompress_image, image_paths)  # Process images in parallel

    # Benchmark the parallel decompression process and calculate speedup
    def benchmark(self, sequential_time):
        image_paths = self.get_image_paths()  # Get the paths of the images
        start = time.perf_counter()  # Start timing
        self.decompress_images(image_paths)  # Decompress images in parallel
        parallel_time = time.perf_counter() - start  # Calculate elapsed time

        speedup = sequential_time / parallel_time if parallel_time > 0 else float('inf')  # Calculate speedup
        return parallel_time, speedup  # Return parallel time and speedup


if __name__ == "__main__":
    directory = "./images"  # Directory where images are stored
    num_images_list = [50, 100, 300, 500, 700, 900]  # List of different image counts to test
    num_processes_list = [1, 2, 4, 6, 8, 16]  # Number of processes to use in parallel tests
    repetitions = 10  # Number of times to repeat the benchmark for averaging

    results = []  # List to store results

    # Open a CSV file to store the benchmark results
    with open("performancelog/decompresslog.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Num_Images", "Num_Processes", "Sequential_Time_Avg", "Parallel_Time_Avg",
                         "Speedup_Avg", "Efficiency_Avg"])

        # Sequential benchmark: run once for each number of images
        for num_images in num_images_list:
            seq_times = []  # List to store sequential times for averaging
            sequential_decompressor = ImageDecompressorSequential(directory, 1, num_images)  # Create sequential decompressor

            # Repeat benchmark for averaging
            for _ in range(repetitions):
                seq_time = sequential_decompressor.benchmark()  # Run the sequential benchmark
                seq_times.append(seq_time)

            avg_seq_time = statistics.mean(seq_times)  # Average sequential time
            seq_std = statistics.stdev(seq_times) if len(seq_times) > 1 else 0  # Standard deviation of sequential times

            print(f"Images: {num_images} -> Sequential: {avg_seq_time:.2f}s")

            # Now perform the parallel tests with varying numbers of processes
            for num_processes in num_processes_list:
                par_times, speedups = [], []  # Lists to store parallel times and speedups
                parallel_decompressor = ImageDecompressorParallel(directory, 1, num_images, num_processes=num_processes)  # Create parallel decompressor

                # Repeat benchmark for averaging
                for _ in range(repetitions):
                    par_time, speedup = parallel_decompressor.benchmark(avg_seq_time)  # Run parallel benchmark
                    par_times.append(par_time)
                    speedups.append(speedup)

                avg_par_time = statistics.mean(par_times)  # Average parallel time
                avg_speedup = statistics.mean(speedups)  # Average speedup
                efficiency = avg_speedup / num_processes  # Calculate efficiency

                # Append the results to the list and write to the CSV file
                results.append([num_images, num_processes, avg_seq_time, avg_par_time, avg_speedup, efficiency])

                writer.writerow([num_images, num_processes, avg_seq_time, avg_par_time, avg_speedup, efficiency])

                print(f"Images: {num_images}, Processes: {num_processes} -> Sequential: {avg_seq_time:.2f}s, "
                      f"Parallel: {avg_par_time:.2f}s, Speedup: {avg_speedup:.2f}x, Efficiency: {efficiency:.2f}")
