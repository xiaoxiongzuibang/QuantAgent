from openai_agent.functions import *
from openai import OpenAI
import os, json, uuid, datetime as dt

from agent_core.data.price_data import *
from agent_core.data.fundamental_data import *
from agent_core.data.macro_data import *
from agent_core.plot.data_plot import *

memory = {"strategy": {k: None for k in
           ("indicator","buy_rule","sell_rule","ticker","start","end")}}

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def gpt(msgs: list) -> str:
    return client.chat.completions.create(
        model="gpt-4o",
        messages=msgs,
        functions=function_schemas,
        function_call="auto"
    ).choices[0].message

msgs=[{
    "role":"system",
    "content":
    "You are a quant trading assistant good at factor investment. "
    "You can use your knowledge and ai agent to deal with tasks in factor investment, such as test a factor and try to find factors."
    "You know that we regard the factor as a stochatic processe."
    }]
print("===AI AGENT===: Hi！I'm an agent good at factor investment. How can I help you？Maybe I can show you what is factor investment?（exit for end chat）\n")

while True:
    user_input=input("User: "); 
    if user_input.lower() in {"exit","quit"}: break
    msgs.append({"role":"user","content":user_input})

    assistant=gpt(msgs); msgs.append(assistant)

    while assistant.function_call:
        function_name=assistant.function_call.name
        args=json.loads(assistant.function_call.arguments or "{}")

        if function_name=="update_strategy_params":
            memory["strategy"].update({k:v for k,v in args.items() if v})
            miss=[k for k,v in memory["strategy"].items() if v is None]
            msgs.append({"role":"function","name":function_name,
                        "content":"params ok" if not miss else f"still need {miss}"})

        # =====Data Module=====    
        elif function_name == "get_res_price_data":
            res = get_res_price_data(**args)
            msgs.append({"role": "function", "name": function_name, "content": res.to_json()})

        elif function_name == "get_cleaned_price_data":
            res = get_res_price_data(**args)
            cleaned_data = clean_df(res)
            msgs.append({"role": "function", "name": function_name, "content": cleaned_data.to_json()})

        elif function_name == "get_fundamental_data":
            res = get_fundamental_data(**args)
            msgs.append({"role": "function", "name": function_name, "content": res.to_json()})

        # elif function_name == "get_macro_data":
        #     res = get_macro_data(**args)
        #     msgs.append({"role": "function", "name": function_name, "content": res.to_json()})

        # =====Plot Module=====
        elif function_name == "plot_line_chart":
            res = plot_res_line_chart(**args)
            msgs.append({"role": "function", "name": function_name, "content": json.dumps(res)})

        # elif function_name == "plot_correlation_chart":
        #     res = plot_correlation_chart(**args)
        #     msgs.append({"role": "function", "name": function_name, "content": json.dumps(res)})

        # elif function_name=="run_backtest":
        #     res=run_backtest(memory["strategy"])
        #     if "error" in res:
        #         msgs.append({"role":"function","name":function_name,"content":res["error"]})
        #     else:
        #         # ① 把摘要给 GPT 生成自然语言
        #         msgs.append({"role":"function","name":function_name,"content":res["summary"]})
        #         print(f"图表已保存为 {res['image']}")   # ② 本地提示图路径

        assistant=gpt(msgs); msgs.append(assistant)

    print("===AI AGENT===: ", assistant.content,"\n")

