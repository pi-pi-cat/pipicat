import streamlit as st
import pandas as pd
from tortoise import Tortoise
from model import TestSession, CaseModel
import plotly.express as px
import plotly.figure_factory as ff
import asyncio
from datetime import datetime, timezone


# 初始化数据库连接
@st.cache_resource
def init_db():
    async def _init():
        await Tortoise.init(
            db_url="sqlite://cases.db?mode=rwc", modules={"models": ["model"]}
        )
        await Tortoise.generate_schemas()

    asyncio.run(_init())
    return True


# 获取会话名称
@st.cache_data(ttl=60)  # 缓存1分钟
def get_session_names():
    async def _get_names():
        return await TestSession.all().values_list("session_name", flat=True)

    return asyncio.run(_get_names())


# 获取特定会话的数据
@st.cache_data(ttl=60)  # 缓存1分钟
def get_session_data(_session_name):
    async def _get_data():
        session = await TestSession.get(session_name=_session_name)
        cases = await CaseModel.filter(session=session).all()
        df = pd.DataFrame([case.__dict__ for case in cases])
        for col in ["start_time", "end_time"]:
            df[col] = pd.to_datetime(df[col], utc=True)
        return df

    return asyncio.run(_get_data())


def create_gantt_chart(df, page=1, page_size=50):
    now = datetime.now(timezone.utc)

    df["end_time"] = df["end_time"].fillna(now)
    df = df.sort_values("end_time", ascending=True)

    # 分页
    start = (page - 1) * page_size
    end = start + page_size
    df_page = df.iloc[start:end]

    gantt_df = pd.DataFrame(
        {
            "Task": df_page["id"].astype(str),
            "Start": df_page["start_time"],
            "Finish": df_page["end_time"],
            "Status": df_page["status"],
        }
    )

    height = len(gantt_df) * 30  # 每个 case 30px 高

    fig = ff.create_gantt(
        gantt_df,
        colors={
            "RUNNING": "rgb(255, 165, 0)",
            "Success": "rgb(34, 139, 34)",
            "Failure": "rgb(255, 0, 0)",
        },
        index_col="Status",
        show_colorbar=True,
        group_tasks=True,
        showgrid_x=True,
        showgrid_y=True,
        title=f"Case 运行时间线 (第 {page} 页)",
    )

    fig.update_layout(
        xaxis_title="时间 (UTC)", yaxis_title="Case ID", height=height, autosize=True
    )

    fig.update_yaxes(autorange="reversed")

    return fig


def main():
    st.title("测试会话数据可视化")

    # 确保数据库已初始化
    if "db_initialized" not in st.session_state:
        st.session_state.db_initialized = init_db()

    session_names = get_session_names()
    selected_session = st.selectbox("选择会话", session_names)

    if selected_session:
        if (
            "df" not in st.session_state
            or st.session_state.current_session != selected_session
        ):
            st.session_state.df = get_session_data(selected_session)
            st.session_state.current_session = selected_session

        df = st.session_state.df

        st.subheader(f"{selected_session} 的测试用例统计")

        # latest_records = df.sort_values('start_time').groupby('case_number').last().reset_index()

        running = df[df["status"] == "RUNNING"].shape[0]
        completed = df[df["status"].isin(["Success", "Failure"])].shape[0]
        success = df[df["status"] == "Success"].shape[0]
        failed = df[df["status"] == "Failure"].shape[0]

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("运行中", running)
        col2.metric("已完成", completed)
        col3.metric("成功", success)
        col4.metric("失败", failed)

        # 饼图
        st.subheader("测试用例状态分布")
        status_counts = df["status"].value_counts().reset_index()
        status_counts.columns = ["status", "count"]
        pie_fig = px.pie(
            status_counts,
            values="count",
            names="status",
            title="测试用例状态分布",
        )
        st.plotly_chart(pie_fig)

        # 甘特图（可展开）
        with st.expander("点击展开查看 Case 运行时间线"):
            if not df.empty:
                total_pages = (len(df) - 1) // 50 + 1
                page = st.slider("选择页面", 1, total_pages, 1)

                gantt_fig = create_gantt_chart(df, page)
                st.plotly_chart(gantt_fig, use_container_width=True)

                st.write(
                    f"显示 {len(df)} 个 cases 中的第 {(page-1)*50+1} 到 {min(page*50, len(df))} 个"
                )
            else:
                st.write("没有可用的数据来创建甘特图。")


if __name__ == "__main__":
    main()
