import traceback

def fatal_analyzer(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_message = f"函数 {func.__name__} 发生了致命错误: \n"
            error_message += f"错误类型: {type(e).__name__} \n"
            error_message += f"错误信息: {str(e)} \n"
            error_message += "异常追踪信息: \n"
            error_message += traceback.format_exc()
            error_message += "异常追踪结束. \n"
            error_message += "===========================================\n"
            
            with open("fatal.log", "a",encoding="utf-8") as file:
                file.write(error_message)
            raise  # 抛出异常，保持异常的原始行为
    return wrapper
