import json
import re

jp_pattern = re.compile(r'[\u3040-\u30FF\u4E00-\u9FFF]')

remove_keys = {
    "子丑寅卯辰巳午未申酉戌亥",
    "甲乙丙丁戊己庚辛壬癸",
    "零一二三四五六七八九",
    "十百千萬",
    "負",
    "零壹貳參肆伍陸柒捌玖",
    "拾佰仟萬",
    "负",
    "零壹贰叁肆伍陆柒捌玖",
    "十百千万",
    "マイナス",
    "零壱弐参四伍六七八九",
    "拾百千万",
    "零壹貳參四五六七八九",
    "拾百千",
    "〇一二三四五六七八九",
    "日本語",
    "あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわゐゑをん",
    "いろはにほへとちりぬるをわかよたれそつねならむうゐのおくやまけふこえてあさきゆめみしゑひもせす",
    "アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヰヱヲン",
    "イロハニホヘトチリヌルヲワカヨタレソツネナラムウヰノオクヤマケフコエテアサキユメミシヱヒモセス"
}

with open('ManualTransFile.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

filtered_items = [
    (k, v) for k, v in data.items()
    if jp_pattern.search(k) and k not in remove_keys
]

sorted_data = dict(filtered_items)

with open('ManualTransFile.json', 'w', encoding='utf-8') as f:
    json.dump(sorted_data, f, ensure_ascii=False, indent=4)