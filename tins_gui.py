# tins_gui.py
# TI-Nspire CX II Python GUI 库
# 作者: Jules
# 版本: 0.1.0

try:
    from ti_draw import *
    from ti_system import *
except ImportError:
    # 如果不在计算器环境中，则创建模拟函数以便在PC上测试
    print("警告: 未在TI-Nspire环境中运行，将使用模拟模块。")
    # 创建一个模拟的 ti_draw 模块
    class MockTiDraw:
        def __getattr__(self, name):
            def mock_func(*args, **kwargs):
                print("调用模拟函数: ti_draw.{} a:{} kw:{}".format(name, args, kwargs))
            return mock_func

    # 创建一个模拟的 ti_system 模块
    class MockTiSystem:
        def __getattr__(self, name):
            def mock_func(*args, **kwargs):
                print("调用模拟函数: ti_system.{} a:{} kw:{}".format(name, args, kwargs))
                if name == 'get_key':
                    return "" # 模拟无按键输入
            return mock_func

    ti_draw = MockTiDraw()
    ti_system = MockTiSystem()


class Widget:
    """
    所有UI组件（控件）的基类。
    定义了所有控件共有的基本属性和方法。
    """
    def __init__(self, x, y, width, height):
        """
        初始化一个控件。

        :param x: 控件左上角的 x 坐标。
        :param y: 控件左上角的 y 坐标。
        :param width: 控件的宽度。
        :param height: 控件的高度。
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.is_focused = False

    def set_focus(self, focused):
        """
        设置控件的焦点状态。

        :param focused: 布尔值，True表示获得焦点，False表示失去焦点。
        """
        self.is_focused = focused

    def handle_key(self, key):
        """
        处理键盘输入。
        子类应该重写此方法以实现特定的交互逻辑。

        :param key: 按键的字符串表示。
        """
        pass

    def draw(self):
        """
        在屏幕上绘制控件。
        子类必须重写此方法以实现其视觉表现。
        """
        raise NotImplementedError("子类必须实现 draw() 方法。")


class App:
    """
    主应用程序类。
    管理所有控件、事件循环和屏幕刷新。
    """
    def __init__(self):
        """
        初始化应用程序。
        """
        self.widgets = []
        self.focused_widget_index = -1

    def add_widget(self, widget, is_focusable=False):
        """
        向应用程序中添加一个控件。

        :param widget: 要添加的控件实例。
        :param is_focusable: 该控件是否可以接收焦点。
        """
        widget.is_focusable = is_focusable
        self.widgets.append(widget)
        # 如果这是第一个可聚焦的控件，则自动给予焦点
        if is_focusable and self.focused_widget_index == -1:
            self.focused_widget_index = len(self.widgets) - 1
            self.widgets[self.focused_widget_index].set_focus(True)

    def _get_focusable_widgets_indices(self):
        """获取所有可聚焦控件的索引列表。"""
        return [i for i, w in enumerate(self.widgets) if w.is_focusable]

    def _switch_focus(self):
        """
        将焦点切换到下一个可聚焦的控件。
        """
        focusable_indices = self._get_focusable_widgets_indices()
        if not focusable_indices:
            return # 没有可聚焦的控件

        # 移除当前控件的焦点
        if self.focused_widget_index != -1:
            self.widgets[self.focused_widget_index].set_focus(False)

        # 找到当前焦点在 focusable_indices 中的位置
        try:
            current_pos = focusable_indices.index(self.focused_widget_index)
            next_pos = (current_pos + 1) % len(focusable_indices)
        except ValueError:
            # 如果当前焦点控件不可见或不存在，则聚焦到第一个
            next_pos = 0

        # 设置新焦点
        self.focused_widget_index = focusable_indices[next_pos]
        self.widgets[self.focused_widget_index].set_focus(True)


    def run(self):
        """
        启动并运行应用程序的主事件循环。
        """
        clear()
        use_buffer()

        while True:
            # 1. 绘制所有控件
            for widget in self.widgets:
                widget.draw()

            # 2. 刷新屏幕
            paint_buffer()

            # 3. 等待并获取按键
            key = get_key(1) # 阻塞模式，等待按键

            # 4. 处理系统级按键
            if key == "esc":
                break # 退出循环

            if key == "tab":
                self._switch_focus()
                continue

            # 5. 将按键事件分发给当前聚焦的控件
            if self.focused_widget_index != -1:
                focused_widget = self.widgets[self.focused_widget_index]
                focused_widget.handle_key(key)

        clear() # 退出时清屏


class Label(Widget):
    """
    标签控件。
    用于在屏幕上显示静态文本。
    """
    def __init__(self, x, y, text):
        """
        初始化一个标签。

        :param x: 标签左上角的 x 坐标。
        :param y: 标签左上角的 y 坐标。
        :param text: 要显示的文本字符串。
        """
        # 假设每个字符大约 6x8 像素
        width = len(text) * 6
        height = 8
        super().__init__(x, y, width, height)
        self.text = text

    def draw(self):
        """
        在屏幕上绘制标签文本。
        """
        # 注意: ti_draw的坐标系原点在左上角
        draw_text(self.x, self.y, self.text)


class Button(Widget):
    """
    按钮控件。
    用户可以聚焦并“按下”以触发一个动作。
    """
    def __init__(self, x, y, width, height, text, on_click=None):
        """
        初始化一个按钮。

        :param x: 按钮左上角的 x 坐标。
        :param y: 按钮左上角的 y 坐标。
        :param width: 按钮的宽度。
        :param height: 按钮的高度。
        :param text: 按钮上显示的文本。
        :param on_click: 当按钮被按下时调用的回调函数。
        """
        super().__init__(x, y, width, height)
        self.text = text
        self.on_click = on_click

    def draw(self):
        """
        在屏幕上绘制按钮。
        """
        # 绘制边框
        if self.is_focused:
            set_pen("medium", "solid") # 焦点状态下，边框加粗
        else:
            set_pen("thin", "solid")

        draw_rect(self.x, self.y, self.width, self.height)

        # 绘制文本（居中）
        # 假设英文字符宽度约为6像素，高度为8像素
        text_x = self.x + (self.width - len(self.text) * 6) // 2
        text_y = self.y + (self.height - 8) // 2
        draw_text(text_x, text_y, self.text)

        # 恢复默认画笔
        set_pen("thin", "solid")

    def handle_key(self, key):
        """
        处理按键事件。如果按下回车键，则执行回调。
        """
        # TI-Nspire的回车键可能是 'enter' 或 '·'
        if key == "enter" or key == "·":
            if self.on_click:
                self.on_click()


class TextInput(Widget):
    """
    文本输入框控件。
    允许用户输入和编辑单行文本。
    """
    def __init__(self, x, y, width, initial_text=""):
        """
        初始化一个文本输入框。

        :param x: 输入框左上角的 x 坐标。
        :param y: 输入框左上角的 y 坐标。
        :param width: 输入框的宽度。
        :param initial_text: 初始文本。
        """
        height = 12 # 固定高度
        super().__init__(x, y, width, height)
        self.text = initial_text

    def draw(self):
        """
        绘制文本输入框。
        """
        # 绘制边框和背景
        set_pen("thin", "solid")
        set_color(255, 255, 255)
        fill_rect(self.x, self.y, self.width, self.height)
        set_color(0,0,0)
        draw_rect(self.x, self.y, self.width, self.height)

        # 绘制文本
        draw_text(self.x + 2, self.y + 2, self.text)

        # 如果获得焦点，绘制一个简单的静态光标
        if self.is_focused:
            cursor_x = self.x + 2 + len(self.text) * 6
            # 确保光标在输入框内
            if cursor_x < self.x + self.width - 6:
                draw_text(cursor_x, self.y + 2, "_")

    def handle_key(self, key):
        """
        处理按键输入以编辑文本。
        """
        # 允许字母、数字、基本符号输入
        if len(key) == 1 and ('a' <= key <= 'z' or 'A' <= key <= 'Z' or '0' <= key <= '9' or key in ' .+-*/()='):
            # 限制输入框的总字符数，防止视觉上超出边界
            if (len(self.text) + 1) * 6 < self.width - 4:
                 self.text += key
        elif key == "del": # TI-Nspire的删除键是 'del'
            if len(self.text) > 0:
                self.text = self.text[:-1]


class Listbox(Widget):
    """
    列表框控件。
    显示一个可滚动的项目列表，并允许用户选择其中一项。
    """
    def __init__(self, x, y, width, height, items, on_select=None):
        """
        初始化一个列表框。

        :param x: 列表框左上角的 x 坐标。
        :param y: 列表框左上角的 y 坐标。
        :param width: 列表框的宽度。
        :param height: 列表框的高度。
        :param items: 一个包含字符串的列表，作为列表框的项目。
        :param on_select: 当用户选择一个项目时调用的回调函数。
        """
        super().__init__(x, y, width, height)
        self.items = items if items else ["(空)"]
        self.on_select = on_select
        self.selected_index = 0
        self.top_item_index = 0
        self.item_height = 10 # 每个项目占用的像素高度
        self.visible_items_count = self.height // self.item_height

    def draw(self):
        """
        绘制列表框及其内容。
        """
        # 绘制边框
        if self.is_focused:
            set_pen("medium", "solid")
        else:
            set_pen("thin", "solid")
        draw_rect(self.x, self.y, self.width, self.height)
        set_pen("thin", "solid") # 恢复

        # 绘制可见的项目
        for i in range(self.visible_items_count):
            item_index = self.top_item_index + i
            if item_index >= len(self.items):
                break

            item_text = self.items[item_index]
            draw_y = self.y + i * self.item_height + 1

            # 如果是选中项，则高亮显示
            if item_index == self.selected_index:
                # 保存当前颜色设置
                # (注意: ti_draw没有直接获取颜色的API，所以我们直接设置)
                set_color(0, 0, 0) # 黑色背景
                fill_rect(self.x + 1, draw_y, self.width - 2, self.item_height)
                set_color(255, 255, 255) # 白色文字
                draw_text(self.x + 2, draw_y, item_text)
                set_color(0, 0, 0) # 恢复默认黑色文字
            else:
                draw_text(self.x + 2, draw_y, item_text)

    def handle_key(self, key):
        """
        处理上下方向键以导航列表，回车键以选择。
        """
        if not self.items:
            return

        if key == "up":
            if self.selected_index > 0:
                self.selected_index -= 1
                # 如果选中项在可视区域之上，则向上滚动
                if self.selected_index < self.top_item_index:
                    self.top_item_index = self.selected_index
        elif key == "down":
            if self.selected_index < len(self.items) - 1:
                self.selected_index += 1
                # 如果选中项在可视区域之下，则向下滚动
                if self.selected_index >= self.top_item_index + self.visible_items_count:
                    self.top_item_index = self.selected_index - self.visible_items_count + 1
        elif (key == "enter" or key == "·") and self.on_select:
            self.on_select(self.selected_index, self.items[self.selected_index])


class Window(Widget):
    """
    窗口控件。
    一个可以包含其他控件的容器，通常带有一个标题和边框。
    """
    def __init__(self, x, y, width, height, title=""):
        """
        初始化一个窗口。

        :param x: 窗口左上角的 x 坐标。
        :param y: 窗口左上角的 y 坐标。
        :param width: 窗口的宽度。
        :param height: 窗口的高度。
        :param title: 窗口的标题。
        """
        super().__init__(x, y, width, height)
        self.title = title
        self.children = [] # 存储子控件

    def add_child(self, widget):
        """
        向窗口中添加一个子控件。
        注意: 子控件的坐标是相对于窗口的。
        """
        self.children.append(widget)

    def draw(self):
        """
        绘制窗口边框、标题以及所有子控件。
        """
        # 绘制背景和边框
        set_color(200, 200, 200) # 浅灰色背景
        fill_rect(self.x, self.y, self.width, self.height)
        set_color(0, 0, 0)
        draw_rect(self.x, self.y, self.width, self.height)

        # 绘制标题栏
        if self.title:
            set_color(100, 100, 100) # 深灰色标题栏
            fill_rect(self.x + 1, self.y + 1, self.width - 2, 12)
            set_color(255, 255, 255) # 白色标题文字
            draw_text(self.x + 4, self.y + 2, self.title)
            set_color(0, 0, 0)

        # 绘制子控件
        for child in self.children:
            # 暂时不支持焦点和事件传递给子控件，仅绘制
            # 绘制子控件时，需要将它们的相对坐标转换为绝对屏幕坐标
            original_x, original_y = child.x, child.y
            child.x += self.x
            child.y += self.y
            child.draw()
            # 恢复其原始坐标
            child.x, child.y = original_x, original_y

    # 注意: 这个基础的Window类不处理子控件的事件。
    # 一个更完整的实现需要一个布局管理器和事件分发系统。


class MessageBox(Window):
    """
    一个简单的消息弹窗。
    通常用于显示一条消息和一个“确定”按钮。
    """
    def __init__(self, title, message, width=200, height=100):
        """
        初始化一个消息框。

        :param title: 弹窗的标题。
        :param message: 要显示的消息文本。
        :param width: 弹窗宽度。
        :param height: 弹窗高度。
        """
        # 居中显示
        screen_w, screen_h = 320, 240 # 假定屏幕尺寸
        x = (screen_w - width) // 2
        y = (screen_h - height) // 2

        super().__init__(x, y, width, height, title)

        self.message_label = Label(10, 20, message)
        self.ok_button = Button(width // 2 - 30, height - 30, 60, 20, "OK")

        self.add_child(self.message_label)
        self.add_child(self.ok_button)

    def run_modal(self, app):
        """
        以模态方式运行消息框，会阻塞主应用的事件循环。
        """
        # 这是一个简化的模态实现
        # 它会接管事件循环直到自己关闭

        # 将按钮的回调设置为关闭自己
        self.ok_button.on_click = lambda: setattr(self, 'is_running', False)
        self.is_running = True

        while self.is_running:
            clear()
            use_buffer()

            # 绘制父应用的所有内容作为背景
            for widget in app.widgets:
                widget.draw()

            # 在顶层绘制自己
            self.draw()

            paint_buffer()

            key = get_key(1)

            if key == "esc" or key == "enter" or key == "·":
                self.is_running = False