
import configparser

import camelot
import pandas as pd

from search_lookup import search_string


def read_credentials(path=r'data/config.txt'):
    config = configparser.ConfigParser()
    with open(path, encoding='UTF-8') as cred_file:
        config.read_file(cred_file)
    fname = config.get('credentials', 'form16_fname')
    paswd = config.get('credentials', 'form16_pwd')
    zerodha_taxpnl = config.get('credentials', 'zerodha_taxpnl')

    return zerodha_taxpnl, fname, paswd


def value_finder(df_, keyword):
    result = df_[df_.eq(keyword).any(axis=1)]
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
        data_extracted['taxable_Income'])) + int(float(data_extracted['dividends']))
    print(taxable_income)
    if taxable_income < 500000:
        tax_payable = 0
    print(tax_payable)


def main():
    zerodha_fname, fname, paswd = read_credentials()
    tables = camelot.read_pdf(
        f"data/{fname}", password=paswd, pages='1-end')

    pdf_data = camelot.core.TableList(tables).n

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

    taxpnl_fname = f"data/{zerodha_fname}"
    df_holding = pd.read_excel(
        taxpnl_fname, skiprows=13,
        sheet_name='Equity', index_col=0)
    df_holding = df_holding.head(3)
    capital_gain = dict(
        zip(df_holding['Unnamed: 1'], df_holding['Unnamed: 2']))

    df_divident = pd.read_excel(
        taxpnl_fname, skiprows=14, sheet_name='Equity Dividends', index_col=0)
    divident = df_divident['Net Dividend Amount'].sum()
    dividends = {'dividends': divident}
    data_extracted.update(capital_gain)
    data_extracted.update(dividends)
    print(data_extracted)

    find_tax(data_extracted)


if __name__ == '__main__':
    main()
