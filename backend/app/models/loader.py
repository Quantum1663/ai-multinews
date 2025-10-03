from dataclasses import dataclass
import random
from ..utils.preprocess import normalize, code_mix_normalize

@dataclass
class ModelOutput:
    hate_prob: float
    misinfo_prob: float
    spans: list  # [{start,end,weight}]

class TextModel:
    def __init__(self):
        # TODO: load real model here (torch/onnx)
        self.ready = True

    def infer(self, text: str, lang: str|None="auto") -> ModelOutput:
        t = code_mix_normalize(normalize(text))
        # Dummy logic: probabilities based on keywords/length to keep UI working
        misinfo = 0.15 + 0.25*("!" in t) + 0.2*(len(t) < 120)
        hate = 0.05 + 0.3*any(k in t for k in ["hate","kill","banish","vermin"])
        misinfo = float(min(misinfo, 0.95))
        hate = float(min(hate, 0.95))
        # random highlight span for demo
        start = max(0, min(len(text)-10, int(len(text)*0.3)))
        span = {"start": start, "end": start+min(28, len(text)-start), "weight": 0.8}
        return ModelOutput(hate_prob=hate, misinfo_prob=misinfo, spans=[span])

_model: TextModel|None = None

def get_model() -> TextModel:
    global _model
    if _model is None:
        _model = TextModel()
    return _model
