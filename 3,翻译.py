import json
import time
import traceback
from llama_cpp import Llama
jsonpath="ManualTransFile.json"
# --- 加载模型 ---
print("[启动] 正在加载模型...")
llm = Llama(
    model_path="gemma-4-26B-A4B-it-UD-Q3_K_XL.gguf",# 16G显存推荐,下载地址: https://huggingface.co/unsloth/gemma-4-26B-A4B-it-GGUF/resolve/main/gemma-4-26B-A4B-it-UD-Q3_K_XL.gguf
    n_ctx=4096,
    n_threads=8,
    n_gpu_layers=-1,
    verbose=False
)
print("[完成] 模型加载成功")

# --- 配置 ---
BATCH_SIZE = 10 # 每次翻译10句
CONTEXT_SENTENCES = 35 # 最多参考35句

# --- 读取 JSON ---
print("[读取] 正在加载 JSON...")
try:
    with open(jsonpath, 'r', encoding='utf-8') as f:
        data_dict = json.load(f)
    print(f"[完成] JSON 条目数: {len(data_dict)}")
except Exception as e:
    print(f"[错误] JSON读取失败: {e}")
    exit()

all_keys = list(data_dict.keys())

# --- 自动断点 ---
print("\n[断点] 开始扫描已翻译内容...")
start_pos = len(all_keys)

for i in range(len(all_keys) - 1, -1, -1):
    k = all_keys[i]
    v = data_dict.get(k, "")
    if v and v.strip() and v.strip() != k.strip() and len(v.strip()) >= 5:
        start_pos = i + 1
        print(f"[断点] 找到已翻译 key: {k}")
        print(f"[断点] start_pos = {start_pos}")
        break
else:
    start_pos = 0
    print("[断点] 未找到，从头开始")

# --- 待翻译 ---
todo_list = []
for i in range(start_pos, len(all_keys)):
    k = all_keys[i]
    v = data_dict.get(k, "")
    if not v or v.strip() == "" or v.strip() == k.strip() or len(v.strip()) < 5:
        todo_list.append((i, k))

total = len(todo_list)
print(f"[任务] 待翻译数量: {total}")

if total == 0:
    print("[完成] 无任务")
    exit(0)

# --- system prompt ---
system_prompt = """你是专业的日语→中文翻译专家，专门负责翻译日语色情游戏脚本。

你的翻译要求：
- 极致自然、色情且富有画面感与沉浸感
- 保留原作的色气、喘息、诱惑与挑逗语气
- 拟声词要做中文化处理，让玩家更易代入
- 性描写大胆直接，同时保持文学质感和情欲张力
- 严格保持角色性格与说话习惯
- 请严格参考【前文参考】中的翻译风格、用词和色气程度，保持高度一致
- 注意剧情连贯性和角色情绪变化

【非常重要的格式约束】
- 输入有 N 行原文，你必须输出 N 行译文
- 每一行译文必须严格对应一行原文（顺序一致，不得合并或拆分）
- 不得增加、删除或跳过任何一行
- 不得输出标题、解释、编号或任何多余字符
- 不得将多行合并为一行，也不得一行拆成多行
- 输出必须是纯译文文本，每行对应一行原文

只输出翻译结果，不要解释，不要添加任何多余文字。
"""

# --- 上下文 ---
def get_recent_context(pos, context_sentences=35):
    start = max(0, pos - context_sentences)
    context_lines = []

    for i in range(start, pos):
        k = all_keys[i]
        trans = data_dict.get(k, "")
        if trans and trans.strip() and trans.strip() != k.strip():
            context_lines.append(f"原文: {k}\n翻译: {trans}")

    print(f"[上下文] 使用 {len(context_lines)} 条历史参考")

    if context_lines:
        return "【前文参考】\n" + "\n\n".join(context_lines) + "\n\n【当前】\n"
    return "【当前】\n"


# --- 主循环 ---
idx = 0

while idx < total:

    print("\n" + "="*50)
    print(f"[批次开始] idx={idx}")

    current_pos, current_key = todo_list[idx]
    current_batch = []

    for j in range(BATCH_SIZE):
        if idx + j >= total:
            break
        _, k = todo_list[idx + j]
        current_batch.append(k)

    print(f"[批次] 当前 size = {len(current_batch)}")
    print(f"[批次] 第一条 key = {current_batch[0]}")

    context_prefix = get_recent_context(current_pos, CONTEXT_SENTENCES)
    prompt = context_prefix + "\n".join(current_batch)

    print("[Prompt] 构造完成，长度 =", len(prompt))

    try:
        print("[模型] 开始推理...")

        result = llm.create_chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            top_p=0.9
        )

        ai_reply = result["choices"][0]["message"]["content"].strip()

        print("\n[模型输出]")
        print(ai_reply)
        print("\n[模型输出结束]\n")

        translated_lines = [x.strip() for x in ai_reply.split("\n") if x.strip()]

        print(f"[解析] 输出行数: {len(translated_lines)}")

        if len(translated_lines) == len(current_batch):

            for k, v in zip(current_batch, translated_lines):
                data_dict[k] = v

            with open(jsonpath, 'w', encoding='utf-8') as f:
                json.dump(data_dict, f, ensure_ascii=False, indent=4)

            print(f"[成功] 写入 {len(current_batch)} 条")

            idx += BATCH_SIZE

        else:
            print(f"[错误] 行数不匹配 {len(translated_lines)} != {len(current_batch)}")

            # --- 失败：追加到 JSON 末尾 ---
            print("[处理] 当前批次将移动到队列末尾")

            for k in current_batch:
                # 如果不存在就追加空占位（防止丢失）
                if k not in data_dict:
                    data_dict[k] = ""

                # 删除旧位置（避免重复）
                # 注意：dict 不保证顺序，这里只做逻辑标记
                data_dict[k] = ""

            # 重新追加到末尾（通过重新构造顺序实现）
            remaining = []
            for key in all_keys:
                if key in current_batch:
                    continue
                remaining.append(key)

            all_keys[:] = remaining + current_batch

            # 保存 JSON
            with open(jsonpath, 'w', encoding='utf-8') as f:
                json.dump(data_dict, f, ensure_ascii=False, indent=4)

            print("[完成] 已移动到末尾，继续下一批")
            time.sleep(2)

    except Exception as e:
        print(f"[异常] {e}")
        traceback.print_exc()
        time.sleep(5)

print("\n[完成]")