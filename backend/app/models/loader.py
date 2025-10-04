from dataclasses import dataclass
from typing import List, Dict
import math, numpy as np, torch
from contextlib import nullcontext
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from ..utils.preprocess import normalize, code_mix_normalize

@dataclass
class ModelOutput:
    hate_prob: float
    misinfo_prob: float
    spans: List[Dict]

HATE_KEYWORDS = {"toxic","insult","obscene","identity","attack","threat","hate","abuse"}

# 👉 device
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class ToxicClassifier:
    def __init__(self):
        self.model_name = "unitary/multilingual-toxic-xlm-roberta"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, use_fast=True)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            self.model_name, output_attentions=True
        ).to(DEVICE)
        self.model.eval()

    @torch.inference_mode()
    def infer(self, text: str, lang: str | None = "auto") -> ModelOutput:
        raw_text = text or ""
        t = code_mix_normalize(normalize(raw_text))

        enc = self.tokenizer(
            t, return_tensors="pt", truncation=True, max_length=512, return_offsets_mapping=True
        )
        # send only model inputs to GPU
        inputs = {k: v.to(DEVICE) for k, v in enc.items() if k != "offset_mapping"}
        offsets = enc["offset_mapping"][0].tolist()

        amp = torch.autocast(device_type="cuda", dtype=torch.float16) if DEVICE.type == "cuda" else nullcontext()

        with amp:
            outputs = self.model(**inputs)

        logits = outputs.logits[0]
        probs = torch.sigmoid(logits).float().cpu().numpy()
        labels = [self.model.config.id2label[i].lower() for i in range(len(probs))]

        hate_vals = [probs[i] for i, lab in enumerate(labels) if any(k in lab for k in HATE_KEYWORDS)]
        hate_prob = float(np.mean(hate_vals)) if hate_vals else float(np.clip(probs.mean(), 0.0, 1.0))
        misinfo_prob = float(np.clip(0.15 + 0.25*("!" in t) + 0.2*(len(t) < 120), 0.0, 0.95))

        # attentions: last layer, mean heads
        last_attn = outputs.attentions[-1].mean(dim=1)[0]  # (L, L)
        cls_to_tokens = last_attn[0].float().cpu().numpy()

        input_ids = enc["input_ids"][0].tolist()
        special_ids = set(self.tokenizer.all_special_ids)

        tok_imps = []
        for i, (ofs, tok_id) in enumerate(zip(offsets, input_ids)):
            if i == 0:           # CLS
                continue
            if ofs == (0, 0):    # special/padding
                continue
            if tok_id in special_ids:
                continue
            tok_imps.append((i, cls_to_tokens[i], ofs))

        if not tok_imps:
            start = max(0, min(len(raw_text)-10, int(len(raw_text)*0.3)))
            return ModelOutput(hate_prob, misinfo_prob, [{"start": start, "end": start+min(28, len(raw_text)-start), "weight": 0.75}])

        scores = np.array([s for _, s, _ in tok_imps]); scores -= scores.min()
        if scores.max() > 0: scores /= scores.max()
        triples = [(idx, float(sc), ofs) for (idx, sc, ofs) in zip([i for i,_,_ in tok_imps], scores, [o for *_, o in tok_imps])]

        k = max(4, math.ceil(0.15 * len(triples)))
        top = sorted(triples, key=lambda x: x[1], reverse=True)[:k]
        top = sorted(top, key=lambda x: x[0])

        spans: List[Dict] = []
        cur_s = cur_e = None; cur_w = 0.0
        for _, w, (s, e) in top:
            if cur_s is None: cur_s, cur_e, cur_w = s, e, w; continue
            if s <= cur_e + 1:
                cur_e = max(cur_e, e); cur_w = max(cur_w, w)
            else:
                spans.append({"start": int(cur_s), "end": int(cur_e), "weight": float(cur_w)})
                cur_s, cur_e, cur_w = s, e, w
        if cur_s is not None:
            spans.append({"start": int(cur_s), "end": int(cur_e), "weight": float(cur_w)})

        L = len(raw_text)
        for sp in spans:
            sp["start"] = max(0, min(L, sp["start"]))
            sp["end"]   = max(sp["start"]+1, min(L, sp["end"]))

        return ModelOutput(hate_prob, misinfo_prob, spans)

_model: ToxicClassifier | None = None
def get_model() -> ToxicClassifier:
    global _model
    if _model is None:
        _model = ToxicClassifier()
    return _model
