# Get top 10K URLs from url_list_prep/tranco_W4L39.csv. Ranking is 1st column.
# Stratified sampling strategy: (1) Top 5K, (2) 5K-10K, (3) 10K-50K, (4) 50K-100K, 100K-500K, (5) 500K-1M

import pandas as pd
import csv
import os

def main():
    csv_path = 'tranco_W4L39.csv'
    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)

    strata_limits = [(1, 5000), (5001, 10000), (10001, 50000), (50001, 100000), (100001, 500000), (500001, 1000000)]
    sample_sizes = [5000, 1000, 1000, 1000, 1000, 1000]

    df = pd.read_csv(csv_path, header=None, names=['rank', 'url'])

    sampled_urls = []
    url_stratum_map = []
    for (low, high), size in zip(strata_limits, sample_sizes):
        stratum = df[(df['rank'] >= low) & (df['rank'] <= high)]
        sampled_df = stratum.sample(n=min(size, len(stratum)), random_state=42)
        sampled_urls.extend(sampled_df['url'].tolist())
        for _, sampled_df_row in sampled_df.iterrows():
            url = sampled_df_row['url']
            rank = sampled_df_row['rank']
            url_stratum_map.append([rank, url, f"{low}-{high}"])

    with open(os.path.join(output_dir, 'sampled_urls_strata.csv'), 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['rank', 'url', 'stratum_range'])
        writer.writerows(url_stratum_map)

    with open(os.path.join(output_dir, 'sampled_urls.txt'), 'w') as f:
        for url in sampled_urls:
            f.write(url + '\n')



if __name__ == '__main__':
    main()
