import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('images/benchmark_decompression.csv')

plt.figure(figsize=(10, 6))
for num_images in df['Num_Images'].unique():
    subset = df[df['Num_Images'] == num_images]
    plt.plot(subset['Num_Processes'], subset['Speedup_Avg'], label=f'Num_Images = {num_images}', marker='o')

plt.title('Average Speedup vs. Number of Processes')
plt.xlabel('Number of Processes')
plt.ylabel('Average Speedup')
plt.legend(title='Num_Images')
plt.grid(True)
plt.show()

plt.figure(figsize=(10, 6))
for num_images in df['Num_Images'].unique():
    subset = df[df['Num_Images'] == num_images]
    plt.plot(subset['Num_Processes'], subset['Efficiency_Avg'], label=f'Num_Images = {num_images}', marker='o')

plt.title('Average Efficiency vs. Number of Processes')
plt.xlabel('Number of Processes')
plt.ylabel('Average Efficiency')
plt.legend(title='Num_Images')
plt.grid(True)
plt.show()
