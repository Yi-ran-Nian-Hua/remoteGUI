from nicegui import ui
import json
from functools import partial
from datetime import datetime


display_area = None
current_status = "接口列表"  # 添加状态管理
expanded_groups = {}  # 存储接口组的展开状态
selected_interface = None  # 存储选中的接口
tabs = {}  # 全局tabs变量
tab_bar = None
tab_area = None
current_tab = None  # 全局current_tab变量
selected_record_ids = set()  # 存储选中的历史记录ID

# 模拟历史记录数据
history_records = [
    {"id": 1, "time": "2024-01-15 14:30:25", "interface": "用户登录", "status": "成功", "duration": "120ms", "parameters": {"username": "admin", "password": "123456"}, "result": "{\n  \"status\": \"success\",\n  \"data\": {\n    \"token\": \"abc123\"\n  }\n}"},
    {"id": 2, "time": "2024-01-15 14:28:10", "interface": "获取用户信息", "status": "成功", "duration": "85ms", "parameters": {"user_id": "123"}, "result": "{\n  \"status\": \"success\",\n  \"data\": {\n    \"name\": \"张三\",\n    \"email\": \"zhangsan@example.com\"\n  }\n}"},
    {"id": 3, "time": "2024-01-15 14:25:45", "interface": "更新用户资料", "status": "失败", "duration": "200ms", "parameters": {"user_id": "123", "name": "李四"}, "result": "{\n  \"status\": \"error\",\n  \"message\": \"用户不存在\"\n}"},
    {"id": 4, "time": "2024-01-15 14:22:30", "interface": "用户登录", "status": "成功", "duration": "110ms", "parameters": {"username": "user1", "password": "password123"}, "result": "{\n  \"status\": \"success\",\n  \"data\": {\n    \"token\": \"def456\"\n  }\n}"},
    {"id": 5, "time": "2024-01-15 14:20:15", "interface": "获取用户列表", "status": "成功", "duration": "150ms", "parameters": {"page": "1", "size": "10"}, "result": "{\n  \"status\": \"success\",\n  \"data\": {\n    \"users\": [\n      {\"id\": 1, \"name\": \"张三\"},\n      {\"id\": 2, \"name\": \"李四\"}\n    ]\n  }\n}"},
    {"id": 6, "time": "2024-01-15 14:18:45", "interface": "创建用户", "status": "成功", "duration": "180ms", "parameters": {"name": "王五", "email": "wangwu@example.com"}, "result": "{\n  \"status\": \"success\",\n  \"data\": {\n    \"id\": 3,\n    \"name\": \"王五\"\n  }\n}"},
    {"id": 7, "time": "2024-01-15 14:16:20", "interface": "删除用户", "status": "成功", "duration": "95ms", "parameters": {"user_id": "123"}, "result": "{\n  \"status\": \"success\",\n  \"message\": \"用户删除成功\"\n}"},
    {"id": 8, "time": "2024-01-15 14:14:10", "interface": "获取角色列表", "status": "成功", "duration": "75ms", "parameters": {}, "result": "{\n  \"status\": \"success\",\n  \"data\": {\n    \"roles\": [\n      {\"id\": 1, \"name\": \"管理员\"},\n      {\"id\": 2, \"name\": \"普通用户\"}\n    ]\n  }\n}"},
    {"id": 9, "time": "2024-01-15 14:12:35", "interface": "创建角色", "status": "失败", "duration": "220ms", "parameters": {"name": "测试角色"}, "result": "{\n  \"status\": \"error\",\n  \"message\": \"角色名称已存在\"\n}"},
    {"id": 10, "time": "2024-01-15 14:10:50", "interface": "更新角色", "status": "成功", "duration": "140ms", "parameters": {"role_id": "1", "name": "超级管理员"}, "result": "{\n  \"status\": \"success\",\n  \"message\": \"角色更新成功\"\n}"},
    {"id": 11, "time": "2024-01-15 14:08:25", "interface": "删除角色", "status": "成功", "duration": "88ms", "parameters": {"role_id": "2"}, "result": "{\n  \"status\": \"success\",\n  \"message\": \"角色删除成功\"\n}"},
    {"id": 12, "time": "2024-01-15 14:06:15", "interface": "获取权限列表", "status": "成功", "duration": "65ms", "parameters": {}, "result": "{\n  \"status\": \"success\",\n  \"data\": {\n    \"permissions\": [\n      {\"id\": 1, \"name\": \"用户管理\"},\n      {\"id\": 2, \"name\": \"角色管理\"}\n    ]\n  }\n}"},
    {"id": 13, "time": "2024-01-15 14:04:40", "interface": "创建权限", "status": "成功", "duration": "160ms", "parameters": {"name": "系统管理", "code": "system:manage"}, "result": "{\n  \"status\": \"success\",\n  \"data\": {\n    \"id\": 3,\n    \"name\": \"系统管理\"\n  }\n}"},
    {"id": 14, "time": "2024-01-15 14:02:30", "interface": "更新权限", "status": "成功", "duration": "125ms", "parameters": {"permission_id": "1", "name": "用户管理升级版"}, "result": "{\n  \"status\": \"success\",\n  \"message\": \"权限更新成功\"\n}"},
    {"id": 15, "time": "2024-01-15 14:00:15", "interface": "删除权限", "status": "失败", "duration": "180ms", "parameters": {"permission_id": "1"}, "result": "{\n  \"status\": \"error\",\n  \"message\": \"权限正在使用中，无法删除\"\n}"},
    {"id": 16, "time": "2024-01-15 13:58:45", "interface": "获取部门列表", "status": "成功", "duration": "70ms", "parameters": {}, "result": "{\n  \"status\": \"success\",\n  \"data\": {\n    \"departments\": [\n      {\"id\": 1, \"name\": \"技术部\"},\n      {\"id\": 2, \"name\": \"产品部\"}\n    ]\n  }\n}"},
    {"id": 17, "time": "2024-01-15 13:56:20", "interface": "创建部门", "status": "成功", "duration": "145ms", "parameters": {"name": "市场部", "description": "负责市场推广"}, "result": "{\n  \"status\": \"success\",\n  \"data\": {\n    \"id\": 3,\n    \"name\": \"市场部\"\n  }\n}"},
    {"id": 18, "time": "2024-01-15 13:54:10", "interface": "更新部门", "status": "成功", "duration": "110ms", "parameters": {"dept_id": "1", "name": "技术研发部"}, "result": "{\n  \"status\": \"success\",\n  \"message\": \"部门更新成功\"\n}"},
    {"id": 19, "time": "2024-01-15 13:52:35", "interface": "删除部门", "status": "成功", "duration": "92ms", "parameters": {"dept_id": "2"}, "result": "{\n  \"status\": \"success\",\n  \"message\": \"部门删除成功\"\n}"},
    {"id": 20, "time": "2024-01-15 13:50:25", "interface": "获取菜单列表", "status": "成功", "duration": "80ms", "parameters": {}, "result": "{\n  \"status\": \"success\",\n  \"data\": {\n    \"menus\": [\n      {\"id\": 1, \"name\": \"用户管理\"},\n      {\"id\": 2, \"name\": \"系统设置\"}\n    ]\n  }\n}"},
    {"id": 21, "time": "2024-01-15 13:48:15", "interface": "创建菜单", "status": "成功", "duration": "155ms", "parameters": {"name": "数据统计", "path": "/statistics"}, "result": "{\n  \"status\": \"success\",\n  \"data\": {\n    \"id\": 3,\n    \"name\": \"数据统计\"\n  }\n}"},
    {"id": 22, "time": "2024-01-15 13:46:30", "interface": "更新菜单", "status": "失败", "duration": "195ms", "parameters": {"menu_id": "1", "name": "用户管理升级"}, "result": "{\n  \"status\": \"error\",\n  \"message\": \"菜单名称重复\"\n}"},
    {"id": 23, "time": "2024-01-15 13:44:45", "interface": "删除菜单", "status": "成功", "duration": "85ms", "parameters": {"menu_id": "2"}, "result": "{\n  \"status\": \"success\",\n  \"message\": \"菜单删除成功\"\n}"},
    {"id": 24, "time": "2024-01-15 13:42:20", "interface": "获取系统配置", "status": "成功", "duration": "60ms", "parameters": {}, "result": "{\n  \"status\": \"success\",\n  \"data\": {\n    \"site_name\": \"管理系统\",\n    \"version\": \"1.0.0\"\n  }\n}"},
    {"id": 25, "time": "2024-01-15 13:40:10", "interface": "更新系统配置", "status": "成功", "duration": "130ms", "parameters": {"site_name": "新管理系统"}, "result": "{\n  \"status\": \"success\",\n  \"message\": \"配置更新成功\"\n}"},
    {"id": 26, "time": "2024-01-15 13:38:25", "interface": "获取系统日志", "status": "成功", "duration": "200ms", "parameters": {"page": "1", "size": "20"}, "result": "{\n  \"status\": \"success\",\n  \"data\": {\n    \"logs\": [\n      {\"id\": 1, \"level\": \"INFO\", \"message\": \"系统启动\"},\n      {\"id\": 2, \"level\": \"ERROR\", \"message\": \"数据库连接失败\"}\n    ]\n  }\n}"},
    {"id": 27, "time": "2024-01-15 13:36:15", "interface": "清理系统日志", "status": "成功", "duration": "300ms", "parameters": {"days": "30"}, "result": "{\n  \"status\": \"success\",\n  \"message\": \"清理了1000条日志\"\n}"},
    {"id": 28, "time": "2024-01-15 13:34:40", "interface": "获取文件列表", "status": "成功", "duration": "90ms", "parameters": {"path": "/uploads"}, "result": "{\n  \"status\": \"success\",\n  \"data\": {\n    \"files\": [\n      {\"name\": \"document.pdf\", \"size\": \"1.2MB\"},\n      {\"name\": \"image.jpg\", \"size\": \"500KB\"}\n    ]\n  }\n}"},
    {"id": 29, "time": "2024-01-15 13:32:30", "interface": "上传文件", "status": "成功", "duration": "500ms", "parameters": {"file": "test.txt"}, "result": "{\n  \"status\": \"success\",\n  \"data\": {\n    \"url\": \"/uploads/test.txt\",\n    \"size\": \"10KB\"\n  }\n}"},
    {"id": 30, "time": "2024-01-15 13:30:15", "interface": "下载文件", "status": "成功", "duration": "250ms", "parameters": {"file_id": "123"}, "result": "{\n  \"status\": \"success\",\n  \"data\": {\n    \"url\": \"/download/123\",\n    \"filename\": \"document.pdf\"\n  }\n}"},
    {"id": 31, "time": "2024-01-15 13:28:45", "interface": "删除文件", "status": "成功", "duration": "75ms", "parameters": {"file_id": "123"}, "result": "{\n  \"status\": \"success\",\n  \"message\": \"文件删除成功\"\n}"},
    {"id": 32, "time": "2024-01-15 13:26:20", "interface": "获取通知列表", "status": "成功", "duration": "70ms", "parameters": {"user_id": "123"}, "result": "{\n  \"status\": \"success\",\n  \"data\": {\n    \"notifications\": [\n      {\"id\": 1, \"title\": \"系统维护通知\", \"read\": false},\n      {\"id\": 2, \"title\": \"新功能上线\", \"read\": true}\n    ]\n  }\n}"},
    {"id": 33, "time": "2024-01-15 13:24:10", "interface": "发送通知", "status": "成功", "duration": "120ms", "parameters": {"title": "测试通知", "content": "这是一条测试通知"}, "result": "{\n  \"status\": \"success\",\n  \"data\": {\n    \"notification_id\": 3\n  }\n}"},
    {"id": 34, "time": "2024-01-15 13:22:35", "interface": "标记通知已读", "status": "成功", "duration": "65ms", "parameters": {"notification_id": "1"}, "result": "{\n  \"status\": \"success\",\n  \"message\": \"标记成功\"\n}"},
    {"id": 35, "time": "2024-01-15 13:20:15", "interface": "删除通知", "status": "成功", "duration": "80ms", "parameters": {"notification_id": "2"}, "result": "{\n  \"status\": \"success\",\n  \"message\": \"通知删除成功\"\n}"},
    {"id": 36, "time": "2024-01-15 13:18:45", "interface": "获取统计数据", "status": "成功", "duration": "180ms", "parameters": {"type": "user"}, "result": "{\n  \"status\": \"success\",\n  \"data\": {\n    \"total_users\": 1000,\n    \"active_users\": 800,\n    \"new_users\": 50\n  }\n}"},
    {"id": 37, "time": "2024-01-15 13:16:30", "interface": "导出数据", "status": "成功", "duration": "400ms", "parameters": {"type": "users", "format": "excel"}, "result": "{\n  \"status\": \"success\",\n  \"data\": {\n    \"download_url\": \"/export/users.xlsx\",\n    \"file_size\": \"2.5MB\"\n  }\n}"},
    {"id": 38, "time": "2024-01-15 13:14:15", "interface": "导入数据", "status": "失败", "duration": "600ms", "parameters": {"file": "data.csv"}, "result": "{\n  \"status\": \"error\",\n  \"message\": \"文件格式不支持\"\n}"},
    {"id": 39, "time": "2024-01-15 13:12:40", "interface": "备份数据", "status": "成功", "duration": "800ms", "parameters": {"backup_name": "daily_backup"}, "result": "{\n  \"status\": \"success\",\n  \"data\": {\n    \"backup_id\": \"backup_20240115\",\n    \"size\": \"500MB\"\n  }\n}"},
    {"id": 40, "time": "2024-01-15 13:10:25", "interface": "恢复数据", "status": "成功", "duration": "1200ms", "parameters": {"backup_id": "backup_20240115"}, "result": "{\n  \"status\": \"success\",\n  \"message\": \"数据恢复成功\"\n}"},
    {"id": 41, "time": "2024-01-15 13:08:10", "interface": "获取API文档", "status": "成功", "duration": "45ms", "parameters": {}, "result": "{\n  \"status\": \"success\",\n  \"data\": {\n    \"swagger_url\": \"/api/docs\",\n    \"version\": \"2.0\"\n  }\n}"},
    {"id": 42, "time": "2024-01-15 13:06:35", "interface": "健康检查", "status": "成功", "duration": "30ms", "parameters": {}, "result": "{\n  \"status\": \"success\",\n  \"data\": {\n    \"database\": \"ok\",\n    \"redis\": \"ok\",\n    \"uptime\": \"24h\"\n  }\n}"},
    {"id": 43, "time": "2024-01-15 13:04:20", "interface": "获取版本信息", "status": "成功", "duration": "25ms", "parameters": {}, "result": "{\n  \"status\": \"success\",\n  \"data\": {\n    \"version\": \"1.0.0\",\n    \"build_time\": \"2024-01-15\"\n  }\n}"},
    {"id": 44, "time": "2024-01-15 13:02:45", "interface": "用户登录", "status": "失败", "duration": "150ms", "parameters": {"username": "invalid", "password": "wrong"}, "result": "{\n  \"status\": \"error\",\n  \"message\": \"用户名或密码错误\"\n}"},
    {"id": 45, "time": "2024-01-15 13:00:30", "interface": "获取用户信息", "status": "成功", "duration": "85ms", "parameters": {"user_id": "456"}, "result": "{\n  \"status\": \"success\",\n  \"data\": {\n    \"name\": \"赵六\",\n    \"email\": \"zhaoliu@example.com\"\n  }\n}"},
    {"id": 46, "time": "2024-01-15 12:58:15", "interface": "更新用户资料", "status": "成功", "duration": "135ms", "parameters": {"user_id": "456", "name": "赵六升级版"}, "result": "{\n  \"status\": \"success\",\n  \"message\": \"用户资料更新成功\"\n}"},
    {"id": 47, "time": "2024-01-15 12:56:40", "interface": "删除用户", "status": "成功", "duration": "95ms", "parameters": {"user_id": "789"}, "result": "{\n  \"status\": \"success\",\n  \"message\": \"用户删除成功\"\n}"},
    {"id": 48, "time": "2024-01-15 12:54:25", "interface": "获取用户列表", "status": "成功", "duration": "120ms", "parameters": {"page": "2", "size": "10"}, "result": "{\n  \"status\": \"success\",\n  \"data\": {\n    \"users\": [\n      {\"id\": 11, \"name\": \"用户11\"},\n      {\"id\": 12, \"name\": \"用户12\"}\n    ]\n  }\n}"},
    {"id": 49, "time": "2024-01-15 12:52:10", "interface": "创建用户", "status": "成功", "duration": "175ms", "parameters": {"name": "新用户", "email": "newuser@example.com"}, "result": "{\n  \"status\": \"success\",\n  \"data\": {\n    \"id\": 13,\n    \"name\": \"新用户\"\n  }\n}"},
    {"id": 50, "time": "2024-01-15 12:50:45", "interface": "批量删除用户", "status": "成功", "duration": "220ms", "parameters": {"user_ids": "[1,2,3]"}, "result": "{\n  \"status\": \"success\",\n  \"message\": \"批量删除成功，删除了3个用户\"\n}"},
    {"id": 51, "time": "2024-01-15 12:48:30", "interface": "用户权限查询", "status": "成功", "duration": "90ms", "parameters": {"user_id": "123"}, "result": "{\n  \"status\": \"success\",\n  \"data\": {\n    \"permissions\": [\n      \"user:read\",\n      \"user:write\"\n    ]\n  }\n}"},
    {"id": 52, "time": "2024-01-15 12:46:15", "interface": "修改用户权限", "status": "成功", "duration": "145ms", "parameters": {"user_id": "123", "permissions": "[\\\"user:read\\\",\\\"user:write\\\",\\\"admin:read\\\"]"}, "result": "{\n  \"status\": \"success\",\n  \"message\": \"权限修改成功\"\n}"},
    {"id": 53, "time": "2024-01-15 12:44:40", "interface": "用户角色分配", "status": "成功", "duration": "160ms", "parameters": {"user_id": "123", "role_ids": "[1,2]"}, "result": "{\n  \"status\": \"success\",\n  \"message\": \"角色分配成功\"\n}"},
]

