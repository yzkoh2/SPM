def test_intentional_backend_failure():
    """This test should fail and block the pipeline"""
    assert False, "CI Test: Backend test failure should block merge!"
