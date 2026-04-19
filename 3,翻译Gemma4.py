import json
import requests
import os
import time
import traceback

# --- 配置区 ---
url = "http://127.0.0.1:8080/v1/chat/completions"
BATCH_SIZE = 10
CONTEXT_SENTENCES = 35

# --- 加载 JSON ---
try:
    with open("ManualTransFile.json", 'r', encoding='utf-8') as f:
        data_dict = json.load(f)
    print(f"[加载] JSON 条目数: {len(data_dict)}")
except Exception as e:
    print(f"[错误] 读取 JSON 失败: {e}")
    exit()

all_keys = list(data_dict.keys())

# ====================== 新增：自动从底部向上查找断点 ======================
print("\n" + "="*70)
print("自动从 JSON 底部向上查找上次翻译位置...")
print("="*70)

start_pos = len(all_keys)  # 默认从最后一条开始

for i in range(len(all_keys) - 1, -1, -1):   # 从最后一条开始往前遍历
    k = all_keys[i]
    v = data_dict.get(k, "")
    # 如果这一条已经翻译了（有内容、不是空的、不是和原文一样、长度够）
    if v and v.strip() and v.strip() != k.strip() and len(v.strip()) >= 5:
        start_pos = i + 1          # 从已翻译的下一条开始
        print(f"[自动断点] 找到最后一条已翻译内容 → key: {k}")
        print(f"[自动断点] 将从下一条开始翻译，位置: {start_pos} / {len(all_keys)}")
        break
else:
    # 如果一条已翻译的都没找到，就从头开始
    start_pos = 0
    print("[自动断点] 未找到任何已翻译内容，将从头开始翻译")

# --- 收集从 start_pos 开始的所有未翻译内容 ---
todo_list = []
for i in range(start_pos, len(all_keys)):
    k = all_keys[i]
    v = data_dict.get(k, "")
    if not v or v.strip() == "" or v.strip() == k.strip() or len(v.strip()) < 5:
        todo_list.append((i, k))

total = len(todo_list)
print(f"[任务] 待翻译条目: {total} 行\n")

if total == 0:
    print("[完成] 所有内容已翻译完毕！")
    exit(0)

# --- System Prompt（保持不变）---
system_prompt = {
    "role": "system",
    "content": """你是专业的日语→中文翻译专家，专门负责翻译日语色情游戏脚本。
你的翻译要求：
- 极致自然、色情且富有画面感与沉浸感
- 保留原作的色气、喘息、诱惑与挑逗语气
- 拟声词要做中文化处理，让玩家更易代入
- 性描写大胆直接，同时保持文学质感和情欲张力
- 严格保持角色性格与说话习惯
- 请严格参考【前文参考】中的翻译风格、用词和色气程度，保持高度一致
- 注意剧情连贯性和角色情绪变化
只输出翻译结果，不要解释，不要添加任何多余文字。"""
}

# --- 获取前文函数（保持不变）---
def get_recent_context(pos, context_sentences=65):
    start = max(0, pos - context_sentences)
    context_lines = []
    for i in range(start, pos):
        k = all_keys[i]
        trans = data_dict.get(k, "")
        if trans and trans.strip() and trans.strip() != k.strip() and len(trans.strip()) >= 5:
            context_lines.append(f"原文: {k}\n翻译: {trans}")
    context_count = len(context_lines)
    print(f"[上下文] 当前位置: {pos} | 使用前 {context_count} 句已翻译内容作为参考")
    if context_lines:
        return "【前文参考（请严格保持相同风格、语气和色气程度）】\n" + "\n\n".join(context_lines) + "\n\n【当前待翻译内容】\n"
    return "【当前待翻译内容】\n"

# --- 主循环（保持不变）---
idx = 0
while idx < total:
    current_pos, current_key = todo_list[idx]
    current_batch = []
   
    for j in range(BATCH_SIZE):
        if idx + j >= total:
            break
        p, k = todo_list[idx + j]
        current_batch.append(k)

    context_prefix = get_recent_context(current_pos, CONTEXT_SENTENCES)
    prompt = context_prefix + "\n".join(current_batch)

    print(f"\n[批次] idx={idx} | 位置={current_pos} | size={len(current_batch)} | 第一个key: {current_key}")

    messages = [system_prompt, {"role": "user", "content": prompt}]

    try:
        response = requests.post(
            url,
            json={
                "model": "gemma-4-E4B-it-UD-Q8_K_XL.gguf",
                "messages": messages,
                "temperature": 0.3
            },
            timeout=300
        )
        response.raise_for_status()
        ai_reply = response.json()["choices"][0]["message"]["content"].strip()

        translated_lines = [line.strip() for line in ai_reply.split('\n') if line.strip()]

        if len(translated_lines) == len(current_batch):
            for k, res in zip(current_batch, translated_lines):
                data_dict[k] = res

            # 保存
            with open("ManualTransFile.json", 'w', encoding='utf-8') as f:
                json.dump(data_dict, f, ensure_ascii=False, indent=4)

            print(f"[成功] 已更新 {len(current_batch)} 条")
            idx += BATCH_SIZE
            print(f"[总进度] {start_pos + idx} / {len(data_dict)}")
        else:
            print(f"[错误] 行数不匹配 (期望{len(current_batch)}, 实际{len(translated_lines)})")
            time.sleep(5)

    except Exception as e:
        print(f"[异常] 请求失败: {e}")
        traceback.print_exc()
        time.sleep(8)

print("\n[完成] 所有翻译已完成！")