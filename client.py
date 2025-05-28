import subprocess

def start_agent():
    proc = subprocess.Popen(
        ["/opt/anaconda3/envs/mcp_env/bin/python", "mcp_servers/market_data/server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )
    return proc

def send_request(proc, prompt):
    if proc.stdin:
        proc.stdin.write(prompt + "\n")
        proc.stdin.flush()

    if proc.stdout:
        response_lines = []
        while True:
            line = proc.stdout.readline()
            if not line.strip():  # 空行代表 response 结束
                break
            response_lines.append(line.strip())
        return "\n".join(response_lines)

if __name__ == "__main__":
    print("🤖 MCP Agent Local Shell (type 'exit' to quit)")
    proc = start_agent()
    while True:
        user_input = input("> ")
        if user_input.lower() in ("exit", "quit"):
            proc.terminate()
            break
        result = send_request(proc, user_input)
        print(result or "[No response]")
