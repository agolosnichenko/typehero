import typer


def test_package_imports():
    assert typer.__doc__ is not None