def delete_selected_records():
    global selected_record_ids, history_records
    if selected_record_ids:
        print(f"删除选中的记录: {selected_record_ids}")
        # 从历史记录列表中删除选中的记录
        history_records = [record for record in history_records if record["id"] not in selected_record_ids]
        selected_record_ids.clear()
        # 重新渲染历史记录
        switch_status("历史记录", display_area)
    else:
        print("当前没有选中任何项目")
        # 可以在这里添加UI提示

def select_all_records():
    global selected_record_ids, history_records
    selected_record_ids.clear()
    # 添加所有记录ID
    for record in history_records:
        selected_record_ids.add(record["id"])
    # 重新渲染历史记录
    switch_status("历史记录", display_area)

def deselect_all_records():
    global selected_record_ids
    selected_record_ids.clear()
    # 重新渲染历史记录
    switch_status("历史记录", display_area)

def send_request(tab_name, tab_data):
    global history_records
    params = []
    if not tab_data.get("params"):
        print("参数数据未初始化")
        return
    
    # 直接从参数数据读取
    for param in tab_data["params"]:
        params.append({
            'key': param["key"], 
            'value': param["value"], 
            'type': param["type"], 
            'comment': param["comment"]
        })
    
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
    
    # 保存到历史记录
    save_to_history(tab_name, result_data, formatted_json)

