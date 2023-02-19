import torch
from transformers import AutoTokenizer, AutoModelWithLMHead
import gradio as gr

tokenizer = AutoTokenizer.from_pretrained('fine_tuning/output-small')
model = AutoModelWithLMHead.from_pretrained('fine_tuning/output-small')

def predict(input, history=[]):
    new_user_input_ids = tokenizer.encode(input + tokenizer.eos_token, return_tensors='pt')
    bot_input_ids = torch.cat([torch.LongTensor(history), new_user_input_ids], dim=-1)
    history = model.generate(
        bot_input_ids, max_length=1000,
        pad_token_id=tokenizer.eos_token_id
    ).tolist()
    response=tokenizer.decode(history[0]).split('<|endoftext|>')
    if '' in response:
        response.remove('')
    print(response)

    html="<div class='chatbot'>"
    for m, msg in enumerate(response):
        cls='user' if m%2==0 else 'elon'
        name='You' if m%2==0 else 'ElonBot'
        html+=f'<div class="msg {cls}">{name}: {msg}</div>'

    html+='</div>'
    return html, history

css="""
h1 {color:white;}
.chatbox {display:flex; flex-direction:column; height:1800px;}
.msg{padding:4px; margin-bottom:4px; border-radius:4px; width:80%;}
.msg.user{background-color:#ee7400; color:white;}
.msg.elon{background-color:#4b5563; margin-left:20%; text-align:right;}
.footer{display:none !important;}
"""

gr.Interface(fn=predict,
             theme='default',
             inputs=[gr.inputs.Textbox(placeholder='Hello'), 'state'],
             outputs=['html', 'state'],
             css=css).launch(share=True)
