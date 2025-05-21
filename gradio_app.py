import gradio as gr
import json
from strategy_agent import gpt, plot_line_chart, get_metrics, update_strategy_params, run_backtest

# Define your system prompt here:
SYSTEM_PROMPT = {"role": "system", "content": "You are a quant trading assistant."}

def chat(user_input, history):
    # Build the OpenAI messages list
    messages = [SYSTEM_PROMPT] + history + [{"role": "user", "content": user_input}]
    updated_history = history + [{"role": "user", "content": user_input}]

    image = None
    metrics_table = None

    # First call
    assistant = gpt(messages)
    if assistant.content:
        updated_history.append({"role": "assistant", "content": assistant.content})

    # Handle any function calls (chain-call)
    while assistant.function_call:
        fn = assistant.function_call.name
        args = json.loads(assistant.function_call.arguments or "{}")

        if fn == "plot_stock_chart":
            res = plot_line_chart(**args)
            image = res.get("image")

        elif fn == "get_metrics":
            res = get_metrics(**args)
            if "error" not in res:
                metrics_table = [[k, v] for k, v in res.items()]

        elif fn == "update_strategy_params":
            res = update_strategy_params(**args)

        elif fn == "run_backtest":
            res = run_backtest(args["strategy"])
            image = res.get("image")

        # Tell the model what the function returned
        messages.append({
            "role": "function",
            "name": fn,
            "content": json.dumps(res, ensure_ascii=False)
        })

        # Run GPT again to see if it wants another call or a final reply
        assistant = gpt(messages)
        if assistant.content:
            updated_history.append({"role": "assistant", "content": assistant.content})

    return updated_history, image, metrics_table


with gr.Blocks(title="Quant Strategy Assistant") as demo:
    gr.Markdown("## 📈 Quant Strategy Assistant")

    with gr.Row():
        with gr.Column(scale=2):
            chatbot = gr.Chatbot(type="messages", label="Chat history")
            userbox = gr.Textbox(placeholder="Enter your strategy or request…", show_label=False)
        with gr.Column(scale=1):
            image   = gr.Image(label="📊 Chart", type="filepath")
            metrics = gr.Dataframe(label="📈 Metrics", headers=["Metric", "Value"], interactive=False)

    # Wire up submit & clear
    userbox.submit(chat, inputs=[userbox, chatbot], outputs=[chatbot, image, metrics])
    gr.Button("🗑️ Clear").click(lambda: ([], None, None), outputs=[chatbot, image, metrics])

demo.launch()