def save_to_history(interface_name, parameters, result):
    global history_records
    # 判断是否有实际调用结果
    status = "成功"
    if result == "未执行请求" or not result or (isinstance(result, str) and result.strip() == "未执行请求"):
        status = "未调用"
    # 生成新的历史记录
    new_record = {
        "id": len(history_records) + 1,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "interface": interface_name,
        "status": status,
        "duration": "120ms",
        "parameters": parameters,
        "result": result
    }
    history_records.insert(0, new_record)  # 插入到列表开头，最新的在前面
    # 动态刷新历史记录区域
    if 'display_area' in globals() and current_status == "历史记录":
        switch_status("历史记录", display_area)

def save_current_data(tab_name, tab_data):
    """保存当前选项卡的数据到历史记录"""
    # 收集当前参数
    params = []
    if tab_data.get("params"):
        for param in tab_data["params"]:
            params.append({
                'key': param["key"], 
                'value': param["value"], 
                'type': param["type"], 
                'comment': param["comment"]
            })
    
    # 创建参数数据
    result_data = {}
    for param in params:
        if param['key']:  # 只添加有 key 的参数
            result_data[param['key']] = param['value']
    
    # 生成结果文本
    if tab_data.get("has_result", False):
        if tab_name.startswith("历史记录-") and tab_data.get("result"):
            result_text = tab_data["result"]
        else:
            result_text = json.dumps(result_data, indent=4, ensure_ascii=False)
    else:
        result_text = "未执行请求"
    
    # 保存到历史记录
    save_to_history(tab_name, result_data, result_text)

