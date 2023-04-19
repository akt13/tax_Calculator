
import configparser
from glob import glob

import camelot
import pandas as pd

config = configparser.ConfigParser()
config.readfp(open(r'data_Inputs/config.txt'))
paswd = config.get('credentials', 'form16_pwd')
print(paswd)


form16 = glob(("data_Inputs/*.pdf"))
tables = camelot.read_pdf(form16[0], password=paswd, pages='1-end')


n = camelot.core.TableList(tables).n


def value_finder(df, keyword):
    result = df[df.eq(keyword).any(1)]
    if not result.empty:
        row_index, col_index = result.stack().index[0]
        next_col_index = (col_index) + 2
        next_col_value = df.iloc[row_index, next_col_index]
        if (next_col_value == ''):
            next_col_index = (col_index) + 3
            next_col_value = df.iloc[row_index, next_col_index]
        # print(keyword, ' : ', next_col_value)
        return next_col_value


search_string = {'gross_Income':  'Gross total income (6+8)',
                 'C_80': 'Total deduction under section 80C, 80CCC and 80CCD(1)',
                 'CCD_80': 'Deductions in respect of amount paid/deposited to notified\npension scheme under section 80CCD (1B)',
                 'E_80': 'Deduction in respect of interest on loan taken for higher\neducation under section 80E',
                 'G_80': 'Total Deduction in respect of donations to certain funds,\ncharitable institutions, etc. under section 80G',
                 'TTA_80': 'Deduction in respect of interest on deposits in savings account\nunder section 80TTA',
                 'taxable_Income': 'Total taxable income (9-11)',
                 'tax_payable': 'Net tax payable (17-18)'}
outputLst = []
for i in range(n):
    for key, val in search_string.items():
        df = tables[i].df
        data_ = value_finder(df, val)
        if data_ != None:
            outputLst.append(data_)
keysList = list(search_string.keys())
data_extracted = dict(zip(keysList, outputLst))
print(data_extracted)


taxpnl = glob(("data_Inputs/taxpnl-*.xlsx"))
df_holding = pd.read_excel(
    taxpnl[0], skiprows=13, sheet_name='Equity', index_col=0)
df_holding = df_holding.head(3)
capitalGain = dict(zip(df_holding['Unnamed: 1'], df_holding['Unnamed: 2']))

df_divident = pd.read_excel(
    taxpnl[0], skiprows=14, sheet_name='Equity Dividends', index_col=0)
divident = df_divident['Net Dividend Amount'].sum()
dividents = {'dividents': divident}
data_extracted.update(capitalGain)
data_extracted.update(dividents)
print(data_extracted)


def find_tax(data_extracted):
    taxable_income = int(float(
        data_extracted['taxable_Income'])) + int(float(data_extracted['dividents']))
    print(taxable_income)
    if (taxable_income < 500000):
        tax_payable = 0
    print(tax_payable)


find_tax(data_extracted)
