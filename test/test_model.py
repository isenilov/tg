from src.model import CategorizationModel


def test_model_embed():
    model = CategorizationModel()
    result = model._embed("Some text")
    assert len(result) == 512