def load_history_record(record):
    """从历史记录加载数据到新选项卡"""
    global tabs, tab_bar, tab_area
    # 创建新选项卡
    tab_name = f"历史记录-{record['interface']}-{record['id']}"
    tab_data = {
        "param_rows": [],
        "param_container": None,
        "has_result": True,
        "json_data": record["parameters"],
        "result": record["result"],
        "params": []  # 初始化参数数据
    }
    tabs[tab_name] = tab_data
    
    # 添加选项卡按钮
    create_tab_button(tab_name, tab_bar, tab_area, tabs)
    
    # 切换到新选项卡
    switch_tab(tab_name, tab_area, tabs)

def switch_tab(tab_name, tab_area, tabs):
    global current_tab, tab_bar
    # 保存当前tab的参数状态（如果有的话）
    if current_tab and current_tab in tabs:
        current_tab_data = tabs[current_tab]
        # 参数数据已经在on_change事件中自动保存，这里不需要额外操作
    
    current_tab = tab_name
    tab_area.clear()
    tab_data = tabs[tab_name]
    render_tab_bar(tabs, tab_bar, tab_area)
    
    with tab_area:
        ui.label('参数列表填写区域').classes('font-bold text-lg')
        with ui.row().classes('w-full gap-2'):
            ui.button('发送请求', on_click=lambda: send_request(tab_name, tab_data)).classes('bg-blue-500 text-white')
            ui.button('保存', on_click=lambda: save_current_data(tab_name, tab_data)).classes('bg-green-500 text-white')
            ui.button('清空', on_click=lambda: clear_params(tab_name, tab_data)).classes('bg-gray-500 text-white')
        with ui.scroll_area().classes('h-[50vh] w-full'):
            # 添加表头
            with ui.row().classes('w-full gap-2 items-center py-2 border-b border-gray-300 bg-gray-50'):
                ui.label('Key').classes('w-32 text-sm font-bold text-gray-700')
                ui.label('类型').classes('w-24 text-sm font-bold text-gray-700')
                ui.label('Value').classes('w-48 text-sm font-bold text-gray-700')
                ui.label('备注').classes('w-40 text-sm font-bold text-gray-700')
            tab_data["param_container"] = ui.column().classes('w-full gap-2')
            # 如果是历史记录选项卡，从历史数据加载参数
            if tab_name.startswith("历史记录-") and tab_data.get("json_data"):
                for key, value in tab_data["json_data"].items():
                    add_param_row(tab_data, key, "string", value)
            else:
                # 从现有参数数据重新生成UI
                if tab_data.get("params"):
                    for param in tab_data["params"]:
                        add_param_row(tab_data, param["key"], param["type"], param["value"], param["comment"], add_to_data=False)
        ui.separator()
        ui.label('调用结果区域').classes('font-bold text-lg')
        tab_data["result_container"] = ui.column().classes('w-full')
        if tab_data.get("has_result", False):
            if tab_name.startswith("历史记录-") and tab_data.get("result"):
                with tab_data["result_container"]:
                    ui.code(tab_data["result"]).classes('w-full h-auto background:#f5f5f5')
            else:
                formatted_json = json.dumps(tab_data["json_data"], indent=4, ensure_ascii=False)
                with tab_data["result_container"]:
                    ui.code(formatted_json).classes('w-full h-auto background:#f5f5f5')
        else:
            with tab_data["result_container"]:
                ui.label('这里展示远程调用结果').classes('text-gray-500 text-center py-8')

