import os
import pandas as pd
from pysradb.sraweb import SRAweb
import concurrent.futures
from tqdm import tqdm
import argparse

# 解析 series_matrix 文件的函数
def parse_series_matrix(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    series_geo_accession = None
    series_sample_ids = []
    
    data = {
        "Series_geo_accession": [],
        "Series_sample_id": [],
        "Sample_title": [],
        "Sample_geo_accession": [],
        "Sample_source_name_ch1": [],
        "Sample_organism_ch1": [],
        "Sample_molecule_ch1": [],
        "Sample_platform_id": [],
        "Sample_Character_1": [],
        "Sample_Character_2": [],
        "Sample_Character_3": []
    }
    
    for line in lines:
        if line.startswith("!Series_geo_accession"):
            series_geo_accession = line.strip().split("\t")[1].strip('"')
        elif line.startswith("!Series_sample_id"):
            series_sample_ids = line.strip().split("\t")[1].strip('"').split()
        elif line.startswith("!Sample_title"):
            sample_titles = line.strip().split("\t")[1:]
        elif line.startswith("!Sample_geo_accession"):
            sample_geo_accessions = line.strip().split("\t")[1:]
        elif line.startswith("!Sample_source_name_ch1"):
            sample_source_names = line.strip().split("\t")[1:]
        elif line.startswith("!Sample_organism_ch1"):
            sample_organisms = line.strip().split("\t")[1:]
        elif line.startswith("!Sample_molecule_ch1"):
            sample_molecules = line.strip().split("\t")[1:]
        elif line.startswith("!Sample_platform_id"):
            sample_platform_ids = line.strip().split("\t")[1:]
        elif line.startswith("!Sample_characteristics_ch1"):
            characteristics = line.strip().split("\t")[1:]
            if not data["Sample_Character_1"]:
                data["Sample_Character_1"] = characteristics
            elif not data["Sample_Character_2"]:
                data["Sample_Character_2"] = characteristics
            elif not data["Sample_Character_3"]:
                data["Sample_Character_3"] = characteristics
    
    max_length = max(len(data[key]) for key in data)
    data["Series_geo_accession"] = [series_geo_accession] * max_length
    data["Series_sample_id"] = series_sample_ids[:max_length]
    data["Sample_title"] = sample_titles
    data["Sample_geo_accession"] = sample_geo_accessions
    data["Sample_source_name_ch1"] = sample_source_names
    data["Sample_organism_ch1"] = sample_organisms
    data["Sample_molecule_ch1"] = sample_molecules
    data["Sample_platform_id"] = sample_platform_ids
    for key in data:
        if isinstance(data[key], list) and len(data[key]) < max_length:
            data[key] += [None] * (max_length - len(data[key]))

    # 创建 DataFrame
    df = pd.DataFrame(data)

    return df

# 解析文件夹中的所有 series_matrix 文件的函数
def parse_all_series_matrix(folder_path):
    all_dataframes = []
    for filename in os.listdir(folder_path):
        if filename.endswith("_series_matrix.txt"):
            file_path = os.path.join(folder_path, filename)
            df = parse_series_matrix(file_path)
            all_dataframes.append(df)
    
    # 合并所有 DataFrame
    combined_df = pd.concat(all_dataframes, ignore_index=True)
    return combined_df

# 获取 GSM 对应的 SRR 的函数
def fetch_srr(gsm_id):
    db = SRAweb()
    try:
        srr_info = db.gsm_to_srr(gsm_id.strip('"'))
        srrs = srr_info['run_accession'].tolist() if not srr_info.empty else []
    except Exception as e:
        srrs = []
    return srrs

def add_srr_and_save(df, save_path, save_interval=500, max_workers=10):
    gsm_ids = df['Sample_geo_accession'].tolist()
    srr_dict = {gsm: [] for gsm in gsm_ids}
    total_tasks = len(gsm_ids)
    srr_expanded_df = pd.DataFrame()

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(fetch_srr, gsm): gsm for gsm in gsm_ids}
        for i, future in enumerate(tqdm(concurrent.futures.as_completed(futures), total=total_tasks, desc="Processing GSM IDs")):
            gsm = futures[future]
            try:
                srrs = future.result()
            except Exception as e:
                srrs = []
                print("Error in:", gsm)
            srr_dict[gsm] = srrs
            
            # 每处理 save_interval 个任务，保存一次结果到 CSV 文件
            if (i + 1) % save_interval == 0 or (i + 1) == total_tasks:
                for gsm, srrs in list(srr_dict.items())[:save_interval]:
                    temp_df = df[df['Sample_geo_accession'] == gsm].copy()
                    temp_df = temp_df.loc[temp_df.index.repeat(len(srrs))]
                    temp_df['SRR'] = srrs
                    srr_expanded_df = pd.concat([srr_expanded_df, temp_df], ignore_index=True)
                    del srr_dict[gsm]  # 删除已处理的 GSM

                # 保存当前批次结果到 CSV 文件
                srr_expanded_df.to_csv(save_path, mode='a', header=not os.path.exists(save_path), index=False)
                srr_expanded_df = pd.DataFrame()  # 清空 DataFrame

def main():
    # 设置命令行参数解析
    parser = argparse.ArgumentParser(description='Parse series_matrix files and fetch SRR IDs')
    parser.add_argument('--folder_path', type=str, required=True, help='Path to the folder containing series_matrix files')
    parser.add_argument('--save_path', type=str, required=True, help='Path to save the resulting CSV file')
    
    args = parser.parse_args()
    folder_path = args.folder_path
    save_path = args.save_path
    
    # 解析所有 series_matrix 文件
    combined_df = parse_all_series_matrix(folder_path)
    # 添加 SRR 列并保存到 CSV 文件
    add_srr_and_save(combined_df, save_path)
    print(f"Combined DataFrame has been exported to {save_path}")

if __name__ == '__main__':
    main()