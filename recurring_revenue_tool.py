import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from dateutil.relativedelta import relativedelta

def generate_monthly_revenue(start_date, end_date, amount, initial_amount=None, projected_close=1.0):
    start_date, end_date = pd.to_datetime(start_date), pd.to_datetime(end_date)
    months = []
    if initial_amount: months.append((start_date.strftime('%Y-%m'), initial_amount * projected_close))
    amount *= projected_close
    current_date = start_date + relativedelta(months=1) if initial_amount else start_date
    while current_date <= end_date:
        months.append((current_date.strftime('%Y-%m'), amount))
        current_date += relativedelta(months=1)
    return months

def calculate_monthly_totals(revenue_data, loss_data):
    all_data = revenue_data + loss_data
    df = pd.DataFrame(all_data, columns=['Month', 'Revenue'])
    df['Loss'] = df['Revenue'].apply(lambda x: x if x < 0 else 0)
    df['Revenue'] = df['Revenue'].apply(lambda x: x if x > 0 else 0)
    return df.groupby('Month').sum().reset_index()

def main():
    st.title("Recurring Revenue Analytics Tool")

    for state in ['revenue_data', 'loss_data', 'saved_details']:
        if state not in st.session_state: st.session_state[state] = []

    uploaded_file = st.file_uploader("Upload CSV File", type="csv")
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            required = ['Deal Stage', 'Deal Name', 'Close Date', 'Amount']
            if missing := [col for col in required if col not in df.columns]:
                st.error(f"Missing columns: {', '.join(missing)}"); return
        except Exception as e:
            st.error(f"Error reading file: {e}"); return

        qualified = ['Proposal/Contract', 'Qualified Lead', 'Closed won']
        deals_df = df[df['Deal Stage'].isin(qualified)]
        deal_name = st.selectbox("Select a Deal:", options=deals_df['Deal Name'])
        deal = deals_df[deals_df['Deal Name'] == deal_name].iloc[0]
        st.write("### Deal Details", deal)

        recurring_amt = st.number_input("Recurring Revenue Amount ($):", min_value=0.0, step=0.01)
        projected_close = st.slider("Projected % Close:", min_value=0, max_value=100, value=100) / 100.0
        inactive_date = st.text_input("Inactive Date (MM/DD/YYYY):")
        inactive_reason = st.selectbox("Inactive Reason:", ["", "Churned", "Renewal", "Upgrade", "Downgrade"])

        if st.button("Save Recurring Revenue Details"):
            if recurring_amt and inactive_date:
                start, end = pd.to_datetime(deal['Close Date']), pd.to_datetime(inactive_date)
                if start <= end:
                    initial_amt = deal['Amount'] if not pd.isna(deal['Amount']) else None

                    # Replace existing deal data if it exists
                    st.session_state.saved_details = [d for d in st.session_state.saved_details if d['Deal Name'] != deal_name]
                    st.session_state.revenue_data = [d for d in st.session_state.revenue_data if d[0] != deal_name]
                    st.session_state.loss_data = [d for d in st.session_state.loss_data if d[0] != deal_name]

                    revenue_data = generate_monthly_revenue(start, end, recurring_amt, initial_amt, projected_close)
                    st.session_state.revenue_data.extend(revenue_data)
                    if inactive_reason == "Churned":
                        st.session_state.loss_data.append((end.strftime('%Y-%m'), -recurring_amt * projected_close))

                    st.session_state.saved_details.append({
                        'Deal Name': deal_name, 'Recurring Amount': recurring_amt, 'Projected %': projected_close * 100,
                        'Inactive Date': inactive_date, 'Inactive Reason': inactive_reason
                    })
                    st.success(f"Details for '{deal_name}' saved.")
                else: st.error("Inactive Date must follow Close Date.")
            else: st.error("Provide Recurring Revenue Amount and Inactive Date.")

        if st.button("Delete Recurring Revenue for Closed Lost/Stalled Deals"):
            closed_stages = ['Closed lost', 'Closed stalled']
            closed_deals = df[df['Deal Stage'].isin(closed_stages)]['Deal Name'].tolist()
            st.session_state.saved_details = [d for d in st.session_state.saved_details if d['Deal Name'] not in closed_deals]
            st.session_state.revenue_data = [d for d in st.session_state.revenue_data if d[0] not in closed_deals]
            st.session_state.loss_data = [d for d in st.session_state.loss_data if d[0] not in closed_deals]
            st.success("Removed recurring revenue for closed lost/stalled deals.")

        totals_df = calculate_monthly_totals(st.session_state.revenue_data, st.session_state.loss_data)
        st.subheader("Recurring Revenue and Losses Over Time")
        fig = go.Figure()
        fig.add_trace(go.Bar(x=totals_df['Month'], y=totals_df['Revenue'], name='Revenue', marker_color='blue'))
        fig.add_trace(go.Bar(x=totals_df['Month'], y=totals_df['Loss'], name='Loss', marker_color='red'))
        fig.update_layout(barmode='group', title='Revenue and Losses Over Time', xaxis_title='Month', yaxis_title='Amount ($)')
        st.plotly_chart(fig)

        st.subheader("Revenue Summary Table")
        st.write(totals_df)

        st.subheader("Saved Recurring Revenue Details")
        details_df = pd.DataFrame(st.session_state.saved_details)
        if not details_df.empty:
            st.write(details_df)
            delete_index = st.number_input("Row to delete:", min_value=0, max_value=len(details_df)-1, step=1)
            if st.button("Delete Selected Row"):
                st.session_state.saved_details.pop(delete_index)
                st.session_state.revenue_data, st.session_state.loss_data = [], []
                for detail in st.session_state.saved_details:
                    deal_row = deals_df[deals_df['Deal Name'] == detail['Deal Name']].iloc[0]
                    start = pd.to_datetime(deal_row['Close Date'])
                    end = pd.to_datetime(detail['Inactive Date'])
                    initial_amt = deal_row['Amount'] if not pd.isna(deal_row['Amount']) else None
                    revenue_data = generate_monthly_revenue(start, end, detail['Recurring Amount'], initial_amt, detail['Projected %'] / 100.0)
                    st.session_state.revenue_data.extend(revenue_data)
                    if detail['Inactive Reason'] == "Churned":
                        st.session_state.loss_data.append((end.strftime('%Y-%m'), -detail['Recurring Amount'] * detail['Projected %'] / 100.0))
                st.experimental_set_query_params()

if __name__ == "__main__": main()
