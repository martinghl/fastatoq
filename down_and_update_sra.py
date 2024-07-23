import os
import pandas as pd
import subprocess
import argparse
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

def download_sra_entry(srr, output_folder):
    try:
        result = subprocess.run(['fastq-dump', srr, '--outdir', output_folder], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Failed to download data for {srr}, Error: {result.stderr}")
        return srr
    except Exception as e:
        print(f"Failed to download data for {srr}, Error: {e}")
        return None

def download_sra_data_and_update_csv(gsm_srr_csv, output_folder):
    # 读取CSV文件
    df = pd.read_csv(gsm_srr_csv)
    
    # 确保输出文件夹存在
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # 将SRR写入文件
    srr_list = df['SRR'].dropna().tolist()
    
    # 使用多线程下载数据并显示进度
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(download_sra_entry, srr, output_folder): srr for srr in srr_list}
        for future in tqdm(as_completed(futures), total=len(futures), desc="Downloading SRA data", unit="file"):
            future.result()

    # 更新下载路径
    download_paths = []
    for srr in df['SRR']:
        if pd.notna(srr):
            download_path = os.path.join(output_folder, srr + ".fastq")
            if os.path.exists(download_path):
                download_paths.append(download_path)
            else:
                download_paths.append(None)
        else:
            download_paths.append(None)
    
    # 将下载路径添加到DataFrame
    df['Download_Path'] = download_paths
    
    # 直接更新输入的CSV
    df.to_csv(gsm_srr_csv, index=False)
    print(f"CSV with download paths has been updated and saved to {gsm_srr_csv}")

def main():
    # 设置命令行参数解析
    parser = argparse.ArgumentParser(description="Download SRA data and update CSV with download paths.")
    parser.add_argument('--gsm_srr_csv', type=str, required=True, help='Path to the input CSV file with GSM and SRR data.')
    parser.add_argument('--output_folder', type=str, required=True, help='Directory to download SRA files.')

    args = parser.parse_args()

    # 调用下载和更新CSV的函数
    download_sra_data_and_update_csv(args.gsm_srr_csv, args.output_folder)

if __name__ == "__main__":
    main()
