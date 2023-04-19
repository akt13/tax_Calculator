
import configparser
from glob import glob

import camelot
import pandas as pd


def read_credentials(path=r'data_Inputs/config.txt'):
    config = configparser.ConfigParser()
    with open(path, encoding='UTF-8') as cred_file:
        config.read_file(cred_file)
    fname = config.get('credentials', 'form16_fname')
    paswd = config.get('credentials', 'form16_pwd')
    return fname, paswd


def main():
    fname, paswd = read_credentials()
    tables = camelot.read_pdf(
        f"data_Inputs/{fname}", password=paswd, pages='1-end')

    pdf_data = camelot.core.TableList(tables).n

    search_string = {'gross_Income':  'Gross total income (6+8)',
                     'C_80': 'Total deduction under section 80C, 80CCC and 80CCD(1)',
                     'CCD_80': 'Deductions in respect of amount paid/deposited to notified\npension scheme under section 80CCD (1B)',
                     'E_80': 'Deduction in respect of interest on loan taken for higher\neducation under section 80E',
                     'G_80': 'Total Deduction in respect of donations to certain funds,\ncharitable institutions, etc. under section 80G',
                     'TTA_80': 'Deduction in respect of interest on deposits in savings account\nunder section 80TTA',
                     'taxable_Income': 'Total taxable income (9-11)',
                     'tax_payable': 'Net tax payable (17-18)'}
    output_lst = []
    for i in range(pdf_data):
        for _, val in search_string.items():
            df_ = tables[i].df
            data_ = value_finder(df_, val)
            if data_ is not None:
                output_lst.append(data_)
    keys_lst = list(search_string.keys())
    data_extracted = dict(zip(keys_lst, output_lst))
    print(data_extracted)

    taxpnl = glob(("data_Inputs/taxpnl-*.xlsx"))
    df_holding = pd.read_excel(
        taxpnl[0], skiprows=13, sheet_name='Equity', index_col=0)
    df_holding = df_holding.head(3)
    capital_gain = dict(
        zip(df_holding['Unnamed: 1'], df_holding['Unnamed: 2']))

    df_divident = pd.read_excel(
        taxpnl[0], skiprows=14, sheet_name='Equity Dividends', index_col=0)
    divident = df_divident['Net Dividend Amount'].sum()
    dividends = {'dividents': divident}
    data_extracted.update(capital_gain)
    data_extracted.update(dividends)
    print(data_extracted)

    find_tax(data_extracted)


def value_finder(df_, keyword):
    result = df_[df_.eq(keyword).any(1)]
    if not result.empty:
        row_index, col_index = result.stack().index[0]
        next_col_index = (col_index) + 2
        next_col_value = df_.iloc[row_index, next_col_index]
        if next_col_value == '':
            next_col_index = (col_index) + 3
            next_col_value = df_.iloc[row_index, next_col_index]
        # print(keyword, ' : ', next_col_value)
        return next_col_value


def find_tax(data_extracted):
    taxable_income = int(float(
        data_extracted['taxable_Income'])) + int(float(data_extracted['dividents']))
    print(taxable_income)
    if (taxable_income < 500000):
        tax_payable = 0
    print(tax_payable)
