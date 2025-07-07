from nicegui import ui
import json
from functools import partial

# 禁用页面滚动
ui.add_body_html('<style>body { overflow: hidden; }</style>')

# 标题栏
with ui.header().classes("bg-blue-500 text-white"):
    ui.label("远程接口调用").classes("text-xl font-bold")


# 下方功能区
with ui.row().classes('w-full h-screen'):
    # 左侧功能选择按钮
    with ui.column():
        ui.button('接口列表')
        ui.button('历史记录')
    ui.separator().classes('w-[1px] h-screen bg-gray-300 mx-2')  # 垂直分割线
    # 显示历史记录还是接口列表区域
    with ui.column():
        # 上方搜索框
        with ui.row():
            ui.input()
            ui.button('搜索')
        # 下方展示数据区域
        with ui.scroll_area().classes("h-screen"):
            ui.label('下方展示数据区域' * 100000)

    ui.separator().classes('w-[1px] h-screen bg-gray-300 mx-2')  # 垂直分割线
    # 右侧填写参数与调用结果界面
    with ui.column().classes('flex-1'):
        # ---------- Postman风格动态选项卡 ----------
        ui.label('选项卡区域')
        # tabs和current_tab用于管理多个选项卡的数据
        tabs = {}
        current_tab = None
        tab_bar = ui.row().classes('gap-2')
        tab_area = ui.column().classes('w-full')


def switch_tab(tab_name, tab_area, tabs):
    global current_tab
    current_tab = tab_name
    tab_area.clear()
    tab_data = tabs[tab_name]

    def send_request():
        params = []
        for row in tab_data["param_container"].slots:
            controls = row.default_slot.children
            enabled = controls[0].value
            key = controls[1].value
            value = controls[2].value
            dtype = controls[3].value
            comment = controls[4].value
            if enabled:
                params.append({'key': key, 'value': value, 'type': dtype, 'comment': comment})
        print(f"发送参数 [{tab_name}]:", params)

    with tab_area:
        ui.label('参数列表填写区域').classes('font-bold text-lg')
        with ui.scroll_area().classes('max-h-[45vh] w-full'):
            with ui.row().classes('w-full gap-2'):
                ui.button('添加参数', on_click=tab_data["add_param_row"])
                ui.button('发送请求', on_click=send_request).classes('bg-blue-500 text-white')
            tab_data["param_container"] = ui.column().classes('w-full gap-2')
            # 重新绘制所有参数行
            for _ in tab_data["param_rows"]:
                tab_data["add_param_row"]()

        ui.separator()
        ui.label('调用结果区域').classes('font-bold text-lg')
        # TODO: 后续这里要改成通过网络接收参数
        formatted_json = json.dumps(tab_data["json_data"], indent=4, ensure_ascii=False)
        ui.code(formatted_json).classes('w-full h-auto background:#f5f5f5')


def create_new_tab(tabs, tab_bar, tab_area):
    tab_name = f"Request {len(tabs)+1}"
    tab_data = {
        "param_rows": [],
        "param_container": None,
        "json_data": {
            "status": "success",
            "data": {
                "id": 123,
                "name": f"{tab_name}接口",
                "result": [1, 2, 3]
            }
        }
    }


    def add_param_row():
        with tab_data["param_container"]:
            row = ui.row().classes('gap-2 w-full items-center')
            with row:
                ui.checkbox(value=True)
                ui.input(placeholder='Key').classes('w-32')
                ui.input(placeholder='Value').classes('w-48')
                ui.select(['string', 'int', 'bool'], value='string').classes('w-24')
                ui.input(placeholder='备注').classes('w-40')
                ui.button(icon='close', on_click=row.delete).props('flat round dense')
            tab_data["param_rows"].append(row)

    tab_data["add_param_row"] = add_param_row
    tabs[tab_name] = tab_data
    with tab_bar:
        ui.button(tab_name, on_click=partial(switch_tab, tab_name, tab_area, tabs))\
            .classes('bg-white shadow-sm text-black')
    switch_tab(tab_name, tab_area, tabs)
    return tab_data


with ui.column().classes('w-full'):
    with tab_bar:
        ui.button('+', on_click=lambda: create_new_tab(tabs, tab_bar, tab_area)).classes('bg-green-200 text-black')
    # 初始化添加一个默认选项卡
    create_new_tab(tabs, tab_bar, tab_area)



# 使用推荐的多进程保护条件
if __name__ in {"__main__", "__mp_main__"}:
    ui.run()