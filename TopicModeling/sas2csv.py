import pandas as pd

from pathlib import Path
import sys
import itertools
import multiprocessing

from manage_path import *

def mutiprocess_filter(sas_chunk,target_year):
    sas_chunk = sas_chunk.query('Offer_d30==1 & Affiliated==0 & Vol_grt_out == 0 & Year == {}'.format(target_year))
    print('done')
    return sas_chunk

def mutiprocess_sas2csv_by_year(save_name, target_year, file_name = 'Jinming_TRACE_data.sas7bdat', chunksize=1000000):
    dataset_directory = get_dataset_directory()
    file_path = dataset_directory / file_name
    sas_data = pd.read_sas(file_path,format='sas7bdat',chunksize=chunksize,iterator=True)
    with multiprocessing.get_context('spawn').Pool(processes=multiprocessing.cpu_count()) as pool:
        print('mutiprocessing start')
        result = pool.starmap(mutiprocess_filter,zip(sas_data,itertools.repeat(target_year)))
        #result = pool.imap(mutiprocess_filter,sas_data,chunksize=1)
        pool.close()
        pool.join()
    print('mutiprocessing done, appending dataframes...')
    result = pd.concat(result,ignore_index=True)
    result.to_csv('{}'.format(save_name),compression='zip')
    print('sas2csv done for year {} saving to {}'.format(target_year,save_name))
    
def sas2csv_by_year(save_name, target_year, file_name = 'Jinming_TRACE_data.sas7bdat', chunksize=5000000):
    dataset_directory = get_dataset_directory()
    file_path = dataset_directory / file_name
    sas_data = pd.read_sas(file_path,format='sas7bdat',chunksize=chunksize,iterator=True)
    result = []
    for sas_chunk in sas_data:
        sas_chunk = sas_chunk.query('Offer_d30==1 & Affiliated==0 & Vol_grt_out == 0 & Year == {}'.format(target_year))
        result.append(sas_chunk)
    result = pd.concat(result,ignore_index=True)
    result.to_csv('{}'.format(save_name),compression='zip')

if __name__== "__main__":
    save_name =  str(sys.argv[1])
    target_year = int(sys.argv[2])
    mutiprocess_sas2csv_by_year(save_name,target_year)
