from nicegui import ui
import json
from functools import partial


display_area = None
current_status = "接口列表"  # 添加状态管理
expanded_groups = {}  # 存储接口组的展开状态
selected_interface = None  # 存储选中的接口
tabs = {}  # 全局tabs变量
tab_area = None  # 全局tab_area变量
current_tab = None  # 全局current_tab变量

def send_request(tab_name, tab_data):
    params = []
    if not tab_data["param_rows"]:
        print("参数行未初始化")
        return
    for row in tab_data["param_rows"]:
        if hasattr(row, 'default_slot') and row.default_slot.children:
            controls = row.default_slot.children
            key = controls[0].text
            dtype = controls[1].text
            value = controls[2].value
            comment = controls[3].value
            params.append({'key': key, 'value': value, 'type': dtype, 'comment': comment})
    print(f"发送参数 [{tab_name}]:", params)
    
    # 创建只包含 key 和 value 的结果数据
    result_data = {}
    for param in params:
        if param['key']:  # 只添加有 key 的参数
            result_data[param['key']] = param['value']
    
    # 更新选项卡的结果数据
    tab_data["json_data"] = result_data
    tab_data["has_result"] = True
    
    # 直接更新结果区域的显示
    if tab_data.get("result_container"):
        tab_data["result_container"].clear()
        with tab_data["result_container"]:
            formatted_json = json.dumps(result_data, indent=4, ensure_ascii=False)
            ui.code(formatted_json).classes('w-full h-auto background:#f5f5f5')

def switch_tab(tab_name, tab_area, tabs):
    global current_tab
    current_tab = tab_name
    tab_area.clear()
    tab_data = tabs[tab_name]

    with tab_area:
        ui.label('参数列表填写区域').classes('font-bold text-lg')
        with ui.scroll_area().classes('max-h-[25vh] w-full'):
            with ui.row().classes('w-full gap-2'):
                ui.button('发送请求', on_click=lambda: send_request(tab_name, tab_data)).classes('bg-blue-500 text-white')
            
            # 添加表头
            with ui.row().classes('w-full gap-2 items-center py-2 border-b border-gray-300 bg-gray-50'):
                ui.label('Key').classes('w-32 text-sm font-bold text-gray-700')
                ui.label('类型').classes('w-24 text-sm font-bold text-gray-700')
                ui.label('Value').classes('w-48 text-sm font-bold text-gray-700')
                ui.label('备注').classes('w-40 text-sm font-bold text-gray-700')
            
            tab_data["param_container"] = ui.column().classes('w-full gap-2')
            # 重新绘制所有参数行
            for row_data in tab_data["param_rows"]:
                # 从现有行中获取参数名和类型
                if hasattr(row_data, 'default_slot') and row_data.default_slot.children:
                    key_label = row_data.default_slot.children[1]  # Key标签
                    type_label = row_data.default_slot.children[2]  # 类型标签
                    param_name = key_label.text if hasattr(key_label, 'text') else ''
                    param_type = type_label.text if hasattr(type_label, 'text') else 'string'
                    add_param_row(tab_data, param_name, param_type)
                else:
                    add_param_row(tab_data)

        # 添加一些空白区域，将结果区域推到下方
        ui.space().classes('h-[20vh]')
        
        ui.separator()
        ui.label('调用结果区域').classes('font-bold text-lg')
        # 创建结果区域容器
        tab_data["result_container"] = ui.column().classes('w-full')
        # 检查是否有调用结果数据
        if tab_data.get("has_result", False):
            # TODO: 后续这里要改成通过网络接收参数
            formatted_json = json.dumps(tab_data["json_data"], indent=4, ensure_ascii=False)
            with tab_data["result_container"]:
                ui.code(formatted_json).classes('w-full h-auto background:#f5f5f5')
        else:
            with tab_data["result_container"]:
                ui.label('这里展示远程调用结果').classes('text-gray-500 text-center py-8')

def add_param_row(tab_data, param_name=None, param_type=None):
    with tab_data["param_container"]:
        row = ui.row().classes('gap-2 w-full items-center')
        with row:
            ui.label(param_name or '').classes('w-32 text-sm font-medium')
            ui.label(param_type or 'string').classes('w-24 text-sm text-gray-600')
            ui.input(placeholder='Value').classes('w-48')
            ui.input(placeholder='备注').classes('w-40')
        tab_data["param_rows"].append(row)

