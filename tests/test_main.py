import application


def test_main(monkeypatch):
    class FA:
        pass

    monkeypatch.setattr(application, "create_app", lambda: FA())

    import main

    assert isinstance(main.app, FA)
