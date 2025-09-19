import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Campaign Analysis", layout="wide")

# --------------------------
# Setup
# --------------------------
DATA_DIR = "campaign_data"  # folder containing all your campaign CSVs

error_lookup = {
    0: "No Error",
    12300: "Invalid Content-Type",
    21211: "Invalid 'To' Phone Number",
    21408: "Message is blocked or permissions are disabled for the region indicated by the 'To' number",
    21610: "Attempt to send to unsubscribed recipient",
    21614: "'To' number is not a valid mobile number",
    30002: "Account suspended",
    30003: "Unreachable destination handset.The destination handset you are trying to reach is switched off or otherwise unavailable.",
    30005: "Unknown destination handset",
    30006: "Message Delivery - Landline or unreachable carrier. The destination number is unable to receive this message",
    30008: "Unknown Error",
    30011: "MMS not supported by the receiving phone number in this region",
    30023: "US A2P 10DLC - Daily Message Cap Reached. You have sent the maximum allowable daily messages for your Brand to the carrier",
}

# --------------------------
# Campaign selection
# --------------------------
campaign_files = [f for f in os.listdir(DATA_DIR) if f.endswith(".csv")]
campaign_names = [os.path.splitext(f)[0] for f in campaign_files]

st.title("📊 Campaign Analysis")
selected_campaign = st.selectbox("Choose a campaign", campaign_names)

