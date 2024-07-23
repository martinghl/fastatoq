# fastatoq.py:

将FASTA格式的序列文件转换为FASTQ格式，并对超过指定长度的序列进行分割。具体实现如下：

	1.	读取命令行参数：从命令行获取输入的FASTA文件路径、输出的FASTQ文件路径，以及最大长度（len_max）。
	2.	读取FASTA文件：逐行读取FASTA文件中的序列。
	3.	处理序列：对每个序列进行以下操作：
	•	如果序列长度小于或等于指定的最大长度，则直接将其转换为FASTQ格式。
	•	如果序列长度大于指定的最大长度，则将其分割为多个片段，每个片段的长度不超过最大长度，并将每个片段转换为FASTQ格式。
	4.	写入FASTQ文件：将处理后的序列信息写入输出的FASTQ文件。

调用方法：
python script.py input.fa output.fq 20

# series_to_csv.py:

解析指定文件夹中的所有series_matrix文件，提取样本信息，并获取对应的SRR（Sequence Read Archive）ID，然后将结果保存到指定的CSV文件中。具体的步骤如下：

	1.	解析series_matrix文件：读取指定文件夹中的所有_series_matrix.txt文件，并提取相关信息，如样本的GEO编号、来源、生物学特性等。
	2.	获取SRR ID：通过调用SRAweb API，根据样本的GEO编号（GSM）获取对应的SRR ID。
	3.	保存结果：将解析后的数据和对应的SRR ID保存到指定的CSV文件中。

在linux环境下调用：
python parse_series.py --folder_path /path/to/matrix_folder --save_path /path/to/matrix_folder/data.csv

# down_and_update_sra.py

从SRA数据库中下载SRR文件，并更新输入的CSV文件，在CSV文件中记录下载的文件路径。具体来说：

	1.	读取CSV文件：从CSV文件中读取GSM和SRR数据。
	2.	下载SRR文件：使用fastq-dump命令下载SRR文件。
	3.	更新CSV文件：在CSV文件中添加一列记录下载的文件路径。

在linux环境下调用：
python down_and_update_sra.py --gsm_srr_csv /path/to/gsm_srr.csv --output_folder /path/to/output_folder
