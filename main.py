# main.py
# 示例应用：公式计算器
# 使用 tins_gui 库来计算勾股定理 (a^2 + b^2 = c^2)。

from tins_gui import *

# 尝试导入数学模块，处理PC和计算器环境的差异
try:
    from math import sqrt, pow
except ImportError:
    # 如果在PC上测试，Python标准库的math模块已经可用
    from math import sqrt, pow

# --- 全局变量和回调函数 ---

# 创建主应用实例
# 需要在全局范围内定义，以便回调函数可以访问它
app = App()

# 定义控件变量，以便在回调函数中引用它们
input_a = None
input_b = None

def calculate_pythagoras():
    """
    当 "Calculate c" 按钮被按下时调用的回调函数。
    它会读取输入框的值，执行计算，并用一个消息框显示结果。
    """
    global input_a, input_b, app

    try:
        # 从输入框获取文本
        a_str = input_a.text
        b_str = input_b.text

        # 转换为浮点数
        a = float(a_str)
        b = float(b_str)

        # 计算 c 的值
        c = sqrt(pow(a, 2) + pow(b, 2))

        # 准备结果消息
        result_message = "Result: c = " + str(round(c, 4))

    except (ValueError, TypeError):
        # 处理无效输入，例如空字符串或非数字字符
        result_message = "Error: Invalid input."

    # 创建并以模态方式显示结果消息框
    msg_box = MessageBox("Calculation Result", result_message, width=220, height=100)
    msg_box.run_modal(app)

# --- UI 布局 ---

# 1. 创建所有控件实例
title_label = Label(10, 5, "Pythagorean Theorem (a^2+b^2=c^2)")
label_a = Label(10, 40, "Value for a:")
input_a = TextInput(110, 38, 120, "3") # 初始值为 "3"

label_b = Label(10, 70, "Value for b:")
input_b = TextInput(110, 68, 120, "4") # 初始值为 "4"

calc_button = Button(110, 110, 120, 25, "Calculate c", on_click=calculate_pythagoras)
info_label = Label(10, 200, "Use 'tab' to switch controls. 'esc' to exit.")

# 2. 将控件添加到应用中
app.add_widget(title_label)
app.add_widget(label_a)
app.add_widget(input_a, is_focusable=True) # 文本框可聚焦
app.add_widget(label_b)
app.add_widget(input_b, is_focusable=True) # 文本框可聚焦
app.add_widget(calc_button, is_focusable=True) # 按钮可聚焦
app.add_widget(info_label)


# --- 运行应用 ---
# 当这个脚本作为主程序在TI-Nspire上运行时，
# 这个 `if` 块内的代码将会执行。
if __name__ == "__main__":
    app.run()