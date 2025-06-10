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
        for text in texts:
            tokens = self.tokenizer(text, return_tensors="pt")
            input_id = tokens['input_ids']
            attention_mask = tokens['attention_mask']
            input_ids.append(input_id[0])
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
                print(start, end, pred_start, pred_end, pred.shape)
                if end == input_id.shape[1]:
                    break
            if not (torch.cat(ids_check, dim=0) == input_id).all():
                raise ValueError(f"Input IDs do not match the original input IDs for text: {text}. Please check the tokenization process.")
            if end != input_id.shape[1]:
                raise ValueError(f"Input text '{text}' is too long, please split it into smaller chunks.")
            preds.append(torch.cat(current_preds, dim=0))
            if len(preds[-1]) != input_id.shape[1]:
                raise ValueError(f"Length of current_preds ({(preds[-1].shape)}) does not match input_id length ({input_id.shape}).")
            # Concatenate the predictions from all chunks
        # preds = torch.stack(preds)

        return_list = []
        for batch_pred, batch_tokens, original_text in zip(preds, input_ids, texts):
            diffs = torch.diff(batch_pred, prepend=torch.tensor([0]))
            diffs = torch.concat((diffs, torch.tensor([1])))
            diff_locs = torch.where(diffs != 0)[0].tolist()
            prev_loc = 0
            
            decoded_text = ''
            decoded_len = 0
            text_sections = []
            return_list.append([])
            for loc in diff_locs:
                if loc == 0:
                    continue
                start = decoded_len + len(decoded_text)
                if self.tokenizer.unk_token_id not in batch_tokens[prev_loc:loc]:
                    curr_text = self.tokenizer.decode(batch_tokens[prev_loc:loc], skip_special_tokens=True)
                    curr_len = len(curr_text)
                else:
                    unk_locs = torch.where(batch_tokens[prev_loc:loc] == self.tokenizer.unk_token_id)[0]
                    # unk_locs = torch.concat((unk_locs, torch.tensor([loc-prev_loc])))
                    unk_prev_loc = prev_loc
                    curr_len = 0
                    for unk_loc in unk_locs:
                        curr_text = self.tokenizer.decode(batch_tokens[unk_prev_loc:unk_prev_loc+unk_loc], skip_special_tokens=True)
                        curr_len += len(curr_text)

                        # text_sections.append(decoded_text+curr_text)
                        text_sections.append(decoded_text+curr_text)
                        decoded_len += len(text_sections[-1])
                        decoded_text = '™'

                        unk_prev_loc += unk_loc + 1

                        # curr_text = self.tokenizer.decode(batch_tokens[unk_prev_loc-1:loc], skip_special_tokens=True)
                        # curr_len += len(curr_text)
                    curr_text = self.tokenizer.decode(batch_tokens[unk_prev_loc:loc], skip_special_tokens=True)
                    curr_len += max(len(curr_text), 1)

                if batch_pred[loc-1].item() != 0 and curr_len != 0:                    
                    return_list[-1].append({
                        'text':     '',
                        'label':    self.idx_to_label[batch_pred[loc-1].item()],
                        'start':    start,
                        'end':      start + curr_len
                    })
                decoded_text += curr_text
                prev_loc = loc
            text_sections.append(decoded_text)

            # Transform the original text to an intermediate form
            np_text = np.array(list(original_text), dtype='<U1')
            is_space = np.char.isspace(np_text)
            treated_text = ''.join(np_text[~is_space])
            real_text_pos = np.where(~is_space)[0]

            # Transform the decoded text to an intermediate form
            np_decoded_text = np.array(list(text_sections[0]), dtype='<U1')
            is_not_space = (~np.char.isspace(np_decoded_text))
            mod_decoded_text = ''.join(np_decoded_text[is_not_space]).replace('™', '')
            # print(mod_decoded_text)
            pos_precount = [is_not_space.astype(int)]
            if mod_decoded_text.replace('™', '') not in treated_text:
                raise ValueError(f"Decoded text '{mod_decoded_text}' not found in treated text '{treated_text}'")

            for i in range(1, len(text_sections)):
                np_decoded_text = np.array(list(text_sections[i]), dtype='<U1')
                is_not_space = (~np.char.isspace(np_decoded_text))
                curr_mod_decoded_text = ''.join(np_decoded_text[is_not_space]).replace('™', '')
                pos_precount.append(is_not_space.astype(int))

                if curr_mod_decoded_text.replace('™', '') not in treated_text:
                    raise ValueError(f"Decoded text '{curr_mod_decoded_text}' not found in treated text '{treated_text}'")
                start_unk = len(mod_decoded_text)
                end_unk = start_unk + treated_text[start_unk:].find(curr_mod_decoded_text)
                pos_precount[-1][0] += end_unk - start_unk - 1
                mod_decoded_text += treated_text[start_unk:end_unk]
                mod_decoded_text += curr_mod_decoded_text.replace('™', '')
            decoded_text_pos = np.concatenate(pos_precount).cumsum() - 1
            # Check if the decoded text matches the treated text
            if mod_decoded_text != treated_text:
                raise ValueError(f"Decoded text '{mod_decoded_text}' does not match treated text '{treated_text}'")
            
            # Adjust the start and end positions of the items in return_list
            for item in return_list[-1]:
                start = real_text_pos[decoded_text_pos[item['start']]]
                # end = real_text_pos[decoded_text_pos[min(item['end'], len(decoded_text_pos))]-1]+1
                end = real_text_pos[decoded_text_pos[item['end']-1]]+1
                # print(item['end']-1)
                item['start'] = start
                item['end'] = end
                item['text'] = original_text[start:end]
                
        if is_string:
            return_list = return_list[0]
        return return_list

    def transform_text(self, texts: list[str] | str):
        return texts
