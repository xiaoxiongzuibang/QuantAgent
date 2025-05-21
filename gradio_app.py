import gradio as gr
import json
from strategy_agent import *

system_prompt = {"role": "system", "content": "You are a quant trading assistant."}

def chat(user_input, history):
    history_openai = [system_prompt] + history + [{"role": "user", "content": user_input}]
    assistant = gpt(history_openai)
    reply = assistant.content
    image = None
    updated_history = history + [
        {"role": "user", "content": user_input},
        {"role": "assistant", "content": reply},
    ]

    if assistant.function_call:
        fn = assistant.function_call.name
        args = json.loads(assistant.function_call.arguments or "{}")

        if fn == "plot_stock_chart":
            res = plot_line_chart(**args)  # ✅ 用简单折线图代替蜡烛图
            reply = "✅ Chart generated." if "image" in res else res.get("error", "Failed.")
            updated_history[-1]["content"] = reply
            return updated_history, res.get("image")

    return updated_history, image


with gr.Blocks(title="量化策略助手") as demo:
    gr.Markdown("## 📈 量化策略助手 – 自然语言生成策略 + 回测")

    with gr.Row(equal_height=True):
        with gr.Column(scale=2):
            chatbot = gr.Chatbot(label="对话", height=500, type="messages")
            msg = gr.Textbox(placeholder="请输入策略描述...", show_label=False)
        with gr.Column(scale=1):
            image = gr.Image(label="📊 Chart", type="filepath", height=300)
    
    msg.submit(fn=chat, inputs=[msg, chatbot], outputs=[chatbot, image])
    gr.Button("🗑️ 清除对话").click(lambda: ([], None), outputs=[chatbot, image])

demo.launch()
