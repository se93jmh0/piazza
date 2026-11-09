import tracemalloc

import application

tracemalloc.start()


"""
def test_main(monkeypatch):
    class FA:
        pass

    monkeypatch.setattr(application, "create_app", lambda _: FA())

    import main

    assert isinstance(main.app, FA)
"""