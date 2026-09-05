import streamlit as st
import json
import os

st.set_page_config(page_title="لوحة المهام", page_icon="📋", layout="wide")

TASKS_FILE = "tasks.json"

def load_tasks():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_tasks(tasks):
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)

st.title("📋 لوحة المهام")

tasks = load_tasks()

if len(tasks) == 0:
    st.info("لا توجد مهام بعد. سجّل اجتماعاً من الصفحة الرئيسية لاستخراج المهام تلقائياً.")
else:
    col1, col2, col3 = st.columns(3)
    columns = {"جديد": col1, "قيد التنفيذ": col2, "منجز": col3}

    for status in columns:
        with columns[status]:
            st.subheader(status)
            for i, task in enumerate(tasks):
                if task.get("status", "جديد") == status:
                    with st.container(border=True):
                        owner = task.get("owner")
                        if owner:
                            st.write(f"👤 **{owner}**")
                        st.write(task["text"])

                        new_status = st.selectbox(
                            "الحالة",
                            ["جديد", "قيد التنفيذ", "منجز"],
                            index=["جديد", "قيد التنفيذ", "منجز"].index(status),
                            key=f"status_{i}"
                        )
                        if new_status != status:
                            tasks[i]["status"] = new_status
                            save_tasks(tasks)
                            st.rerun()

                        if st.button("🗑️ حذف", key=f"delete_{i}"):
                            tasks.pop(i)
                            save_tasks(tasks)
                            st.rerun()

    if st.button("🗑️ حذف كل المهام"):
        save_tasks([])
        st.rerun()