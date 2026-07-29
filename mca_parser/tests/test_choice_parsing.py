import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location('parser', Path(__file__).resolve().parents[1] / 'parser.py')
parser = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parser)


def test_choice_code_with_suffix_and_course_line():
    chunk_lines = [
        '0267224170U Master in Computer Application 120 6 0 0 24',
        'Category OPEN SC ST VJDT NTB NTC NTD OBC SEBC Total',
    ]
    choice = parser.extract_choice(chunk_lines)
    assert choice['choice_code'] == '0267224170U'
    assert choice['course'] == 'Master in Computer Application'
    assert choice['intake'] == 120
    assert choice['si_seats'] == 6


def test_choice_code_with_tfws_suffix_variants():
    chunk_lines = [
        '1614524271UT Master of Computer Applications 60 13 3 0 12',
        'Category OPEN SC ST VJDT NTB NTC NTD OBC SEBC Total',
    ]
    choice = parser.extract_choice(chunk_lines)
    assert choice['choice_code'] == '1614524271UT'
    assert choice['course'] == 'Master of Computer Applications'
    assert choice['intake'] == 60
