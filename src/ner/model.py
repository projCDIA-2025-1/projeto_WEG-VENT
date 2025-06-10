import numpy as np

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

        self.load_state_dict(torch.load('model/ner_model.pt'))
        self.tokenizer = AutoTokenizer.from_pretrained("dmis-lab/biobert-v1.1")


    def forward(self, input_ids, attention_mask, **kwargs):
        outputs = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
        logits = self.fc(outputs.last_hidden_state) * 10
        return logits
    
    @torch.inference_mode()
    def predict(self, texts: list[str] | str):
        is_string = False
        if isinstance(texts, str):
            texts = [texts]
            is_string = True
        inputs = self.tokenizer(texts, padding=True, truncation=True, return_tensors="pt")

        preds = []
        input_ids = []
        offsets = []
        for text in texts:
            tokens = self.tokenizer(text, return_tensors="pt", return_offsets_mapping=True)
            input_id = tokens['input_ids']
            attention_mask = tokens['attention_mask']
            input_ids.append(input_id[0])
            offsets.append(tokens['offset_mapping'][0])
            # print(input_id.shape)
            # if input_id.shape[1] <= 512:
            #     pred = self.forward(input_id, attention_mask)
            #     preds.append(pred.argmax(dim=-1).cpu()[0])
            # If the input is too long, we split it into chunks of 512 tokens
            chunk_size = 512
            # overlap = 128
            # chunk_size = 128
            overlap = chunk_size // 4
            current_preds = []
            ids_check = []
            for i in range(0, input_id.shape[1], chunk_size // 2):
                end = int(min(i + chunk_size, input_id.shape[1]))
                start = i
                pred_start = overlap if start != 0 else 0
                pred_end = end - start - overlap  if end != input_id.shape[1] else end - start
                
                chunk_input_ids = input_id[:, start:end]
                chunk_attention_mask = attention_mask[:, start:end]
                pred = self.forward(chunk_input_ids, chunk_attention_mask)[0, pred_start:pred_end]
                pred = pred.argmax(dim=-1).cpu()
                current_preds.append(pred)
                ids_check.append(chunk_input_ids[0, pred_start:pred_end])

                if end == input_id.shape[1]:
                    break
            if not (torch.cat(ids_check, dim=0) == input_id).all():
                raise ValueError(f"Input IDs do not match the original input IDs for text: {text}. Please check the tokenization process.")
            if end != input_id.shape[1]:
                raise ValueError(f"Input text '{text}' is too long, please split it into smaller chunks.")
            preds.append(torch.cat(current_preds, dim=0))
            if len(preds[-1]) != input_id.shape[1]:
                raise ValueError(f"Length of current_preds ({(preds[-1].shape)}) does not match input_id length ({input_id.shape}).")

        return_list = []
        for batch_pred, batch_tokens, batch_offset, original_text in zip(preds, input_ids, offsets, texts):
            diffs = torch.diff(batch_pred, prepend=torch.tensor([0]))
            diffs = torch.concat((diffs, torch.tensor([1])))
            diff_locs = torch.where(diffs != 0)[0].tolist()
            prev_loc = 0
            
            return_list.append([])
            for loc in diff_locs:
                if loc == 0:
                    continue

                if batch_pred[loc-1].item() != 0:
                    start = batch_offset[prev_loc][0].item()
                    end = batch_offset[loc-1][1].item()

                    if start < end:
                        return_list[-1].append({
                            'text':     original_text[start:end],
                            'label':    self.idx_to_label[batch_pred[loc-1].item()],
                            'start':    start,
                            'end':      end,
                        })
                prev_loc = loc

        if is_string:
            return_list = return_list[0]
        return return_list

    def transform_text(self, texts: list[str] | str):
        return texts
