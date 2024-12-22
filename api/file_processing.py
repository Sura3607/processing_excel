import pandas as pd

def process_file(input_path, output_path):
    """
    Hàm xử lý file Excel.
    - `input_path`: Đường dẫn file gốc.
    - `output_path`: Đường dẫn file sau xử lý.
    """
    try:
        df = pd.read_excel(input_path, header=None)
    except FileNotFoundError:
        raise Exception("File not found. Please check the file path.")
    
    start_row = None
    for i, row in df.iterrows():
        if all(item in row.values for item in ['NGÀY', 'TÊN MÁY']):
            start_row = i
            break

    if start_row is None:
        raise ValueError("Không tìm thấy hàng tiêu đề dữ liệu.")

    header = df.iloc[start_row].values.tolist()
    unique_header = []
    seen = set()
    for item in header:
        original_item = item
        count = 1
        while item in seen:
            item = f"{original_item}_{count}"
            count += 1
        unique_header.append(item)
        seen.add(item)

    df = df.iloc[start_row + 1:].copy()
    df.columns = unique_header

    df.fillna(0, inplace=True)
    df['SL ĐỊNH MỨC'] = pd.to_numeric(df['SL ĐỊNH MỨC'], errors='coerce')
    df['THỜI GIAN SX (giờ)'] = pd.to_numeric(df['THỜI GIAN SX (giờ)'], errors='coerce')
    df['THỜI GIAN SX TT'] = pd.to_numeric(df['THỜI GIAN SX TT'], errors='coerce')

    df['Sản lượng'] = ((df['SL ĐỊNH MỨC'] / df['THỜI GIAN SX (giờ)']) * df['THỜI GIAN SX TT']).round()
    df['Head Count DM'] = df['Nhân sự định biên (công)']
    df['Thời gian\nSXĐM'] = df['THỜI GIAN DM']
    df['Down Time'] = df['THỜI GIAN DỪNG MÁY']
    df['Head Count TT'] = df['Nhân sự thực tế (công)']
    df['Thời gian \nSXTT'] = df['Thời gian\nSXĐM'] - df['Down Time']
    df['Sản lượng ĐM'] = (df['Sản lượng'] / df['Thời gian\nSXĐM'] * df['Head Count TT'] / df['Head Count DM'] * df['Thời gian \nSXTT']).round()
    df['Sản lượng TT'] = df['SLSX THỰC TẾ']
    df['HIỆU SUẤT'] = (df['Sản lượng TT'] / df['Sản lượng ĐM']).round()
    df['% Downtime'] = (df['Down Time'] / df['Thời gian \nSXTT']).round()

    # Xuất file Excel ra memory
    with pd.ExcelWriter(output_path) as writer:
        for ma_may in df['TÊN MÁY'].unique():
            df_ma_may = df[df['TÊN MÁY'] == ma_may].copy()
            columns_to_keep = ['NGÀY', 'TÊN MÁY', 'MÃ HÀNG', 'TÊN SP','Sản lượng','Head Count DM','Thời gian\nSXĐM','Down Time','Head Count TT','Thời gian \nSXTT','Sản lượng ĐM','Sản lượng TT','HIỆU SUẤT','% Downtime']
            df_ma_may = df_ma_may[columns_to_keep]

            sheet_name = str(ma_may)[:31]
            df_ma_may.to_excel(writer, sheet_name=sheet_name, index=False)
            worksheet = writer.sheets[sheet_name]
            
            # Định dạng cột HIỆU SUẤT và % Downtime thành phần trăm
            for col_name in ['HIỆU SUẤT', '% Downtime']:
                try:
                    col_idx = df_ma_may.columns.get_loc(col_name) + 1
                    for cell in worksheet.iter_cols(min_col=col_idx, max_col=col_idx, min_row=2):
                        for c in cell:
                            c.number_format = '0%'
                except KeyError:
                    print(f"Warning: Column '{col_name}' not found in sheet {sheet_name}")