def create_tab_button(tab_name, tab_bar, tab_area, tabs):
    global current_tab
    is_active = current_tab == tab_name
    bg_class = 'bg-blue-100 border-b-2 border-blue-500' if is_active else 'bg-white hover:bg-gray-50'
    tab_data = tabs[tab_name]
    editing = tab_data.get('editing', False)
    with tab_bar:
        with ui.row().classes(f'{bg_class} flex items-center rounded-t-lg px-4 py-1.5 mr-1').on(
            'dblclick', lambda e, name=tab_name: start_edit_tab_name(name, tabs, tab_bar, tab_area)
        ):
            if editing:
                def save_name(e, old_name=tab_name):
                    new_name = e.sender.value.strip()
                    if new_name and new_name != old_name and new_name not in tabs:
                        tabs[new_name] = tabs.pop(old_name)
                        tabs[new_name]['editing'] = False
                        global current_tab
                        if current_tab == old_name:
                            current_tab = new_name
                        render_tab_bar(tabs, tab_bar, tab_area)
                        switch_tab(new_name, tab_area, tabs)
                    else:
                        tabs[old_name]['editing'] = False
                        render_tab_bar(tabs, tab_bar, tab_area)
                ui.input(value=tab_name).classes('w-24 text-black text-center bg-transparent border-none shadow-none p-0').props('dense autofocus').on('blur', save_name).on('keydown.enter', save_name)
            else:
                ui.button(tab_name, on_click=partial(switch_tab, tab_name, tab_area, tabs))\
                    .classes('bg-transparent text-black border-none shadow-none p-0')\
                    .props('flat')
            def delete_tab(tab_name=tab_name):
                delete_tab_by_name(tab_name, tabs, tab_bar, tab_area)
            ui.button('×', on_click=delete_tab)\
                .classes('bg-transparent text-gray-500 hover:text-red-500 rounded-full w-5 h-5 p-0 border-none shadow-none text-base font-bold')\
                .props('flat')

