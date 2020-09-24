import os
import pandas as pd

from forwarder.app import scrap_forwarder
from truck.app import scrap_truck

def run():
    df1 = scrap_forwarder()
    df2 = scrap_truck()

    # Create a Pandas Excel writer using XlsxWriter as the engine.
    file_location = os.path.join(os.getcwd(), 'excel/teralogistics_data_scraping.xlsx')
    writer = pd.ExcelWriter(file_location, engine='xlsxwriter')

    # save to excel
    df1.to_excel(
        writer,
        sheet_name='Freight Forwarder'
    )
    df2.to_excel(
        writer,
        sheet_name='Trucking Company'
    )


    # Close the Pandas Excel writer and output the Excel file.
    writer.save()

    print('excel generated...')


if __name__ == '__main__':
    run()