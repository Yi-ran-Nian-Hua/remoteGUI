from nicegui import ui

# 标题栏
with ui.header().classes("bg-blue-500 text-white"):
    ui.label("远程接口调用").classes("text-xl font-bold")

# 搜索栏及按钮区
with ui.row().classes("items-center p-2"):
    # 搜索输入框和按钮
    with ui.row().classes("flex-grow items-center"):
        search_input = ui.input(placeholder="输入搜索关键词")
        ui.icon("search").classes("ml-2 cursor-pointer").on("click", lambda: print(f"搜索内容: {search_input.value}"))
    # 多个功能按钮
    for _ in range(6):
        ui.button("按钮").classes("ml-2")
    # 右侧的 + 按钮和保存按钮
    ui.icon("add").classes("ml-auto mr-2 cursor-pointer").on("click", lambda: print("点击 + 按钮"))
    ui.button("保存").classes("bg-gray-500 text-white")

# 左侧边栏（历史记录、接口列表）
with ui.column().classes("w-64 bg-gray-100 p-2"):
    ui.label("历史记录").classes("font-bold mb-2")
    ui.label("历史记录1")
    ui.label("历史记录2")

    ui.separator().classes("my-2")

    ui.label("接口列表").classes("font-bold mb-2")
    ui.label("接口1")
    ui.label("接口2")

# 主内容区，分为参数列表和调用结果
with ui.column().classes("flex-grow p-2"):
    # 参数列表部分
    with ui.row():
        ui.label("参数列表").classes("font-bold text-lg mb-2")
    with ui.row().classes("flex-wrap"):
        for _ in range(4):
            with ui.card().classes("w-64 mr-4 mb-4"):
                ui.image("https://via.placeholder.com/150").classes("mb-2")
                ui.label("滚动面板内容")

    ui.separator().classes("my-4")

    # 调用结果部分
    with ui.row():
        ui.label("调用结果").classes("font-bold text-lg mb-2")
    with ui.row().classes("flex-wrap"):
        for _ in range(2):
            with ui.card().classes("w-64 mr-4 mb-4"):
                ui.image("https://via.placeholder.com/150").classes("mb-2")
                ui.label("结果内容")
    # 结果复制和剪切按钮
    with ui.row().classes("justify-end"):
        ui.button("结果复制").classes("mr-2")
        ui.button("结果剪切").classes("bg-gray-500 text-white")

# 使用推荐的多进程保护条件
if __name__ in {"__main__", "__mp_main__"}:
    ui.run()