def start_edit_tab_name(tab_name, tabs, tab_bar, tab_area):
    tabs[tab_name]['editing'] = True
    render_tab_bar(tabs, tab_bar, tab_area)

def render_tab_bar(tabs, tab_bar, tab_area):
    tab_bar.clear()
    # + 按钮
    with tab_bar:
        with ui.row().classes('bg-white hover:bg-gray-50 flex items-center rounded-t-lg px-4 py-1.5 mr-1'):
            ui.button('+', on_click=lambda: create_new_tab(tabs, tab_bar, tab_area))\
                .classes('bg-transparent text-black border-none shadow-none p-0 text-xl font-bold min-w-[2.5rem] min-h-[2.5rem] flex items-center justify-center mt-1')\
                .props('flat')
        # 其他tab
        for remaining_tab_name in tabs.keys():
            create_tab_button(remaining_tab_name, tab_bar, tab_area, tabs)

def delete_tab_by_name(tab_name, tabs, tab_bar, tab_area):
    global current_tab
    if tab_name in tabs:
        del tabs[tab_name]
    render_tab_bar(tabs, tab_bar, tab_area)
    if current_tab == tab_name:
        if tabs:
            first_tab = list(tabs.keys())[0]
            switch_tab(first_tab, tab_area, tabs)
        else:
            create_new_tab(tabs, tab_bar, tab_area)

