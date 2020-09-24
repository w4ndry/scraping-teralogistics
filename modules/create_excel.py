import os
import json
import pandas as pd

def create_excel(files):
    print('start generated excel...')

    datas = []
    for file in files:
        with open(file) as json_file:
            data = json.load(json_file)
            datas.append(data)
    
    df = pd.DataFrame(datas)
    # replace column name and uppercas first letter
    df.columns = [x.replace('_', ' ').title() for x in df.columns]
    # add index labe
    df.index.name = 'No'
    # start index with 1
    df.index = df.index + 1
    
    return df