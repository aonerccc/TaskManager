import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox, END
import random
import pyperclip
import json
import os
import appdirs

# 设置数据文件路径
DATA_DIR = appdirs.user_data_dir("TaskManager")
os.makedirs(DATA_DIR, exist_ok=True)
DATA_FILE = os.path.join(DATA_DIR, "task_manager_data.json")

# 全局变量
accounts = []
tasks = []
user_assignments = {}
assignment_count = {}
min_tasks = 1
max_tasks = 5
random_assign = True
ensure_all_tasks = 5
current_page = "main"
users_frame = None

def save_data():
    data = {
        "accounts": accounts,
        "tasks": tasks,
        "user_assignments": user_assignments,
        "assignment_count": assignment_count,
        "settings": {
            "min_tasks": min_tasks,
            "max_tasks": max_tasks,
            "random_assign": random_assign,
            "ensure_all_tasks": ensure_all_tasks
        }
    }
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_data():
    global accounts, tasks, user_assignments, assignment_count, min_tasks, max_tasks, random_assign, ensure_all_tasks
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        accounts = data.get("accounts", [])
        tasks = data.get("tasks", [])
        user_assignments = data.get("user_assignments", {})
        assignment_count = data.get("assignment_count", {})
        settings = data.get("settings", {})
        min_tasks = settings.get("min_tasks", 1)
        max_tasks = settings.get("max_tasks", 5)
        random_assign = settings.get("random_assign", True)
        ensure_all_tasks = settings.get("ensure_all_tasks", 5)

        # 确保 assignment_count 包含所有当前的任务
        for user in accounts:
            if user not in assignment_count:
                assignment_count[user] = {}
            for task in tasks:
                if task['name'] not in assignment_count[user]:
                    assignment_count[user][task['name']] = 0

def show_page(page):
    global current_page
    current_page = page
    for widget in main_frame.winfo_children():
        widget.destroy()
    if page == "main":
        show_main_page()
    elif page == "task_list":
        show_task_list_page()
    elif page == "assign_rules":
        show_assign_rules_page()

def show_main_page():
    global accounts, users_frame

    create_user_frame = ttk.Frame(main_frame)
    create_user_frame.pack(fill=X, padx=10, pady=10)

    entry_users = ttk.Entry(create_user_frame)
    entry_users.pack(side=LEFT, fill=X, expand=True, padx=(0, 5))

    def create_users():
        try:
            num_users = int(entry_users.get())
            current_count = len(accounts)
            for i in range(num_users):
                accounts.append(f"{current_count + i + 1}")
            entry_users.delete(0, 'end')
            update_user_display()
            save_data()
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")

    create_button = ttk.Button(create_user_frame, text="创建", command=create_users)
    create_button.pack(side=LEFT)

    users_frame = ttk.Frame(main_frame)
    users_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

    update_user_display()

def update_user_display():
    global users_frame
    for widget in users_frame.winfo_children():
        widget.destroy()

    for i, user in enumerate(accounts):
        user_frame = ttk.Frame(users_frame)
        user_frame.pack(fill=X, padx=5, pady=(15, 5), anchor='w')

        user_label = ttk.Label(user_frame, text=user,
                               style="User.TLabel",
                               padding=(5, 2),
                               background="#FFA500")
        user_label.pack(fill=X)

        if user in user_assignments:
            for task in user_assignments[user]:
                task_frame = ttk.Frame(user_frame)
                task_frame.pack(fill=X, padx=5, pady=2)

                task_button = ttk.Frame(task_frame, style="Task.TFrame")
                task_button.pack(side=LEFT, fill=X, expand=True)

                task_name_label = ttk.Label(task_button, text=task['name'],
                                            style="TaskName.TLabel")
                task_name_label.pack(side=LEFT, padx=5)

                details_frame = ttk.Frame(task_button)
                details_frame.pack(side=LEFT, fill=X, expand=True)

                for detail in task['details']:
                    if isinstance(detail, dict) and 'text' in detail and 'url' in detail:
                        detail_label = ttk.Label(details_frame, text=detail['text'],
                                                 style="TaskDetail.TLabel",
                                                 cursor="hand2", foreground="blue")
                        detail_label.pack(side=LEFT, padx=2)
                        detail_label.bind("<Button-1>", lambda e, url=detail['url']: copy_url(url))
                    else:
                        detail_label = ttk.Label(details_frame, text=detail,
                                                 style="TaskDetail.TLabel")
                        detail_label.pack(side=LEFT, padx=2)

                ttk.Separator(task_frame, orient='horizontal', style="TaskSeparator.TSeparator").pack(fill=X, pady=2)