def create_new_tab(tabs, tab_bar, tab_area):
    base = "Request"
    i = 1
    while f"{base} {i}" in tabs:
        i += 1
    tab_name = f"{base} {i}"
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
        },
        "status": "未调用",
        "params": []  # 初始化参数数据
    }
    tabs[tab_name] = tab_data
    render_tab_bar(tabs, tab_bar, tab_area)
    switch_tab(tab_name, tab_area, tabs)
    return tab_data

def update_param_list(params):
    """更新当前选项卡的参数列表"""
    global current_tab, tabs
    if current_tab and current_tab in tabs:
        tab_data = tabs[current_tab]
        # 清空现有参数数据
        tab_data["params"] = []
        tab_data["param_rows"] = []
        if tab_data["param_container"]:
            tab_data["param_container"].clear()
            # 重新添加参数行
            for param in params:
                add_param_row(tab_data, param["name"], param["type"])

def add_param_row(tab_data, param_name=None, param_type=None, param_value=None, param_comment=None, add_to_data=True):
    """添加参数行，数据与UI分离"""
    # 创建参数数据
    param_data = {
        "key": param_name or "",
        "type": param_type or "string", 
        "value": param_value or "",
        "comment": param_comment or ""
    }
    
    # 将参数数据添加到tab的params列表（仅在需要时）
    if add_to_data:
        if "params" not in tab_data:
            tab_data["params"] = []
        tab_data["params"].append(param_data)
    
    # 生成UI
    with tab_data["param_container"]:
        row = ui.row().classes('gap-2 w-full items-center')
        with row:
            ui.label(param_data["key"]).classes('w-32 text-sm font-medium')
            ui.label(param_data["type"]).classes('w-24 text-sm text-gray-600')
            
            # Value输入框，绑定到数据
            def update_value(e, param=param_data):
                param["value"] = e.value
            value_input = ui.input(placeholder='Value', value=param_data["value"]).classes('w-48').on('change', update_value)
            
            # 备注输入框，绑定到数据
            def update_comment(e, param=param_data):
                param["comment"] = e.value
            comment_input = ui.input(placeholder='备注', value=param_data["comment"]).classes('w-40').on('change', update_comment)
        
        # 保存UI引用（可选）
        if "param_rows" not in tab_data:
            tab_data["param_rows"] = []
        tab_data["param_rows"].append(row)

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
            
            # 添加删除按钮
            with ui.row().classes('w-full gap-2 mb-4'):
                ui.button('删除选中', on_click=delete_selected_records).classes('bg-red-500 text-white')
                ui.button('全选', on_click=select_all_records).classes('bg-blue-500 text-white')
                ui.button('取消全选', on_click=deselect_all_records).classes('bg-gray-500 text-white')
            
            for record in history_records:
                def on_checkbox_change(e, record_id=record["id"]):
                    if e.value:
                        selected_record_ids.add(record_id)
                    else:
                        selected_record_ids.discard(record_id)
                with ui.row().classes('w-full items-center py-2 border-b border-gray-200 hover:bg-gray-50 relative'):
                    ui.checkbox(value=record["id"] in selected_record_ids, on_change=on_checkbox_change)
                    # 记录信息（可点击）
                    with ui.column().classes('flex-1 ml-2 cursor-pointer').on('click', lambda r=record: load_history_record(r)):
                        ui.label(record["interface"]).classes('font-bold')
                        ui.label(f"时间: {record['time']}").classes('text-gray-600 text-sm')
                    # 状态颜色映射
                    status_color = {
                        "成功": "bg-green-500",
                        "失败": "bg-red-500",
                        "未调用": "bg-gray-400"
                    }
                    ui.label(record["status"]).classes(f'px-2 py-1 rounded text-white text-sm {status_color.get(record["status"], "bg-gray-400")}')
                    ui.label(f"耗时: {record['duration']}" ).classes('text-gray-600 text-sm')