def update_param_list(params):
    """更新当前选项卡的参数列表"""
    global current_tab, tabs
    if current_tab and current_tab in tabs:
        tab_data = tabs[current_tab]
        # 清空现有参数行
        tab_data["param_rows"].clear()
        if tab_data["param_container"]:
            tab_data["param_container"].clear()
            # 重新添加参数行
            for param in params:
                add_param_row(tab_data, param["name"], param["type"])

def create_new_tab(tabs, tab_bar, tab_area):
    tab_name = f"Request {len(tabs)+1}"
    tab_data = {
        "param_rows": [],
        "param_container": None,
        "has_result": False,
        "json_data": {
            "status": "success",
            "data": {
                "id": 123,
                "name": f"{tab_name}接口",
                "result": [1, 2, 3]
            }
        }
    }
    tabs[tab_name] = tab_data
    with tab_bar:
        ui.button(tab_name, on_click=partial(switch_tab, tab_name, tab_area, tabs))\
            .classes('bg-white shadow-sm text-black')
    switch_tab(tab_name, tab_area, tabs)
    return tab_data

def switch_status(status, display_area):
    """切换左侧显示状态"""
    global current_status, expanded_groups
    current_status = status
    display_area.clear()
    
    with display_area:
        if status == "接口列表":
            ui.label('接口列表').classes('text-xl font-bold mb-4')
            # 模拟接口分组数据
            interface_groups = {
                "用户管理": [
                    {"name": "用户登录", "method": "POST", "url": "/api/login", "status": "active"},
                    {"name": "获取用户信息", "method": "GET", "url": "/api/user/info", "status": "active"},
                    {"name": "更新用户资料", "method": "PUT", "url": "/api/user/profile", "status": "inactive"},
                    {"name": "删除用户", "method": "DELETE", "url": "/api/user/{id}", "status": "active"},
                    {"name": "获取用户列表", "method": "GET", "url": "/api/users", "status": "active"},
                    {"name": "创建用户", "method": "POST", "url": "/api/users", "status": "active"},
                    {"name": "批量删除用户", "method": "DELETE", "url": "/api/users/batch", "status": "active"},
                ],
                "权限管理": [
                    {"name": "用户权限查询", "method": "GET", "url": "/api/user/permissions", "status": "inactive"},
                    {"name": "修改用户权限", "method": "PUT", "url": "/api/user/permissions", "status": "active"},
                    {"name": "用户角色分配", "method": "POST", "url": "/api/user/roles", "status": "active"},
                    {"name": "获取角色列表", "method": "GET", "url": "/api/roles", "status": "active"},
                    {"name": "创建角色", "method": "POST", "url": "/api/roles", "status": "active"},
                    {"name": "更新角色", "method": "PUT", "url": "/api/roles/{id}", "status": "active"},
                    {"name": "删除角色", "method": "DELETE", "url": "/api/roles/{id}", "status": "active"},
                    {"name": "获取权限列表", "method": "GET", "url": "/api/permissions", "status": "active"},
                    {"name": "创建权限", "method": "POST", "url": "/api/permissions", "status": "active"},
                    {"name": "更新权限", "method": "PUT", "url": "/api/permissions/{id}", "status": "active"},
                    {"name": "删除权限", "method": "DELETE", "url": "/api/permissions/{id}", "status": "active"},
                ],
                "部门管理": [
                    {"name": "获取部门列表", "method": "GET", "url": "/api/departments", "status": "active"},
                    {"name": "创建部门", "method": "POST", "url": "/api/departments", "status": "active"},
                    {"name": "更新部门", "method": "PUT", "url": "/api/departments/{id}", "status": "active"},
                    {"name": "删除部门", "method": "DELETE", "url": "/api/departments/{id}", "status": "active"},
                ],
                "菜单管理": [
                    {"name": "获取菜单列表", "method": "GET", "url": "/api/menus", "status": "active"},
                    {"name": "创建菜单", "method": "POST", "url": "/api/menus", "status": "active"},
                    {"name": "更新菜单", "method": "PUT", "url": "/api/menus/{id}", "status": "active"},
                    {"name": "删除菜单", "method": "DELETE", "url": "/api/menus/{id}", "status": "active"},
                ],
                "系统管理": [
                    {"name": "获取系统配置", "method": "GET", "url": "/api/system/config", "status": "active"},
                    {"name": "更新系统配置", "method": "PUT", "url": "/api/system/config", "status": "active"},
                    {"name": "获取系统日志", "method": "GET", "url": "/api/system/logs", "status": "active"},
                    {"name": "清理系统日志", "method": "DELETE", "url": "/api/system/logs", "status": "active"},
                ],
                "文件管理": [
                    {"name": "获取文件列表", "method": "GET", "url": "/api/files", "status": "active"},
                    {"name": "上传文件", "method": "POST", "url": "/api/files/upload", "status": "active"},
                    {"name": "下载文件", "method": "GET", "url": "/api/files/{id}/download", "status": "active"},
                    {"name": "删除文件", "method": "DELETE", "url": "/api/files/{id}", "status": "active"},
                ],
                "通知管理": [
                    {"name": "获取通知列表", "method": "GET", "url": "/api/notifications", "status": "active"},
                    {"name": "发送通知", "method": "POST", "url": "/api/notifications", "status": "active"},
                    {"name": "标记通知已读", "method": "PUT", "url": "/api/notifications/{id}/read", "status": "active"},
                    {"name": "删除通知", "method": "DELETE", "url": "/api/notifications/{id}", "status": "active"},
                ],
                "数据管理": [
                    {"name": "获取统计数据", "method": "GET", "url": "/api/statistics", "status": "active"},
                    {"name": "导出数据", "method": "GET", "url": "/api/export", "status": "active"},
                    {"name": "导入数据", "method": "POST", "url": "/api/import", "status": "active"},
                    {"name": "备份数据", "method": "POST", "url": "/api/backup", "status": "active"},
                    {"name": "恢复数据", "method": "POST", "url": "/api/restore", "status": "active"},
                ],
                "系统服务": [
                    {"name": "获取API文档", "method": "GET", "url": "/api/docs", "status": "active"},
                    {"name": "健康检查", "method": "GET", "url": "/api/health", "status": "active"},
                    {"name": "获取版本信息", "method": "GET", "url": "/api/version", "status": "active"},
                ]
            }
            
            for group_name, interfaces in interface_groups.items():
                # 点击展开/收起
                def toggle_group(name=group_name):
                    expanded_groups[name] = not expanded_groups.get(name, False)
                    # 重新渲染整个接口列表
                    switch_status("接口列表", display_area)
                
                # 创建组标题行
                with ui.row().classes('w-full items-center py-2 border-b border-gray-200 cursor-pointer hover:bg-gray-50'):
                    # 展开/收起图标（可点击）
                    expanded = expanded_groups.get(group_name, False)
                    ui.button('', on_click=toggle_group).props('flat').classes('p-0 min-w-0 bg-transparent').classes('text-gray-500 hover:text-blue-500').props('icon=expand_more' if expanded else 'icon=chevron_right')
                    
                    ui.label(group_name).classes('font-bold flex-1 ml-2')
                    ui.label(f"({len(interfaces)}个接口)").classes('text-gray-500 text-sm')
                
                # 如果展开，显示接口列表
                if expanded_groups.get(group_name, False):
                    for interface in interfaces:
                        # 模拟接口参数（包含类型信息）
                        params = []
                        if interface["method"] == "GET":
                            params = [{"name": "page", "type": "int"}, {"name": "size", "type": "int"}, {"name": "keyword", "type": "string"}]
                        elif interface["method"] == "POST":
                            params = [{"name": "username", "type": "string"}, {"name": "password", "type": "string"}, {"name": "email", "type": "string"}]
                        elif interface["method"] == "PUT":
                            params = [{"name": "id", "type": "int"}, {"name": "name", "type": "string"}, {"name": "description", "type": "string"}]
                        elif interface["method"] == "DELETE":
                            params = [{"name": "id", "type": "int"}]
                        
                        # 判断是否选中
                        is_selected = selected_interface == f"{group_name}_{interface['name']}"
                        bg_class = "bg-blue-100" if is_selected else "bg-gray-50"
                        
                        def select_interface(name=group_name, interface_name=interface["name"], interface_params=params):
                            global selected_interface
                            selected_interface = f"{name}_{interface_name}"
                            # 更新右侧参数列表
                            update_param_list(interface_params)
                            # 重新渲染接口列表
                            switch_status("接口列表", display_area)
                        
                        with ui.row().classes(f'w-full items-center py-2 border-b border-gray-100 {bg_class} pl-8 cursor-pointer hover:bg-gray-100 relative'):
                            ui.label(interface["name"]).classes('font-medium flex-1')
                            param_names = [param["name"] for param in params]
                            ui.label(f"参数: {', '.join(param_names)}").classes('text-gray-600 text-sm flex-1')
                            
                            # 添加点击事件
                            ui.button('', on_click=select_interface).props('flat').classes('absolute inset-0 bg-transparent')
        
        elif status == "历史记录":
            ui.label('历史记录').classes('text-xl font-bold mb-4')
            # 模拟历史记录数据
            history_records = [
                {"time": "2024-01-15 14:30:25", "interface": "用户登录", "status": "成功", "duration": "120ms"},
                {"time": "2024-01-15 14:28:10", "interface": "获取用户信息", "status": "成功", "duration": "85ms"},
                {"time": "2024-01-15 14:25:45", "interface": "更新用户资料", "status": "失败", "duration": "200ms"},
                {"time": "2024-01-15 14:22:30", "interface": "用户登录", "status": "成功", "duration": "110ms"},
                {"time": "2024-01-15 14:20:15", "interface": "获取用户列表", "status": "成功", "duration": "150ms"},
                {"time": "2024-01-15 14:18:45", "interface": "创建用户", "status": "成功", "duration": "180ms"},
                {"time": "2024-01-15 14:16:20", "interface": "删除用户", "status": "成功", "duration": "95ms"},
                {"time": "2024-01-15 14:14:10", "interface": "获取角色列表", "status": "成功", "duration": "75ms"},
                {"time": "2024-01-15 14:12:35", "interface": "创建角色", "status": "失败", "duration": "220ms"},
                {"time": "2024-01-15 14:10:50", "interface": "更新角色", "status": "成功", "duration": "140ms"},
                {"time": "2024-01-15 14:08:25", "interface": "删除角色", "status": "成功", "duration": "88ms"},
                {"time": "2024-01-15 14:06:15", "interface": "获取权限列表", "status": "成功", "duration": "65ms"},
                {"time": "2024-01-15 14:04:40", "interface": "创建权限", "status": "成功", "duration": "160ms"},
                {"time": "2024-01-15 14:02:30", "interface": "更新权限", "status": "成功", "duration": "125ms"},
                {"time": "2024-01-15 14:00:15", "interface": "删除权限", "status": "失败", "duration": "180ms"},
                {"time": "2024-01-15 13:58:45", "interface": "获取部门列表", "status": "成功", "duration": "70ms"},
                {"time": "2024-01-15 13:56:20", "interface": "创建部门", "status": "成功", "duration": "145ms"},
                {"time": "2024-01-15 13:54:10", "interface": "更新部门", "status": "成功", "duration": "110ms"},
                {"time": "2024-01-15 13:52:35", "interface": "删除部门", "status": "成功", "duration": "92ms"},
                {"time": "2024-01-15 13:50:25", "interface": "获取菜单列表", "status": "成功", "duration": "80ms"},
                {"time": "2024-01-15 13:48:15", "interface": "创建菜单", "status": "成功", "duration": "155ms"},
                {"time": "2024-01-15 13:46:30", "interface": "更新菜单", "status": "失败", "duration": "195ms"},
                {"time": "2024-01-15 13:44:45", "interface": "删除菜单", "status": "成功", "duration": "85ms"},
                {"time": "2024-01-15 13:42:20", "interface": "获取系统配置", "status": "成功", "duration": "60ms"},
                {"time": "2024-01-15 13:40:10", "interface": "更新系统配置", "status": "成功", "duration": "130ms"},
                {"time": "2024-01-15 13:38:25", "interface": "获取系统日志", "status": "成功", "duration": "200ms"},
                {"time": "2024-01-15 13:36:15", "interface": "清理系统日志", "status": "成功", "duration": "300ms"},
                {"time": "2024-01-15 13:34:40", "interface": "获取文件列表", "status": "成功", "duration": "90ms"},
                {"time": "2024-01-15 13:32:30", "interface": "上传文件", "status": "成功", "duration": "500ms"},
                {"time": "2024-01-15 13:30:15", "interface": "下载文件", "status": "成功", "duration": "250ms"},
                {"time": "2024-01-15 13:28:45", "interface": "删除文件", "status": "成功", "duration": "75ms"},
                {"time": "2024-01-15 13:26:20", "interface": "获取通知列表", "status": "成功", "duration": "70ms"},
                {"time": "2024-01-15 13:24:10", "interface": "发送通知", "status": "成功", "duration": "120ms"},
                {"time": "2024-01-15 13:22:35", "interface": "标记通知已读", "status": "成功", "duration": "65ms"},
                {"time": "2024-01-15 13:20:15", "interface": "删除通知", "status": "成功", "duration": "80ms"},
                {"time": "2024-01-15 13:18:45", "interface": "获取统计数据", "status": "成功", "duration": "180ms"},
                {"time": "2024-01-15 13:16:30", "interface": "导出数据", "status": "成功", "duration": "400ms"},
                {"time": "2024-01-15 13:14:15", "interface": "导入数据", "status": "失败", "duration": "600ms"},
                {"time": "2024-01-15 13:12:40", "interface": "备份数据", "status": "成功", "duration": "800ms"},
                {"time": "2024-01-15 13:10:25", "interface": "恢复数据", "status": "成功", "duration": "1200ms"},
                {"time": "2024-01-15 13:08:10", "interface": "获取API文档", "status": "成功", "duration": "45ms"},
                {"time": "2024-01-15 13:06:35", "interface": "健康检查", "status": "成功", "duration": "30ms"},
                {"time": "2024-01-15 13:04:20", "interface": "获取版本信息", "status": "成功", "duration": "25ms"},
                {"time": "2024-01-15 13:02:45", "interface": "用户登录", "status": "失败", "duration": "150ms"},
                {"time": "2024-01-15 13:00:30", "interface": "获取用户信息", "status": "成功", "duration": "85ms"},
                {"time": "2024-01-15 12:58:15", "interface": "更新用户资料", "status": "成功", "duration": "135ms"},
                {"time": "2024-01-15 12:56:40", "interface": "删除用户", "status": "成功", "duration": "95ms"},
                {"time": "2024-01-15 12:54:25", "interface": "获取用户列表", "status": "成功", "duration": "120ms"},
                {"time": "2024-01-15 12:52:10", "interface": "创建用户", "status": "成功", "duration": "175ms"},
                {"time": "2024-01-15 12:50:45", "interface": "批量删除用户", "status": "成功", "duration": "220ms"},
                {"time": "2024-01-15 12:48:30", "interface": "用户权限查询", "status": "成功", "duration": "90ms"},
                {"time": "2024-01-15 12:46:15", "interface": "修改用户权限", "status": "成功", "duration": "145ms"},
                {"time": "2024-01-15 12:44:40", "interface": "用户角色分配", "status": "成功", "duration": "160ms"},
            ]
            
            for record in history_records:
                with ui.row().classes('w-full items-center py-2 border-b border-gray-200'):
                    ui.label(record["interface"]).classes('font-bold flex-1')
                    ui.label(record["status"]).classes(f'px-2 py-1 rounded text-white text-sm {"bg-green-500" if record["status"] == "成功" else "bg-red-500"}')
                    ui.label(f"时间: {record['time']}").classes('text-gray-600 text-sm flex-1 mx-2')
                    ui.label(f"耗时: {record['duration']}").classes('text-gray-600 text-sm flex-1')

