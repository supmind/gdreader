# TI-Nspire CX II Python GUI 库

这是一个为 TI-Nspire CX II 系列图形计算器设计的简单图形用户界面（GUI）库。它使用 Python 语言编写，并基于计算器内置的 `ti_draw` 和 `ti_system` 模块。

## 功能

本 GUI 库旨在提供一个面向对象的框架，用于轻松创建交互式应用程序。目前支持以下控件：

*   **Label**: 用于显示静态文本。
*   **Button**: 可点击的按钮，支持回调函数。
*   **TextInput**: 单行文本输入框。
*   **Listbox**: 可滚动的项目列表。
*   **Window**: 可包含其他控件的容器窗口。
*   **MessageBox**: 用于显示信息、警告或错误的模态弹窗。

## 文件结构

*   `tins_gui.py`: GUI 库的核心文件，包含了所有控件和应用程序的类。您可以在自己的项目中导入此文件来使用这些控件。
*   `main.py`: 一个完整的示例应用程序（公式计算器），展示了如何使用 `tins_gui.py` 中的各种控件来构建一个实际的应用。

## 如何使用

1.  将 `tins_gui.py` 文件与您的主程序文件（例如 `my_app.py`）放在同一个文件夹中。
2.  在您的主程序中，从 `tins_gui` 导入所需的类。
3.  实例化 `App` 类，然后创建并添加您需要的控件。
4.  调用 `app.run()` 来启动事件循环。

## 示例代码

以下是一个简单的示例，演示了如何创建一个带有标签、输入框和按钮的应用程序。完整代码请参见 `main.py`。

```python
# main.py
# 示例应用：公式计算器
# 使用 tins_gui 库来计算勾股定理 (a^2 + b^2 = c^2)。

from tins_gui import *

# 尝试导入数学模块
try:
    from math import sqrt, pow
except ImportError:
    from math import sqrt, pow

# --- 全局变量和回调函数 ---
app = App()
input_a = None
input_b = None

def calculate_pythagoras():
    """
    当 "Calculate c" 按钮被按下时调用的回调函数。
    """
    global input_a, input_b, app
    try:
        a = float(input_a.text)
        b = float(input_b.text)
        c = sqrt(pow(a, 2) + pow(b, 2))
        result_message = "Result: c = " + str(round(c, 4))
    except (ValueError, TypeError):
        result_message = "Error: Invalid input."

    # 创建并显示结果消息框
    msg_box = MessageBox("Calculation Result", result_message)
    msg_box.run_modal(app)

# --- UI 布局 ---
title_label = Label(10, 5, "Pythagorean Theorem (a^2+b^2=c^2)")
label_a = Label(10, 40, "Value for a:")
input_a = TextInput(110, 38, 120, "3")

label_b = Label(10, 70, "Value for b:")
input_b = TextInput(110, 68, 120, "4")

calc_button = Button(110, 110, 120, 25, "Calculate c", on_click=calculate_pythagoras)

# --- 将控件添加到应用中 ---
app.add_widget(title_label)
app.add_widget(label_a)
app.add_widget(input_a, is_focusable=True)
app.add_widget(label_b)
app.add_widget(input_b, is_focusable=True)
app.add_widget(calc_button, is_focusable=True)

# --- 运行应用 ---
if __name__ == "__main__":
    app.run()
```

## 贡献

欢迎通过提交 issue 或 pull request 来改进这个库。