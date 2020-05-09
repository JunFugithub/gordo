import sys
import json
import pytest

from io import StringIO

from gordo.cli.exceptions_reporter import (
    ReportLevel,
    ExceptionsReporter,
    DEFAULT_EXIT_CODE,
)


def test_report_level():
    level = ReportLevel.get_by_name("MESSAGE")
    assert level == ReportLevel.MESSAGE
    level = ReportLevel.get_by_name("DIFFERENT")
    assert level is None
    level = ReportLevel.get_by_name("DIFFERENT", ReportLevel.MESSAGE)
    assert level == ReportLevel.MESSAGE
    levels = ReportLevel.get_names()
    assert len(levels) == 3


class _Test1Exception(Exception):
    pass


class _Test2Exception(Exception):
    pass


class _Test3Exception(_Test1Exception):
    pass


@pytest.fixture
def reporter1():
    return ExceptionsReporter(((_Test1Exception, 110),))


def test_sort_exceptions():
    exceptions = ((Exception, 10), (IOError, 20), (FileNotFoundError, 30))
    sorted_exceptions = ExceptionsReporter.sort_exceptions(exceptions)
    assert sorted_exceptions == [
        (FileNotFoundError, 30),
        (OSError, 20),
        (Exception, 10),
    ]


def test_reporter1(reporter1):
    assert reporter1.exception_exit_code(_Test1Exception) == 110
    assert reporter1.exception_exit_code(_Test2Exception) == DEFAULT_EXIT_CODE
    assert reporter1.exception_exit_code(_Test3Exception) == 110


def report(e, reporter, report_level, report_file, **kwargs):
    try:
        raise e
    except Exception:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        reporter.report(
            report_level, exc_type, exc_value, exc_traceback, report_file, **kwargs
        )


def report_to_string(e, reporter, report_level, **kwargs):
    sio = StringIO()
    report(e, reporter, report_level, sio, **kwargs)
    value = sio.getvalue()
    return json.loads(value)


def test_with_message_report_level(reporter1):
    result = report_to_string(
        _Test1Exception("Test message"), reporter1, ReportLevel.MESSAGE
    )
    assert result == {
        "type": "_Test1Exception",
        "message": "Test message",
    }


def test_with_type_report_level(reporter1):
    result = report_to_string(
        _Test1Exception("Test message"), reporter1, ReportLevel.TYPE
    )
    assert result == {
        "type": "_Test1Exception",
    }


def test_with_exit_code_report_level(reporter1):
    result = report_to_string(
        _Test1Exception("Test message"), reporter1, ReportLevel.EXIT_CODE
    )
    assert result == {}


def test_with_unicode_chars(reporter1):
    result = report_to_string(
        _Test1Exception("你好 world!"), reporter1, ReportLevel.MESSAGE
    )
    assert result == {
        "type": "_Test1Exception",
        "message": "?? world!",
    }


def test_with_max_message_len(reporter1):
    result = report_to_string(
        _Test1Exception("Hello world!"),
        reporter1,
        ReportLevel.MESSAGE,
        max_message_len=8,
    )
    assert result == {
        "type": "_Test1Exception",
        "message": "Hello...",
    }
    result = report_to_string(
        _Test1Exception("Hello world!"),
        reporter1,
        ReportLevel.MESSAGE,
        max_message_len=20,
    )
    assert result == {
        "type": "_Test1Exception",
        "message": "Hello world!",
    }
    result = report_to_string(
        _Test1Exception("Hello"), reporter1, ReportLevel.MESSAGE, max_message_len=4
    )
    assert result == {
        "type": "_Test1Exception",
        "message": "",
    }
