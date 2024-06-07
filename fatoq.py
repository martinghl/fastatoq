import sys

fa_f = sys.argv[1]
fq_f = sys.argv[2]
len_max = int(sys.argv[3])  # fq len max: 150bp

with open(fa_f, 'r') as f, open(fq_f, 'w') as pf:
    while True:
        name = f.readline().strip()
        if not name:
            break
        if name.startswith('>'):
            tmp_name = name.strip('>')
            read_id = '@'+tmp_name
        seq = f.readline().strip()
        if len(seq) <= len_max:
            read_info = '{rd_id}\n{seq}\n+\n{qual}\n'.format(rd_id=read_id, seq=seq, qual='F'*len(seq))
        else:
            read_info = ''
            cnt = int(len(seq) / len_max)
            for i in range(cnt):
                tmp_id = read_id + '_' + str(i)
                tmp_seq = seq[i*len_max:(i+1)*len_max]
                read_info += '{rd_id}\n{seq}\n+\n{qual}\n'.format(rd_id=tmp_id, seq=tmp_seq, qual='F'*len_max)
            lseq = len(seq) % len_max
            if lseq != 0:
                tmp_id = read_id + '_' + str(cnt)
                tmp_seq =seq[-lseq:]
                read_info += '{rd_id}\n{seq}\n+\n{qual}\n'.format(rd_id=tmp_id, seq=tmp_seq, qual='F'*lseq)
        pf.write(read_info)
