import streamlit as st
import pandas as pd
from tortoise import Tortoise
from model import TestSession, CaseModel
import plotly.express as px
import plotly.figure_factory as ff
import asyncio
import time
from datetime import datetime, timezone


async def init_db():
    await Tortoise.init(
        db_url="sqlite://cases.db?mode=rwc", modules={"models": ["model"]}
    )
    await Tortoise.generate_schemas()


async def get_session_names():
    return await TestSession.all().values_list("session_name", flat=True)


async def get_cases_by_session(session_name):
    session = await TestSession.get(session_name=session_name)
    return await CaseModel.filter(session=session).all()


def create_gantt_chart(df):
    now = datetime.now(timezone.utc)

    # 将 start_time 和 end_time 转换为 UTC 时间
    df["start_time"] = pd.to_datetime(df["start_time"], utc=True)
    df["end_time"] = pd.to_datetime(df["end_time"], utc=True)

    # 对于 end_time 为 NaT 的行，填充为当前时间
    df["end_time"] = df["end_time"].fillna(now)

    df = df.sort_values("end_time", ascending=False)

    gantt_df = pd.DataFrame(
        {
            "Task": df["id"].astype(str),
            "Start": df["start_time"],
            "Finish": df["end_time"],
            "Status": df["status"],
        }
    )

    # 计算适当的高度
    num_cases = len(gantt_df)
    height = max(600, num_cases * 30)  # 每个 case 至少 30px 高，最小高度为 600px

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
        title="Case 运行时间线",
    )

    fig.update_layout(
        xaxis_title="时间", yaxis_title="Case ID", height=height, autosize=True
    )

    return fig


async def async_main():
    await init_db()
    session_names = await get_session_names()
    selected_session = st.selectbox("选择会话", session_names)

    placeholder = st.empty()

    while True:
        with placeholder.container():
            await init_db()
            if selected_session:
                cases = await get_cases_by_session(selected_session)
                df = pd.DataFrame([case.__dict__ for case in cases])

                st.subheader(f"{selected_session} 的测试用例统计")

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

                # 显示详细数据表格
                st.subheader("测试用例详细信息")
                st.dataframe(df)

                # 甘特图（可展开）
                with st.expander("点击展开查看 Case 运行时间线"):
                    if not df.empty:
                        gantt_fig = create_gantt_chart(df)
                        st.plotly_chart(gantt_fig, use_container_width=True)
                    else:
                        st.write("没有可用的数据来创建甘特图。")

            await Tortoise.close_connections()
        # break
        time.sleep(50)
        st.rerun()


def main():
    loop = asyncio.new_event_loop()
    asyncio.run(async_main())
    loop.run_until_complete(async_main())


if __name__ == "__main__":
    st.title("测试会话数据可视化")
    main()