def show_task_list_page():
    for widget in main_frame.winfo_children():
        widget.destroy()

    task_list_frame = ttk.Frame(main_frame)
    task_list_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

    for task in tasks:
        task_frame = ttk.Frame(task_list_frame, style="Task.TFrame")
        task_frame.pack(fill=X, padx=5, pady=5)

        task_name_label = ttk.Label(task_frame, text=task['name'], style="TaskName.TLabel")
        task_name_label.pack(side=LEFT, padx=5)

        details_frame = ttk.Frame(task_frame, style="TaskDetails.TFrame")
        details_frame.pack(side=LEFT, fill=X, expand=True)

        for detail in task['details']:
            if isinstance(detail, dict) and 'text' in detail and 'url' in detail:
                detail_label = ttk.Label(details_frame, text=detail['text'],
                                         style="TaskDetail.TLabel",
                                         cursor="hand2", foreground="blue")
                detail_label.pack(side=LEFT, padx=2)
                detail_label.bind("<Button-1>", lambda e, url=detail['url']: copy_url(url))
            else:
                detail_label = ttk.Label(details_frame, text=detail,
                                         style="TaskDetail.TLabel")
                detail_label.pack(side=LEFT, padx=2)

        edit_button = ttk.Button(task_frame, text="编辑", command=lambda t=task: re_edit_task(t))
        edit_button.pack(side=RIGHT, padx=5)

        delete_button = ttk.Button(task_frame, text="删除", command=lambda t=task: delete_task(t))
        delete_button.pack(side=RIGHT, padx=5)

    add_task_button = ttk.Button(main_frame, text="添加新任务", command=show_add_task)
    add_task_button.pack(pady=10)

def show_add_task():
    task_window = ttk.Frame(main_frame)
    task_window.pack(fill=BOTH, expand=True, padx=10, pady=10)

    name_frame = ttk.Frame(task_window)
    name_frame.pack(fill=X, pady=(5, 0))

    label_name = ttk.Label(name_frame, text="任务名称:", bootstyle="info")
    label_name.pack(side=LEFT, padx=5)

    entry_name = ttk.Entry(name_frame)
    entry_name.pack(side=LEFT, fill=X, expand=True, padx=5)

    details_frame = ttk.Frame(task_window)
    details_frame.pack(fill=X, pady=5)

    detail_entries = []

    def add_detail_entry():
        detail_frame = ttk.Frame(details_frame)
        detail_frame.pack(fill=X, pady=5)

        label_detail = ttk.Label(detail_frame, text="任务详情:", bootstyle="warning")
        label_detail.pack(side=LEFT, padx=5)

        entry_detail = ttk.Entry(detail_frame)
        entry_detail.pack(side=LEFT, fill=X, expand=True, padx=5)

        entry_link = ttk.Entry(detail_frame, width=20)
        entry_link.pack(side=LEFT, padx=5)
        entry_link.insert(0, "输入链接")
        entry_link.bind("<FocusIn>", lambda e: entry_link.delete(0, END) if entry_link.get() == "输入链接" else None)
        entry_link.bind("<FocusOut>", lambda e: entry_link.insert(0, "输入链接") if entry_link.get() == "" else None)

        def update_text_color(*args):
            if entry_link.get() and entry_link.get() != "输入链接":
                entry_detail.configure(foreground="blue")
            else:
                entry_detail.configure(foreground="black")

        entry_link.bind("<KeyRelease>", update_text_color)

        detail_entries.append((entry_detail, entry_link))

    add_detail_entry()

    add_detail_button = ttk.Button(task_window, text="➕ 添加更多详情", bootstyle=PRIMARY, command=add_detail_entry)
    add_detail_button.pack(pady=5)

    def save_task():
        task_name = entry_name.get()
        task_details = []
        for entry_detail, entry_link in detail_entries:
            if entry_detail.get():
                if entry_link.get() and entry_link.get() != "输入链接":
                    task_details.append({'text': entry_detail.get(), 'url': entry_link.get()})
                else:
                    task_details.append(entry_detail.get())
        if task_name and task_details:
            tasks.append({'name': task_name, 'details': task_details})
            save_data()
            show_page("task_list")
        else:
            messagebox.showwarning("警告", "请填写任务名和任务详情")

    save_button = ttk.Button(task_window, text="保存任务", bootstyle=SUCCESS, command=save_task)
    save_button.pack(side=LEFT, padx=5, pady=10)

    cancel_button = ttk.Button(task_window, text="取消", bootstyle=SECONDARY, command=lambda: show_page("task_list"))
    cancel_button.pack(side=LEFT, padx=5, pady=10)