# 禁用页面滚动
ui.add_body_html('<style>body { overflow: hidden; }</style>')

# 标题栏
with ui.header().classes("bg-blue-500 text-white"):
    ui.label("远程接口调用").classes("text-xl font-bold")


# 下方功能区
with ui.row().classes('w-full h-screen'):
    # 左侧功能选择按钮
    with ui.column():
        ui.button('接口列表', on_click=lambda: switch_status("接口列表", display_area)).classes('w-full mb-2')
        ui.button('历史记录', on_click=lambda: switch_status("历史记录", display_area)).classes('w-full')
    ui.separator().classes('w-[1px] h-screen bg-gray-300 mx-2')  # 垂直分割线
    # 显示历史记录还是接口列表区域
    with ui.column().classes('w-96 mx-0 p-0'):
        # 上方搜索框
        with ui.row():
            ui.input(placeholder='搜索...').classes('flex-1')
            ui.button('搜索').classes('bg-blue-500 text-white')
        # 下方展示数据区域
        with ui.scroll_area().classes("h-screen"):
            display_area = ui.column().classes('w-full p-2')

    ui.separator().classes('w-[1px] h-screen bg-gray-300 mx-2')  # 垂直分割线
    # 右侧填写参数与调用结果界面
    with ui.column().classes('flex-1'):
        # ---------- Postman风格动态选项卡 ---------
        # tabs和current_tab用于管理多个选项卡的数据
        tab_bar = ui.row().classes('gap-2')
        tab_area = ui.column().classes('w-full')

with ui.column().classes('w-full'):
    with tab_bar:
        ui.button('+', on_click=lambda: create_new_tab(tabs, tab_bar, tab_area)).classes('bg-green-200 text-black')
    # 初始化添加一个默认选项卡
    create_new_tab(tabs, tab_bar, tab_area)

# 初始化显示接口列表
switch_status("接口列表", display_area)

# 使用推荐的多进程保护条件
if __name__ in {"__main__", "__mp_main__"}:
    ui.run()