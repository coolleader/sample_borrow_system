import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 文件保存路径
DATA_FILE = 'sample_inventory.csv'

# 初始化样品库
def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
    else:
        df = pd.DataFrame(columns=['SampleID', 'Status', 'BorrowTime', 'ReturnTime', 'Client',
                                   'SendAttachment', 'ReturnAttachment'])
    return df

# 保存数据
def save_data(df):
    df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')

# 加载数据
df = load_data()
st.title("📦 样品送存管理系统")

menu = ["样品登记", "送出样品", "归还样品", "当前状态", "删除样品"]
# choice = st.sidebar.selectbox("选择操作", menu)
# choice = st.sidebar.radio("选择操作", menu)

if choice == "样品登记":
    st.header("📄 样品登记")
    sample_id = st.text_input("输入新样品编号")
    if st.button("登记"):
        if sample_id and sample_id not in df['SampleID'].astype(str).values:
            new_entry = pd.DataFrame([{
                'SampleID': sample_id,
                'Status': '在库',
                'BorrowTime': '',
                'ReturnTime': '',
                'Client': '',
                'SendAttachment': '',
                'ReturnAttachment': ''
            }])
            df = pd.concat([df, new_entry], ignore_index=True)
            save_data(df)
            st.success(f"样品 {sample_id} 登记成功")
        else:
            st.warning("编号为空或已存在")

elif choice == "送出样品":
    st.header("📤 送出样品")
    sid = st.text_input("输入送出样品编号")
    client = st.text_input("送样客户")
    send_attach = st.text_input("送出附件")
    if st.button(" 确认送出"):
        if sid in df['SampleID'].astype(str).values:
            idx = df[df['SampleID'].astype(str) == sid].index[0]
            if df.at[idx, 'Status'] == '在库':
                df.at[idx, 'Status'] = '送出'
                df.at[idx, 'BorrowTime'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                df.at[idx, 'Client'] = client
                df.at[idx, 'SendAttachment'] = send_attach
                df.at[idx, 'ReturnTime'] = ''
                df.at[idx, 'ReturnAttachment'] = ''
                save_data(df)
                st.success(f"样品 {sid} 送出成功")
            else:
                st.warning("样品已送出")
        else:
            st.error("样品不存在")

elif choice == "归还样品":
    st.header("📥 归还样品")
    sid = st.text_input(" 输入归还样品编号")
    return_attach = st.text_input("归还附件")
    if st.button("确认归还"):
        if sid in df['SampleID'].astype(str).values:
            idx = df[df['SampleID'].astype(str) == sid].index[0]
            if df.at[idx, 'Status'] == '送出':
                df.at[idx, 'Status'] = '在库'
                df.at[idx, 'ReturnTime'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                df.at[idx, 'ReturnAttachment'] = return_attach
                save_data(df)
                st.success(f"样品 {sid} 已归还")
            else:
                st.warning("样品未送出")
        else:
            st.error("样品不存在")

elif choice == "当前状态":
    st.header("📊 当前样品状态")
    st.dataframe(df, use_container_width=True)


elif choice == "删除样品":
    st.header("❌ 删除样品")
    sid = st.text_input("输入要删除的样品编号")
    if st.button(" 删除"):
        if sid in df['SampleID'].astype(str).values:
            df = df[df['SampleID'].astype(str) != sid]
            save_data(df)
            st.success(f"样品 {sid} 已删除")
        else:
            st.warning("样品不存在")