if selected_campaign:
    file_path = os.path.join(DATA_DIR, selected_campaign + ".csv")
    df = pd.read_csv(file_path)

    # Basic filtered DataFrames
    outbound_df = df[df["Direction"] == "outbound-api"]
    inbound_df = df[df["Direction"] == "inbound"]

    st.header(f"📌 {selected_campaign} - Analysis")

    st.subheader("Dataset Preview")
    st.dataframe(df[df["Status"] == "delivered"].tail())
    # -------------------------------------------------------------------
    # 1. Overall Analysis
    # -------------------------------------------------------------------
    st.subheader("1️⃣ Overall Analysis")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Messages", f"{df.shape[0]:,}")
    col2.metric("Unique Statuses", df["Status"].nunique())
    col3.metric("Unique ErrorCodes", df["ErrorCode"].nunique())

    col4, col5, col6 = st.columns(3)
    col4.write("Type of Messages")
    col4.dataframe(df["Direction"].value_counts().to_frame("Count"), width=200)

    col5.write("Status of Messages")
    col5.dataframe(df["Status"].value_counts().to_frame("Count"), width=200)

    error_df = df["ErrorCode"].value_counts().to_frame("Count")
    for i in error_df.index:
        if i in error_lookup.keys():
            error_df.loc[i, "Description"] = error_lookup[i]

    col6.write("Error Codes Received")
    col6.dataframe(error_df)

    # -------------------------------------------------------------------
    # 2. Outbound API Analysis
    # -------------------------------------------------------------------
    st.divider()
    st.subheader("2️⃣ Outbound API Analysis")

    col101, col102, col103 = st.columns(3)
    col101.metric("Total Outbound", f"{outbound_df.shape[0]:,}")
    col102.metric("**Unique Outbound Statuses**", outbound_df["Status"].nunique())
    col103.metric("Unique ErrorCodes", outbound_df["ErrorCode"].nunique())

    col7, col8, col9 = st.columns(3)
    col8.write("**Outbound Status Counts**")
    col8.dataframe(outbound_df["Status"].value_counts().to_frame("Count"))

    out_error_df = outbound_df["ErrorCode"].value_counts().to_frame("Count")
    for i in out_error_df.index:
        if i in error_lookup.keys():
            out_error_df.loc[i, "Description"] = error_lookup[i]
    col9.write("**Outbound ErrorCode Counts**")
    col9.dataframe(out_error_df)

    # -------------------------------------------------------------------
    # 3. Inbound & Outbound Reply Analysis
    # -------------------------------------------------------------------
    # st.subheader("3️⃣ Inbound & Outbound Reply Analysis")

    # st.write("**Inbound Messages**")
    # st.dataframe(inbound_df["Status"].value_counts().to_frame("Count"))

    # st.write("**Outbound Messages**")
    # st.dataframe(outbound_df["Status"].value_counts().to_frame("Count"))

    # -------------------------------------------------------------------
    # 4. Delivery Success Rate
    # -------------------------------------------------------------------
    # st.subheader("4️⃣ Delivery Success Rate")

    delivered = outbound_df[outbound_df["Status"] == "delivered"]
    delivered_count = delivered.shape[0]
    total_outbound = outbound_df.shape[0]
    delivery_success_rate = (
        (delivered_count / total_outbound * 100) if total_outbound else 0
    )

    col7.metric("Delivery Success Rate", f"{delivery_success_rate:.2f}%")
    col7.metric("No. of People to whom messages are delivered", delivered_count)

    # -------------------------------------------------------------------
    # 5. Stop Rate
    # -------------------------------------------------------------------
    # st.subheader("5️⃣ Stop Rate")

    # Assuming STOP messages are in inbound messages with 'STOP' in text column

    stop_msgs = inbound_df[
        inbound_df["Body"].str.contains("stop|unsubscribe", case=False)
    ][["From", "To", "Body"]]
    stop_count = stop_msgs.shape[0]
    stop_rate = (stop_count / total_outbound) * 100

    col7.metric("Stop Rate", f"{stop_rate:.2f}%")
    col7.metric("No. Of People who Unsubscribed/Stop", stop_count)

    st.write("**List of Numbers who Unsubscribed/Stop**")
    st.dataframe(stop_msgs)
    # -------------------------------------------------------------------
    # 6. Campaign Expense
    # -------------------------------------------------------------------
    # st.subheader("6️⃣ Campaign Expense")
    st.divider()
    st.subheader("3️⃣ Campaign Expense")
    st.info("Carrier fee is not levied on Failed Messages")
    col10, col11, col12, col13 = st.columns(4)

    expense_exluding_failed_df = df[
        df["Status"].isin(["received", "undelivered", "delivered", "sent"])
    ][["NumSegments", "Price"]].agg(["count", "sum", "mean"])
    cost_excluding_failed = round(float(-expense_exluding_failed_df["Price"][1]), 2)
    col10.metric("Message Cost (Excl. Failed Msgs)", f"${cost_excluding_failed}")
    col10.write("Stats for Messages (Excl. Failed Messages)")
    col10.dataframe(expense_exluding_failed_df)
    avg_cost_per_segment = round(
        -(
            expense_exluding_failed_df["Price"][1]
            / expense_exluding_failed_df["NumSegments"][1]
        ),
        4,
    )
    avg_cost_per_msg = round(
        -(
            expense_exluding_failed_df["Price"][1]
            / expense_exluding_failed_df["NumSegments"][0]
        ),
        4,
    )

    segments_exlcuding_failed = float(expense_exluding_failed_df["NumSegments"][1])
    carrier_cost_per_segment = 0.0033
    sid = df[df["Direction"] == "outbound-api"]["Sid"]
    si = sid.iloc[0]
    # si
    carrier_cost = (
        round(segments_exlcuding_failed * 3 * carrier_cost_per_segment, 2)
        if si.startswith("MM")
        else round(segments_exlcuding_failed * carrier_cost_per_segment, 2)
    )
    # carrier_cost
    col11.metric("Carrier Cost", f"${carrier_cost}")
    col11.metric("Average Cost Per Message", avg_cost_per_msg)
    col11.metric("Average Cost Per Segment", avg_cost_per_segment)

    failed = df[df["Status"].isin(["failed"])][["Price"]].agg(["count", "sum", "mean"])
    # failed
    failed_cost = round(float(-failed["Price"][1]), 2)
    col12.metric("Failed Message Cost", f"${failed_cost}")

    campaign_cost = round(cost_excluding_failed + carrier_cost + failed_cost, 2)
    col13.metric("Total Campaign Cost (Approx.)", f"${campaign_cost}")

    st.badge("Other Numbers")
    col14, col15, col16, col17 = st.columns(4)
    outbound_api_expense_df = df[df["Direction"].isin(["outbound-api"])][
        ["NumSegments", "Price"]
    ].agg(["count", "sum", "mean"])
    outbound_api_cost = round(float(-outbound_api_expense_df["Price"][1]), 2)
    col14.metric("Outbound API Cost", f"${outbound_api_cost}")

    outbound_reply_expense_df = df[df["Direction"].isin(["outbound-reply"])][
        ["NumSegments", "Price"]
    ].agg(["count", "sum", "mean"])
    # outbound_reply_expense_df
    outbound_reply_cost = round(float(-outbound_reply_expense_df["Price"][1]), 2)
    col15.metric("Outbound Reply Cost", f"${outbound_reply_cost}")

    inbound_expense_df = df[df["Direction"].isin(["inbound"])][
        ["NumSegments", "Price"]
    ].agg(["count", "sum", "mean"])
    # inbound_expense_df
    inbound_cost = round(float(-inbound_expense_df["Price"][1]), 2)
    col16.metric("Inbound Cost", f"${inbound_cost}")

    total_campaign_cost = round(
        outbound_api_cost + outbound_reply_cost + inbound_cost, 2
    )
    col17.metric("Total Direction Wise Cost", f"${total_campaign_cost}")

# MMb7dcf2b23e7b393b9eb790a1258715a9
# SM76cb2526e309efc2047edb20c1361ce4
