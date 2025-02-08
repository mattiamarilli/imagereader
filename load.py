import os
import time
import aiofiles
from PIL import Image
from io import BytesIO
import asyncio
import tempfile
import re

# Class to load images sequentially on demand
class SequentialOnDemandImageReader:
    # Initializes with directory and index range for images
    def __init__(self, directory, min_index=1, max_index=10):
        self.directory = directory
        self.min_index = min_index
        self.max_index = max_index
        self.compressed_images = {}  # Dictionary to store loaded images

    # Loads images from the directory that match the specified index range
    def load_images(self):
        for file_name in os.listdir(self.directory):
            match = re.match(r"image(\d+)\.(jpg|jpeg)", file_name.lower())
            if match:
                index = int(match.group(1))
                if self.min_index <= index <= self.max_index:
                    file_path = os.path.join(self.directory, file_name)
                    with open(file_path, "rb") as f:
                        self.compressed_images[file_name] = BytesIO(f.read())

    # Retrieves an image by its file name
    def get_image(self, file_name):
        if file_name not in self.compressed_images:
            raise ValueError(f"Image '{file_name}' not found.")
        compressed_stream = self.compressed_images[file_name]
        compressed_stream.seek(0)
        return Image.open(compressed_stream)

    # Benchmarks the time taken to load images sequentially
    def benchmark(self):
        start_time = time.time()
        self.load_images()
        end_time = time.time()
        return end_time - start_time


# Class to load images asynchronously on demand
class AsyncOnDemandImageReader:
    # Initializes with directory and index range for images
    def __init__(self, directory, min_index=1, max_index=10):
        self.directory = directory
        self.min_index = min_index
        self.max_index = max_index
        self.compressed_images = {}

    # Asynchronously loads an image from a given file path
    async def load_image(self, file_path):
        async with aiofiles.open(file_path, "rb") as f:
            content = await f.read()
        return BytesIO(content)

    # Asynchronously loads all images in the specified index range
    async def load_images(self):
        tasks = []
        for file_name in os.listdir(self.directory):
            match = re.match(r"image(\d+)\.(jpg|jpeg)", file_name.lower())
            if match:
                index = int(match.group(1))
                if self.min_index <= index <= self.max_index:
                    file_path = os.path.join(self.directory, file_name)
                    tasks.append(self.load_image(file_path))
        results = await asyncio.gather(*tasks)
        for file_name, result in zip(os.listdir(self.directory), results):
            self.compressed_images[file_name] = result

    # Retrieves an image by its file name
    def get_image(self, file_name):
        if file_name not in self.compressed_images:
            raise ValueError(f"Image '{file_name}' not found.")
        compressed_stream = self.compressed_images[file_name]
        compressed_stream.seek(0)
        return Image.open(compressed_stream)

    # Benchmarks the time taken to load images asynchronously
    async def benchmark(self):
        start_time = time.time()
        await self.load_images()
        end_time = time.time()
        return end_time - start_time


# Function to saturate cache with temporary data of a given size
def saturate_cache(file_size_gb=2):
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        file_path = temp_file.name
        chunk_size = 1024 * 1024  # 1 MB chunks
        total_size = file_size_gb * 1024 * 1024 * 1024  # Total size in bytes
        for _ in range(total_size // chunk_size):
            temp_file.write(b'\0' * chunk_size)
    try:
        with open(file_path, "rb") as f:
            while f.read(chunk_size):
                pass
    finally:
        os.remove(file_path)  # Clean up the temporary file

if __name__ == "__main__":
    image_dir = "./images"  # Directory where images are stored
    min_index = 1
    speedups = {}  # Dictionary to store speedup results

    num_images_list = [50, 100, 300, 500, 700, 900]  # List of different image set sizes

    for num_images in num_images_list:
        print(f"\nRunning benchmark with {num_images} images...")

        speedups[num_images] = []
        for i in range(0, 5):
            print("Saturating cache...")
            saturate_cache(file_size_gb=2)  # Fill cache with temporary data

            sequential_reader = SequentialOnDemandImageReader(image_dir, min_index, min_index + num_images - 1)
            sequential_time = sequential_reader.benchmark()  # Benchmark sequential loading
            print(f"Sequential time: {sequential_time} seconds")

            print("Saturating cache again...")
            saturate_cache(file_size_gb=2)

            async_reader = AsyncOnDemandImageReader(image_dir, min_index, min_index + num_images - 1)
            async_time = asyncio.run(async_reader.benchmark())  # Benchmark asynchronous loading
            print(f"Asynchronous time: {async_time} seconds")

            # Calculate and print speedup
            speedup = sequential_time / async_time if async_time > 0 else float("inf")
            print(f"Speedup: {speedup}x")
            speedups[num_images].append(speedup)

        # Calculate average speedup for the current number of images
        avg_speedup = sum(speedups[num_images]) / len(speedups[num_images])
        print(f"Average speedup for {num_images} images: {avg_speedup}x\n")

    # Write the speedup report to a file
    with open("./report/speedup_report.txt", "w") as report_file:
        report_file.write("Average Speedup Report\n")
        report_file.write("========================\n")
        for num_images, speedup_list in speedups.items():
            avg_speedup = sum(speedup_list) / len(speedup_list)
            report_file.write(f"Number of images: {num_images} - Average speedup: {avg_speedup}x\n")
