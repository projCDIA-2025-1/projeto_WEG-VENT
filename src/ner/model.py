import torch
import torch.nn as nn
from transformers import AutoModel, AutoTokenizer

class Model(nn.Module):
    idx_to_label = {
        0:          '0',
        1:          'STARTING_MATERIAL',
        2:          'REAGENT_CATALYST',
        3:          'REACTION_PRODUCT',
        4:          'SOLVENT',
        5:          'OTHER_COMPOUND',
        6:          'TIME',
        7:          'TEMPERATURE',
        8:          'YIELD_PERCENT',
        9:          'YIELD_OTHER',
        10:         'EXAMPLE_LABEL',
        11:         'REACTION_STEP',
        12:         'WORKUP'
    }

    def __init__(self):
        super(Model, self).__init__()
        self.encoder = AutoModel.from_pretrained("dmis-lab/biobert-v1.1")
        self.fc = nn.Linear(self.encoder.config.hidden_size, 13, bias=False)

        self.load_state_dict(torch.load('./src/ner/ner_model.pt', map_location=torch.device('cpu')))
        self.tokenizer = AutoTokenizer.from_pretrained("dmis-lab/biobert-v1.1")


    def forward(self, input_ids, attention_mask, **kwargs):
        outputs = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
        logits = self.fc(outputs.last_hidden_state) * 10
        return logits
    
    @torch.inference_mode()
    def predict(self, texts: list[str] | str):
        if isinstance(texts, str):
            texts = [texts]
        inputs = self.tokenizer(texts, padding=True, truncation=True, return_tensors="pt")
        input_ids = inputs["input_ids"]
        attention_mask = inputs["attention_mask"]

        preds = self.forward(input_ids, attention_mask)
        preds = preds.argmax(dim=-1).cpu()

        # Convert predictions labels to ranges
        return_list = []
        for batch_pred, batch_tokens in zip(preds, input_ids):
            text = ''
            return_list.append([])

            diffs = torch.diff(batch_pred, prepend=torch.tensor([0]), append=torch.tensor([0]))
            diff_locs = torch.where(diffs != 0)[0].tolist()
            prev_loc = 0
            for loc in diff_locs:
                if loc == 0:
                    continue
                curr_text = self.tokenizer.decode(batch_tokens[prev_loc:loc])
                if batch_pred[loc-1].item() != 0:
                    return_list[-1].append({
                        'text': curr_text,
                        'label': self.idx_to_label[batch_pred[loc-1].item()],
                        'start': len(text),
                        'end': len(text) + len(curr_text)
                    })
                text += curr_text
                prev_loc = loc
        
        if len(return_list) == 1:
            return_list = return_list[0]
        return return_list

    def transform_text(self, texts: list[str] | str):
        return self.tokenizer.batch_decode(
            self.tokenizer(texts, padding=True, truncation=True, return_tensors="pt")["input_ids"],
            skip_special_tokens=True
        )

