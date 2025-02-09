[![Università degli studi di Firenze](https://i.imgur.com/1NmBfH0.png)](https://ingegneria.unifi.it)

Learn more:  
📄 **[Read the Full Report](https://github.com/mattiamarilli/imagereader/blob/master/reports/ImageReaderReport.pdf)**  
🎥 **[Watch the Presentation](https://github.com/mattiamarilli/imagereader/blob/master/reports/ImageReaderPresentation.pdf)**

Image Reader Project - Sequential vs Parallel
---

## Overview
This project explores the optimization of image reading in Python using **sequential** and **parallel** approaches. The goal is to improve the efficiency of image loading and decompression by leveraging asynchronous I/O and multiprocessing techniques. The project compares the performance of these approaches and provides insights into their effectiveness for different workloads.

The project focuses on two critical phases of image loading:
1. **Memory Loading**: Reading image data from storage into memory.
2. **Decompression**: Decoding compressed image data into a usable format.

Two main approaches are implemented:
1. **Sequential Version**: Processes images one at a time without parallelism.
2. **Parallel Version**: Uses asynchronous I/O for memory loading and multiprocessing for decompression to improve performance.

---

## Key Features

- **Asynchronous I/O**: Utilizes `aiofiles` for non-blocking file I/O operations, allowing multiple images to be loaded concurrently.
- **Multiprocessing**: Leverages Python's `concurrent.futures` with `ProcessPoolExecutor` to distribute decompression tasks across multiple CPU cores.
- **Performance Metrics**: Measures execution time, speedup, and efficiency to evaluate the benefits of parallelization.

---

## Implementation

### Sequential Approach
- **Memory Loading**: Images are loaded one by one using synchronous file I/O.
- **Decompression**: Each image is decompressed sequentially after being loaded into memory.
- **Performance**: Suitable for small datasets but inefficient for larger workloads due to lack of parallelism.

### Parallel Approach
- **Asynchronous I/O**: Uses `aiofiles` to load multiple images concurrently, reducing idle time during I/O operations.
- **Multiprocessing**: Distributes decompression tasks across multiple processes to maximize CPU utilization.
- **Performance**: Significantly faster for large datasets, especially when decompression is CPU-bound.

---

## Performance Evaluation

### Metrics
- **Execution Time**: Time taken to load and decompress images.
- **Speedup**: Ratio of sequential execution time to parallel execution time.
- **Efficiency**: Measures how effectively additional resources (e.g., CPU cores) are utilized.

### Results
- **Asynchronous I/O**: Minimal speedup due to disk I/O limitations.
- **Multiprocessing**: Significant speedup for large datasets, with diminishing returns as the number of processes increases.

---

## Example Usage

### Sequential Version
```bash
python sequential_image_reader.py 
```
### Parallel Version
```bash
python parallel_image_reader.py


