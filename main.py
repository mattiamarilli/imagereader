import os
import time
import aiofiles
from PIL import Image
from io import BytesIO
import asyncio
import tempfile
import re

class SequentialOnDemandImageReader:
    def __init__(self, directory, min_index=1, max_index=10):
        self.directory = directory
        self.min_index = min_index
        self.max_index = max_index
        self.compressed_images = {}

    def load_images(self):
        for file_name in os.listdir(self.directory):
            match = re.match(r"image(\d+)\.(jpg|jpeg)", file_name.lower())
            if match:
                index = int(match.group(1))
                if self.min_index <= index <= self.max_index:
                    file_path = os.path.join(self.directory, file_name)
                    with open(file_path, "rb") as f:
                        #time.sleep(0.2)
                        self.compressed_images[file_name] = BytesIO(f.read())

    def get_image(self, file_name):
        if file_name not in self.compressed_images:
            raise ValueError(f"Image '{file_name}' not found.")
        compressed_stream = self.compressed_images[file_name]
        compressed_stream.seek(0)
        return Image.open(compressed_stream)


class AsyncOnDemandImageReader:
    def __init__(self, directory, min_index=1, max_index=10):
        self.directory = directory
        self.min_index = min_index
        self.max_index = max_index
        self.compressed_images = {}

    async def load_image(self, file_path):
        async with aiofiles.open(file_path, "rb") as f:
            #await asyncio.sleep(0.2)
            content = await f.read()
        return BytesIO(content)

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

    def get_image(self, file_name):
        if file_name not in self.compressed_images:
            raise ValueError(f"Image '{file_name}' not found.")
        compressed_stream = self.compressed_images[file_name]
        compressed_stream.seek(0)
        return Image.open(compressed_stream)


def benchmark_sequential(directory, min_index=1, max_index=10):
    reader = SequentialOnDemandImageReader(directory, min_index, max_index)
    start_time = time.time()
    reader.load_images()
    end_time = time.time()
    return end_time - start_time


async def benchmark_async(directory, min_index=1, max_index=10):
    reader = AsyncOnDemandImageReader(directory, min_index, max_index)
    start_time = time.time()
    await reader.load_images()
    end_time = time.time()
    return end_time - start_time


def saturate_cache(file_size_gb=2):
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        file_path = temp_file.name
        chunk_size = 1024 * 1024
        total_size = file_size_gb * 1024 * 1024 * 1024
        for _ in range(total_size // chunk_size):
            temp_file.write(b'\0' * chunk_size)
    try:
        with open(file_path, "rb") as f:
            while f.read(chunk_size):
                pass
    finally:
        os.remove(file_path)

def run_benchmark():
    image_dir = "./images"
    min_index = 1
    speedups = {}

    num_images_list = [50, 100, 300, 500, 700, 900]

    for num_images in num_images_list:
        print(f"\nEsecuzione benchmark con {num_images} immagini...")

        speedups[num_images] = []
        for i in range(0, 5):
            print("Saturazione della cache...")
            saturate_cache(file_size_gb=2)
            sequential_time = benchmark_sequential(image_dir, min_index, min_index + num_images - 1)
            print(f"Tempo sequenziale: {sequential_time} secondi")

            print("Saturazione della cache...")
            saturate_cache(file_size_gb=2)
            async_time = asyncio.run(benchmark_async(image_dir, min_index, min_index + num_images - 1))
            print(f"Tempo asincrono: {async_time} secondi")

            speedup = sequential_time / async_time if async_time > 0 else float("inf")
            print(f"Speedup: {speedup}x")
            speedups[num_images].append(speedup)

        avg_speedup = sum(speedups[num_images]) / len(speedups[num_images])
        print(f"Speedup medio per {num_images} immagini: {avg_speedup}x\n")

    return speedups

def save_report(speedups):
    with open("speedup_report_first.txt", "w") as report_file:
        report_file.write("Report dei Speedup medi\n")
        report_file.write("========================\n")
        for num_images, speedup_list in speedups.items():
            avg_speedup = sum(speedup_list) / len(speedup_list)
            report_file.write(f"Numero di immagini: {num_images} - Speedup medio: {avg_speedup}x\n")

if __name__ == "__main__":
    speedups = run_benchmark()
    save_report(speedups)