def clear_params(tab_name, tab_data):
    """清空当前选项卡的参数"""
    # 清空参数数据
    tab_data["params"] = []
    tab_data["param_rows"] = []
    if tab_data["param_container"]:
        tab_data["param_container"].clear()

# 禁用页面滚动
ui.add_body_html('<style>body { overflow: hidden; }</style>')

# 标题栏
with ui.header().classes("bg-blue-500 text-white"):
    ui.label("远程接口调用").classes("text-xl font-bold")


# 下方功能区
with ui.row().classes('w-full h-screen mt-0'):
    # 左侧功能选择按钮
    with ui.column():
        ui.button('接口列表', on_click=lambda: switch_status("接口列表", display_area)).classes('w-full mb-2')
        ui.button('历史记录', on_click=lambda: switch_status("历史记录", display_area)).classes('w-full')
    ui.separator().classes('w-[1px] h-screen bg-gray-300')  # 垂直分割线
    # 显示历史记录还是接口列表区域
    with ui.column().classes('w-96 mx-0 p-0'):
        # 上方搜索框 - 居中并占满宽度
        with ui.row().classes('w-full justify-center px-2 py-2'):
            with ui.row().classes('w-full max-w-sm gap-2'):
                ui.input(placeholder='搜索...').classes('flex-1')
                ui.button('搜索').classes('bg-blue-500 text-white')
        # 下方展示数据区域
        with ui.scroll_area().classes("h-screen"):
            display_area = ui.column().classes('w-full -m-3')

    ui.separator().classes('w-[1px] h-screen bg-gray-300')  # 垂直分割线
    # 右侧填写参数与调用结果界面
    with ui.column().classes('flex-1'):
        # ---------- Postman风格动态选项卡 ---------
        # tabs和current_tab用于管理多个选项卡的数据
        with ui.column().classes('w-full'):
            tab_bar = ui.row().classes('gap-2')
            tab_area = ui.column().classes('w-full')
            render_tab_bar(tabs, tab_bar, tab_area)
            create_new_tab(tabs, tab_bar, tab_area)

# 初始化显示接口列表
switch_status("接口列表", display_area)

# 使用推荐的多进程保护条件
if __name__ in {"__main__", "__mp_main__"}:
    ui.run()