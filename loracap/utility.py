import re
LORA_MODE = ["TEST", "LWOTAA", "LWABP"]

def hex_value(line):
    """
    extract hex value
    """
    pattern = r'\+\w+:\s*\w+,\s*([0-9A-Fa-f]{2}(?::[0-9A-Fa-f]{2}){2,7})'
    match = re.search(pattern, line)
    if match:
        return match.group(1)  # 返回匹配的十六进制字符串
    else:
        return None

def validate_and_format_hex(value, expected_length):
    """
    验证和格式化十六进制字符串。
    :param value: 原始字符串值。
    :param expected_length: 期望的十六进制字符长度。
    :return: 格式化后的十六进制字符串。
    """
    # 移除非十六进制字符
    cleaned_value = ''.join(filter(str.isalnum, value)).upper()
    # 验证长度
    if len(cleaned_value) != expected_length:
        raise ValueError(f"Expected hex string of length {expected_length}, got {len(cleaned_value)}")
    return cleaned_value
