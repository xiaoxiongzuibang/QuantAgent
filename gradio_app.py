import gradio as gr
import json
from strategy_agent import gpt, run_backtest, update_strategy_params, memory

system_prompt = {"role": "system", "content": "You are a quant trading assistant."}

def chat(user_input, history):
    history_openai = [system_prompt] + history + [{"role": "user", "content": user_input}]
    assistant = gpt(history_openai)
    reply = assistant.content
    image = None

    if assistant.function_call:
        fn = assistant.function_call.name
        args = json.loads(assistant.function_call.arguments or "{}")

        if fn == "update_strategy_params":
            update_strategy_params(**args)
            missing = [k for k, v in memory["strategy"].items() if v is None]
            reply = "✅ 参数已更新。" if not missing else f"📌 还缺这些参数：{missing}"

        elif fn == "run_backtest":
            result = run_backtest(memory["strategy"])
            if "error" in result:
                reply = f"⚠️ 回测失败：{result['error']}"
            else:
                reply = result["summary"]
                image = result["image"]

    updated_history = history + [
        {"role": "user", "content": user_input},
        {"role": "assistant", "content": reply},
    ]
    return updated_history, image

with gr.Blocks(title="量化策略助手") as demo:
    gr.Markdown("## 📈 量化策略助手 – 自然语言生成策略 + 回测")

    with gr.Row(equal_height=True):
        with gr.Column(scale=2):
            chatbot = gr.Chatbot(label="对话", height=500, type="messages")
            msg = gr.Textbox(placeholder="请输入策略描述...", show_label=False)
        with gr.Column(scale=1):
            image = gr.Image(label="📊 回测图", type="filepath", height=500)

    msg.submit(fn=chat, inputs=[msg, chatbot], outputs=[chatbot, image])
    gr.Button("🗑️ 清除对话").click(lambda: ([], None), outputs=[chatbot, image])

demo.launch()