def re_edit_task(task):
    task_window = ttk.Frame(main_frame)
    task_window.pack(fill=BOTH, expand=True, padx=10, pady=10)

    name_frame = ttk.Frame(task_window)
    name_frame.pack(fill=X, pady=(5, 0))

    label_name = ttk.Label(name_frame, text="任务名称:", bootstyle="info")
    label_name.pack(side=LEFT, padx=5)

    entry_name = ttk.Entry(name_frame)
    entry_name.pack(side=LEFT, fill=X, expand=True, padx=5)
    entry_name.insert(0, task['name'])

    details_frame = ttk.Frame(task_window)
    details_frame.pack(fill=X, pady=5)

    detail_entries = []

    def add_detail_entry(detail=None):
        detail_frame = ttk.Frame(details_frame)
        detail_frame.pack(fill=X, pady=5)

        label_detail = ttk.Label(detail_frame, text="任务详情:", bootstyle="warning")
        label_detail.pack(side=LEFT, padx=5)

        entry_detail = ttk.Entry(detail_frame)
        entry_detail.pack(side=LEFT, fill=X, expand=True, padx=5)

        entry_link = ttk.Entry(detail_frame, width=20)
        entry_link.pack(side=LEFT, padx=5)
        entry_link.insert(0, "输入链接")
        entry_link.bind("<FocusIn>", lambda e: entry_link.delete(0, END) if entry_link.get() == "输入链接" else None)
        entry_link.bind("<FocusOut>", lambda e: entry_link.insert(0, "输入链接") if entry_link.get() == "" else None)

        def update_text_color(*args):
            if entry_link.get() and entry_link.get() != "输入链接":
                entry_detail.configure(foreground="blue")
            else:
                entry_detail.configure(foreground="black")

        entry_link.bind("<KeyRelease>", update_text_color)

        if detail:
            if isinstance(detail, dict) and 'text' in detail and 'url' in detail:
                entry_detail.insert(0, detail['text'])
                entry_link.delete(0, END)
                entry_link.insert(0, detail['url'])
                entry_detail.configure(foreground="blue")
            else:
                entry_detail.insert(0, detail)

        detail_entries.append((entry_detail, entry_link))

    for detail in task['details']:
        add_detail_entry(detail)

    add_detail_button = ttk.Button(task_window, text="➕ 添加更多详情", bootstyle=PRIMARY, command=add_detail_entry)
    add_detail_button.pack(pady=5)

    def save_edited_task():
        task_name = entry_name.get()
        task_details = []
        for entry_detail, entry_link in detail_entries:
            if entry_detail.get():
                if entry_link.get() and entry_link.get() != "输入链接":
                    task_details.append({'text': entry_detail.get(), 'url': entry_link.get()})
                else:
                    task_details.append(entry_detail.get())
        if task_name and task_details:
            task['name'] = task_name
            task['details'] = task_details
            save_data()
            show_page("task_list")
        else:
            messagebox.showwarning("警告", "请填写任务名和任务详情")

    save_button = ttk.Button(task_window, text="保存更改", bootstyle=SUCCESS, command=save_edited_task)
    save_button.pack(side=LEFT, padx=5, pady=10)

    cancel_button = ttk.Button(task_window, text="取消", bootstyle=SECONDARY, command=lambda: show_page("task_list"))
    cancel_button.pack(side=LEFT, padx=5, pady=10)

def delete_task(task):
    tasks.remove(task)
    save_data()
    show_page("task_list")

def show_assign_rules_page():
    global min_tasks, max_tasks, random_assign, ensure_all_tasks

    for widget in main_frame.winfo_children():
        widget.destroy()

    task_count_frame = ttk.Frame(main_frame)
    task_count_frame.pack(fill=X, padx=10, pady=5)

    ttk.Label(task_count_frame, text="最小任务数:").pack(side=LEFT)
    min_tasks_entry = ttk.Entry(task_count_frame, width=5)
    min_tasks_entry.insert(0, str(min_tasks))
    min_tasks_entry.pack(side=LEFT, padx=(0, 10))

    ttk.Label(task_count_frame, text="最大任务数:").pack(side=LEFT)
    max_tasks_entry = ttk.Entry(task_count_frame, width=5)
    max_tasks_entry.insert(0, str(max_tasks))
    max_tasks_entry.pack(side=LEFT)

    random_var = ttk.BooleanVar(value=random_assign)
    random_check = ttk.Checkbutton(main_frame, text="启用随机分配", variable=random_var)
    random_check.pack(anchor=W, padx=10, pady=5)

    ensure_frame = ttk.Frame(main_frame)
    ensure_frame.pack(fill=X, padx=10, pady=5)
    ttk.Label(ensure_frame, text="在多少次分配中确保所有任务被选择:").pack(side=LEFT)
    ensure_entry = ttk.Entry(ensure_frame, width=5)
    ensure_entry.insert(0, str(ensure_all_tasks))
    ensure_entry.pack(side=LEFT)

    save_button = ttk.Button(main_frame, text="保存设置", command=lambda: save_settings(
        int(min_tasks_entry.get()),
        int(max_tasks_entry.get()),
        random_var.get(),
        int(ensure_entry.get())
    ))
    save_button.pack(pady=10)

    apply_button = ttk.Button(main_frame, text="应用规则", command=apply_rules)
    apply_button.pack(pady=10)

