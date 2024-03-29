
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
        return next_col_value


def find_tax(data_extracted):
    taxable_income = int(float(
        data_extracted['taxable_Income'])) + int(float(data_extracted['dividends']))
    if taxable_income < 500000:
        tax_payable = 0
    return taxable_income, tax_payable
    


def parse_form16(fname, paswd):
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
    return data_extracted


def parse_zerodha_pnl(fname):
    taxpnl_fname = f"data/{fname}"
    df_holding = pd.read_excel(
        taxpnl_fname, skiprows=13,
        sheet_name='Equity', index_col=0)
    df_holding = df_holding.head(3)
    capital_gain = dict(
        zip(df_holding['Unnamed: 1'], df_holding['Unnamed: 2']))

    df_divident = pd.read_excel(
        taxpnl_fname, skiprows=14, sheet_name='Equity Dividends', index_col=0)
    dividend = df_divident['Net Dividend Amount'].sum()
    dividends = {'dividends': dividend}
    return capital_gain, dividends


def gen_report(data, fname):
    items = data.items()
    report = pd.DataFrame({'component': [i[0] for i in items], 'amount in Rs': [i[1] for i in items]})
    print(report)
    report.to_csv(f'reports/{fname}', index=False)


def main():
    zerodha_fname, fname, paswd = read_credentials()
    data_extracted = parse_form16(fname, paswd)
    gen_report(data_extracted, 'form16_report.csv')

    capital_gain, dividends = parse_zerodha_pnl(zerodha_fname)
    gen_report(capital_gain, 'capital_gain_report.csv')
    gen_report(dividends, 'dividends_report.csv')
    
    data_extracted.update(capital_gain)
    data_extracted.update(dividends)
    taxable_income, tax_payable = find_tax(data_extracted)
    data_extracted['taxable_Income'] = taxable_income
    data_extracted['tax_payable'] = tax_payable
    print(f"taxable_income = Rs {taxable_income}")
    print(f"Tax payable = {tax_payable}")
    gen_report(data_extracted, 'final_report.csv')


if __name__ == '__main__':
    main()
