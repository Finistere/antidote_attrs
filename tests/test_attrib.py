import sys
import textwrap

import attr
import pytest

from antidote import new_container
from antidote_attrs import attrib, UndefinedAttrDependencyError


class Service:
    pass


@pytest.fixture()
def container():
    c = new_container()
    c.update_singletons({Service: Service(), 'parameter': object()})

    return c


def test_simple(container):
    @attr.s
    class Test:
        service = attrib(Service, container=container)
        parameter = attrib(use_name=True, container=container)

    test = Test()

    assert container[Service] is test.service
    assert container['parameter'] is test.parameter


def test_invalid_attrib(container):
    @attr.s
    class BrokenTest:
        service = attrib(container=container)

    with pytest.raises(UndefinedAttrDependencyError):
        BrokenTest()


if sys.version_info >= (3, 6):
    def test_var_annotation(container):
        g = globals().copy()
        g['container'] = container
        exec(
            textwrap.dedent("""
            @attr.s
            class Test:
                service: Service = attrib(container=container)

            test = Test()
            """),
            g
        )
        test = g['test']

        assert container[Service] is test.service
