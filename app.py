import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# 🔐 Google Sheets 认证
SCOPE = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=SCOPE
)
gc = gspread.authorize(creds)

# 📄 打开 Google Sheet
SHEET_ID = "14NUgJ8kk9DJtWaRKtIM_bQ5VXTJkZDibG28z_v_AwbU"
SHEET_NAME = "sample_inventory"
worksheet = gc.open_by_key(SHEET_ID).worksheet(SHEET_NAME)


# ✅ 读取数据
def load_data():
    try:
        records = worksheet.get_all_records()
        return pd.DataFrame(records)
    except:
        return pd.DataFrame(columns=[
            '型号', '序列号', '料号', '样品快递号', '状态',
            '送出时间', '送出客户', '送出附件',
            '收货时间', '收货快递号', '归还附件'
        ])

# ✅ 保存数据（清空整个 Sheet 再写入）
def save_data(df):
    worksheet.clear()
    worksheet.update([df.columns.values.tolist()] + df.values.tolist())

# ========= Streamlit 界面 ==========
df = load_data()
st.title("📦 样品送存管理系统")

menu = ["样品登记", "送出样品", "归还样品", "当前状态", "删除样品"]
choice = st.radio("选择操作", menu)

if choice == "样品登记":
    st.header("📄 样品登记")
    sample_type = st.text_input("型号")
    sample_id = st.text_input("序列号")
    sample_material = st.text_input("料号")
    sample_deliver_id = st.text_input("样品快递号")
    if st.button("登记"):
        if sample_id and sample_id not in df['序列号'].astype(str).values:
            new_row = pd.DataFrame([{
                '型号': sample_type,
                '序列号': sample_id,
                '料号': sample_material,
                '样品快递号': sample_deliver_id,
                '状态': '在库',
                '送出时间': '', '送出客户': '', '送出附件': '',
                '收货时间': '', '收货快递号': '', '归还附件': ''
            }])
            df = pd.concat([df, new_row], ignore_index=True)
            save_data(df)
            st.success("样品已登记")
        else:
            st.warning("序列号重复或为空")

elif choice == "送出样品":
    st.header("📤 送出样品")
    sid = st.text_input("序列号")
    client = st.text_input("送出客户")
    send_attach = st.text_input("送出附件")
    if st.button("确认送出"):
        if sid in df['序列号'].astype(str).values:
            idx = df[df['序列号'].astype(str) == sid].index[0]
            if df.at[idx, '状态'] == '在库':
                df.at[idx, '状态'] = '送出'
                df.at[idx, '送出时间'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                df.at[idx, '送出客户'] = client
                df.at[idx, '送出附件'] = send_attach
                df.at[idx, '收货时间'] = ''
                df.at[idx, '收货快递号'] = ''
                df.at[idx, '归还附件'] = ''
                save_data(df)
                st.success("样品送出成功")
            else:
                st.warning("该样品不是在库状态")
        else:
            st.warning("样品不存在")

elif choice == "归还样品":
    st.header("📥 归还样品")
    sid = st.text_input("序列号")
    deliver_id = st.text_input("收货快递号")
    return_attach = st.text_input("归还附件")
    if st.button("确认归还"):
        if sid in df['序列号'].astype(str).values:
            idx = df[df['序列号'].astype(str) == sid].index[0]
            if df.at[idx, '状态'] == '送出':
                df.at[idx, '状态'] = '在库'
                df.at[idx, '收货时间'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                df.at[idx, '收货快递号'] = deliver_id
                df.at[idx, '归还附件'] = return_attach
                save_data(df)
                st.success("样品已归还")
            else:
                st.warning("该样品未被送出")
        else:
            st.warning("样品不存在")

elif choice == "当前状态":
    st.header("📊 当前样品状态")
    st.dataframe(df, use_container_width=True)
    csv = df.to_csv(index=False, encoding='utf-8-sig')
    st.download_button("📥 下载样品表 (CSV)", data=csv, file_name="样品表.csv", mime="text/csv")

elif choice == "删除样品":
    st.header("❌ 删除样品")
    sid = st.text_input("要删除的序列号")
    confirm = st.checkbox("确认删除该样品")
    if st.button("删除"):
        if sid in df['序列号'].astype(str).values:
            if confirm:
                df = df[df['序列号'].astype(str) != sid]
                save_data(df)
                st.success("样品已删除")
            else:
                st.warning("请勾选确认删除")
        else:
            st.warning("样品不存在")
