import pandas as pd

from parser import build_output_path, validate_dataframe


def test_build_output_path_uses_pdf_stem_and_output_directory():
    output = build_output_path('samples/demo.pdf', output_dir='out')
    assert output == 'out/demo.csv'


def test_validate_dataframe_accepts_expected_columns_and_non_empty_values():
    df = pd.DataFrame([
        {
            'college_code': '1001',
            'college_name': 'Sample College',
            'choice_code': '1001101010',
            'course': 'MBA',
        }
    ])

    report = validate_dataframe(df, expected_columns=['college_code', 'college_name', 'choice_code', 'course'])
    assert report['missing_columns'] == []
    assert report['empty_rows'] == []