def save_settings(min_t, max_t, random_a, ensure_t):
    global min_tasks, max_tasks, random_assign, ensure_all_tasks
    min_tasks = min_t
    max_tasks = max_t
    random_assign = random_a
    ensure_all_tasks = ensure_t

    save_data()

    save_label = ttk.Label(main_frame, text="设置已保存", foreground="green")
    save_label.pack(pady=5)
    main_frame.after(1000, save_label.destroy)

def apply_rules():
    global accounts, tasks, user_assignments, assignment_count

    if not accounts or not tasks:
        messagebox.showerror("错误", "没有用户或任务可分配")
        return

    user_assignments = {user: [] for user in accounts}

    for user in accounts:
        if user not in assignment_count:
            assignment_count[user] = {}
        for task in tasks:
            if task['name'] not in assignment_count[user]:
                assignment_count[user][task['name']] = 0

    for user in accounts:
        num_tasks = random.randint(min_tasks, max_tasks)
        available_tasks = tasks.copy()

        unassigned_tasks = [task for task in tasks if assignment_count[user][task['name']] < ensure_all_tasks]

        for _ in range(num_tasks):
            if not available_tasks:
                break

            if unassigned_tasks:
                task = random.choice(unassigned_tasks)
                unassigned_tasks.remove(task)
            else:
                task = random.choice(available_tasks)

            user_assignments[user].append(task)
            available_tasks.remove(task)

            assignment_count[user][task['name']] += 1

    save_data()
    show_page("main")

def copy_url(url):
    pyperclip.copy(url)

    success_label = ttk.Label(main_frame, text="链接已复制", foreground="green")
    success_label.pack(pady=5)
    main_frame.after(1000, success_label.destroy)

# 主窗口设置
root = ttk.Window(themename="cosmo")
root.title("任务管理器")
root.geometry("600x400")

# 创建画布和滚动条
canvas = ttk.Canvas(root)
scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
scrollable_frame = ttk.Frame(canvas)

scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

canvas.pack(side=LEFT, fill=BOTH, expand=True)
scrollbar.pack(side=RIGHT, fill=Y)
canvas.configure(yscrollcommand=scrollbar.set)

# 绑定鼠标滚轮事件
canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1 * (event.delta / 120)), "units"))

# 创建顶部按钮框架
top_frame = ttk.Frame(scrollable_frame)
top_frame.pack(side=TOP, fill=X, padx=10, pady=10)

for i in range(3):
    top_frame.columnconfigure(i, weight=1)

# 创建顶部按钮
buttons = [
    ("主页面", "main", SUCCESS),
    ("任务列表", "task_list", INFO),
    ("分配规则", "assign_rules", WARNING)
]

for i, (text, page, style) in enumerate(buttons):
    ttk.Button(top_frame, text=text, bootstyle=style, command=lambda p=page: show_page(p)).grid(row=0, column=i, sticky="ew", padx=5, pady=5)

# 创建主页面框架
main_frame = ttk.Frame(scrollable_frame)
main_frame.pack(fill=BOTH, expand=True)

# 自定义样式
style = ttk.Style()
style.configure("User.TLabel", foreground="black", font=("Arial", 12, "bold"), anchor="center", width=18)
style.configure("TaskName.TLabel", foreground="white", background="#007BFF", font=("Arial", 10, "bold"), width=10, anchor="center")
style.configure("TaskDetail.TLabel", foreground="black", font=("Arial", 9), background="#f0f0f0", relief="solid", borderwidth=1, padding=(2, 1))

# 加载保存的数据并显示主页面
load_data()
show_page("main")

# 运行主窗口
root.mainloop()

# 保存数据
save_data()