from app.importers.seat_matrix_importer import SeatMatrixImporter
import pandas as pd

df = pd.read_csv('parser_V3/output.csv', dtype=str, keep_default_na=False)
print('original cols', list(df.columns))
df2 = SeatMatrixImporter.normalize_columns(df)
print('normalized cols', list(df2.columns))
print('cap_seats present?', 'cap_seats' in df2.columns)
print('college_name present?', 'college_name' in df2.columns)
print('choice_code present?', 'choice_code' in df2.columns)
