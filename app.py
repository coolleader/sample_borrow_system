import streamlit as st
import pandas as pd
from datetime import datetime
import os
import io
from openpyxl.styles import numbers

# 文件路径设置（共享和本地备份）
DATA_FILE = r"\\192.168.5.252\文件中转\魏进磊\仓库清单\sample_inventory.xlsx"
LOCAL_BACKUP_FILE = "sample_inventory_backup.xlsx"

# 初始化样品库
def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_excel(DATA_FILE, dtype=str)
    else:
        df = pd.DataFrame(columns=[
            '型号', '序列号', '料号', '样品快递号', '状态',
            '送出时间', '送出客户', '送出附件',
            '收货时间', '收货快递号', '归还附件'
        ])
    return df.fillna('')

# 保存数据（共享 + 本地，列格式设置为文本）
def save_data(df):
    df = df.astype(str)

    def write_excel(path):
        with pd.ExcelWriter(path, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='样品数据')
            ws = writer.sheets['样品数据']
            for col in ['B', 'C', 'D', 'J']:  # B=序列号, C=料号, D=样品快递号, J=收货快递号
                for cell in ws[col]:
                    cell.number_format = '@'  # 文本格式

    write_excel(DATA_FILE)
    write_excel(LOCAL_BACKUP_FILE)

# 加载数据
df = load_data()
st.title("📦 样品送存管理系统")

menu = ["样品登记", "送出样品", "归还样品", "当前状态", "删除样品"]
choice = st.radio("选择操作", menu)

if choice == "样品登记":
    st.header("📄 样品登记")
    sample_type = st.text_input("输入新样品型号")
    sample_id = st.text_input("输入新样品序列号")
    sample_material = st.text_input("输入新样品料号")
    sample_deliver_id = st.text_input("输入新样品快递号")
    if st.button("登记"):
        if sample_id and sample_id not in df['序列号'].astype(str).values:
            new_entry = pd.DataFrame([{
                '型号': sample_type,
                '序列号': sample_id.strip(),
                '料号': sample_material.strip(),
                '样品快递号': sample_deliver_id.strip(),
                '状态': '在库',
                '送出时间': '',
                '送出客户': '',
                '送出附件': '',
                '收货时间': '',
                '收货快递号': '',
                '归还附件': ''
            }])
            df = pd.concat([df, new_entry], ignore_index=True)
            save_data(df)
            st.success(f"样品 {sample_id} 登记成功")
        else:
            st.warning("序列号为空或已存在")

elif choice == "送出样品":
    st.header("📤 送出样品")
    sid = st.text_input("输入送出样品序列号")
    client = st.text_input("送出客户")
    send_attach = st.text_input("送出附件")
    if st.button("确认送出"):
        if sid in df['序列号'].astype(str).values:
            idx = df[df['序列号'].astype(str) == sid].index[0]
            if df.at[idx, '状态'] == '在库':
                df.at[idx, '状态'] = '送出'
                df.at[idx, '送出时间'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                df.at[idx, '送出客户'] = client.strip()
                df.at[idx, '送出附件'] = send_attach.strip()
                df.at[idx, '收货时间'] = ''
                df.at[idx, '收货快递号'] = ''
                df.at[idx, '归还附件'] = ''
                save_data(df)
                st.success(f"样品 {sid} 送出成功")
            else:
                st.warning("样品已送出")
        else:
            st.error("样品不存在")

elif choice == "归还样品":
    st.header("📥 归还样品")
    sid = st.text_input("输入归还样品序列号")
    deliver_id = st.text_input("收货快递号")
    return_attach = st.text_input("归还附件")
    if st.button("确认归还"):
        if sid in df['序列号'].astype(str).values:
            idx = df[df['序列号'].astype(str) == sid].index[0]
            if df.at[idx, '状态'] == '送出':
                df.at[idx, '状态'] = '在库'
                df.at[idx, '收货时间'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                df.at[idx, '收货快递号'] = deliver_id.strip()
                df.at[idx, '归还附件'] = return_attach.strip()
                save_data(df)
                st.success(f"样品 {sid} 已归还")
            else:
                st.warning("样品未送出")
        else:
            st.error("样品不存在")

elif choice == "当前状态":
    st.header("📊 当前样品状态")
    st.dataframe(df.style.set_properties(**{'white-space': 'pre-wrap'}), use_container_width=True)

    # 导出为 Excel，显式设为文本格式
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='样品数据')
        ws = writer.sheets['样品数据']
        for col in ['B', 'C', 'D', 'J']:  # B=序列号, C=料号, D=样品快递号, J=收货快递号
            for cell in ws[col]:
                cell.number_format = '@'
    excel_buffer.seek(0)

    st.download_button(
        label="📥 下载为 Excel 文件",
        data=excel_buffer,
        file_name="样品状态表.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

elif choice == "删除样品":
    st.header("❌ 删除样品")
    sid = st.text_input("输入要删除的样品序列号")
    confirm = st.checkbox("我确认要删除该样品，并且此操作不可恢复。")
    if st.button("删除"):
        if sid in df['序列号'].astype(str).values:
            if confirm:
                df = df[df['序列号'].astype(str) != sid]
                save_data(df)
                st.success(f"样品 {sid} 已删除")
            else:
                st.warning("请先确认是否删除该样品")
        else:
            st.warning("样品不存在")
