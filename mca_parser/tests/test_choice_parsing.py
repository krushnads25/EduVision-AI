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


def test_infer_course_uses_available_context_without_mca_hardcoding():
    inferred = parser.infer_course(
        choice_code='1234567890',
        course_name='Master in Business Administration',
        fallback_text='Vacancy for MBA admissions',
    )
    assert inferred == 'Master in Business Administration'


def test_parse_page_uses_previous_college_context_for_headerless_continuation_page():
    continuation_text = '\n'.join([
        'M.B.A.(Human Resource',
        '0256916410 60 23 0 0 0',
        'Management)',
        'Category OPEN SC ST VJDT NTB NTC NTD OBC SEBC Total',
        'HU 0 0 2 1 1 2 0 7 4 17',
    ])

    records, university, institute_count = parser.parse_page(
        continuation_text,
        current_university='Savitribai Phule Pune University',
        page_number=19,
        current_college_code='12345',
        current_college_name='Sample College',
    )

    assert institute_count == 1
    assert university == 'Savitribai Phule Pune University'
    assert len(records) == 1
    assert records[0].college_code == '12345'
    assert records[0].college_name == 'Sample College'
    assert records[0].choice_code == '0256916410'
    assert records[0].course == 'M.B.A.(Human Resource Management)'
    assert records[0].intake == 60
