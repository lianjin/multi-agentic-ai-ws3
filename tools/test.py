from .singapore_time import singapore_time
from .singapore_weather import singapore_weather
from .singapore_traffic import singapore_traffic


def test_print_all():
    print(singapore_time())
    print("\n" + singapore_weather())
    print("\n" + singapore_traffic())
