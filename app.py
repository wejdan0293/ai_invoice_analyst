import streamlit as st
import pandas as pd
import requests


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="AI Invoice Analyst",
    page_icon="📊",
    layout="wide"
)


# =========================================================
# APP HEADER
# =========================================================

st.title("📊 AI Invoice Analyst")

st.write(
    "Upload your invoice CSV file, analyze it with AI, "
    "build dashboards, and ask questions about your data."
)


# =========================================================
# N8N WEBHOOKS
# =========================================================

# Webhook 1:
# Upload CSV + analyze dataset

ANALYZE_WEBHOOK_URL = (
    "https://wejdansaleh0293.app.n8n.cloud/workflow/jSXdktz9kiAYhSh9"
)


# Webhook 2:
# Ask questions about analyzed data

ASK_WEBHOOK_URL = (
    "https://wejdansaleh0293.app.n8n.cloud/workflow/jSXdktz9kiAYhSh9"
)


# =========================================================
# SESSION STATE
# =========================================================

if "analysis" not in st.session_state:
    st.session_state["analysis"] = None


if "last_answer" not in st.session_state:
    st.session_state["last_answer"] = None


if "uploaded_filename" not in st.session_state:
    st.session_state["uploaded_filename"] = None


# =========================================================
# FILE UPLOAD
# =========================================================

uploaded_file = st.file_uploader(
    "Upload CSV File",
    type=["csv"],
    key="invoice_csv_upload"
)


# =========================================================
# CSV READING
# =========================================================

if uploaded_file is not None:

    try:

        # Read uploaded CSV
        df = pd.read_csv(uploaded_file)

        st.session_state[
            "uploaded_filename"
        ] = uploaded_file.name


        st.success(
            f"File uploaded successfully: {uploaded_file.name}"
        )


        # -------------------------------------------------
        # DATA PREVIEW
        # -------------------------------------------------

        st.subheader("Data Preview")

        st.dataframe(
            df.head(20),
            use_container_width=True
        )


        # -------------------------------------------------
        # BASIC DATASET METRICS
        # -------------------------------------------------

        metric1, metric2, metric3 = st.columns(3)


        metric1.metric(
            "Rows",
            f"{len(df):,}"
        )


        metric2.metric(
            "Columns",
            len(df.columns)
        )


        metric3.metric(
            "Missing Values",
            int(
                df.isnull()
                .sum()
                .sum()
            )
        )


        # -------------------------------------------------
        # ANALYZE BUTTON
        # -------------------------------------------------

        st.divider()


        analyze_button = st.button(
            "Analyze Data",
            type="primary",
            use_container_width=True
        )


        if analyze_button:

            files = {
                "file": (
                    uploaded_file.name,
                    uploaded_file.getvalue(),
                    "text/csv"
                )
            }


            try:

                with st.spinner(
                    "Analyzing your dataset..."
                ):

                    response = requests.post(
                        ANALYZE_WEBHOOK_URL,
                        files=files,
                        timeout=180
                    )


                st.write(
                    "Status Code:",
                    response.status_code
                )


                if response.status_code == 200:

                    try:

                        result = response.json()


                        st.session_state[
                            "analysis"
                        ] = result


                        # Clear previous Ask Data answer
                        st.session_state[
                            "last_answer"
                        ] = None


                        st.success(
                            "Analysis completed successfully"
                        )


                    except Exception:

                        st.error(
                            "n8n returned a response, "
                            "but the response was not valid JSON."
                        )

                        st.code(
                            response.text
                        )


                else:

                    st.error(
                        "n8n returned an error"
                    )

                    st.code(
                        response.text
                    )


            except requests.exceptions.Timeout:

                st.error(
                    "The analysis request timed out."
                )


            except requests.exceptions.RequestException as e:

                st.error(
                    f"Connection error: {e}"
                )


            except Exception as e:

                st.error(
                    f"Unexpected error: {e}"
                )


    except Exception as e:

        st.error(
            f"Could not read CSV file: {e}"
        )


# =========================================================
# ANALYSIS RESULTS
# =========================================================

result = st.session_state.get(
    "analysis"
)


if result:

    st.divider()


    # =====================================================
    # TABS
    # =====================================================

    (
        tab1,
        tab2,
        tab3,
        tab4,
        tab5
    ) = st.tabs(
        [
            "Overview",
            "Dashboard",
            "AI Insights",
            "Data",
            "Ask Your Data"
        ]
    )


    # =====================================================
    # TAB 1 — OVERVIEW
    # =====================================================

    with tab1:

        st.header(
            "Overview"
        )


        kpis = result.get(
            "kpis",
            {}
        )


        # -------------------------------------------------
        # KPI ROW 1
        # -------------------------------------------------

        col1, col2, col3, col4 = st.columns(4)


        col1.metric(
            "Transactions",
            f"{kpis.get('transactions', 0):,}"
        )


        col2.metric(
            "Total Amount",
            f"{kpis.get('total_amount', 0):,.2f}"
        )


        col3.metric(
            "Average Amount",
            f"{kpis.get('average_amount', 0):,.2f}"
        )


        col4.metric(
            "Customers",
            f"{kpis.get('unique_customers', 0):,}"
        )


        # -------------------------------------------------
        # KPI ROW 2
        # -------------------------------------------------

        col5, col6, col7, col8 = st.columns(4)


        col5.metric(
            "Products",
            f"{kpis.get('unique_products', 0):,}"
        )


        col6.metric(
            "Total Quantity",
            f"{kpis.get('total_quantity', 0):,.0f}"
        )


        max_amount = kpis.get(
            "max_amount"
        )


        min_amount = kpis.get(
            "min_amount"
        )


        col7.metric(
            "Max Transaction",
            (
                f"{max_amount:,.2f}"
                if max_amount is not None
                else "N/A"
            )
        )


        col8.metric(
            "Min Transaction",
            (
                f"{min_amount:,.2f}"
                if min_amount is not None
                else "N/A"
            )
        )


        # -------------------------------------------------
        # DATASET INFORMATION
        # -------------------------------------------------

        st.divider()

        st.subheader(
            "Dataset Information"
        )


        dataset = result.get(
            "dataset",
            {}
        )


        info1, info2, info3 = st.columns(3)


        info1.metric(
            "Dataset Rows",
            f"{dataset.get('rows', 0):,}"
        )


        info2.metric(
            "Dataset Columns",
            dataset.get(
                "columns",
                0
            )
        )


        info3.metric(
            "Missing Values",
            dataset.get(
                "missing_values",
                0
            )
        )


    # =====================================================
    # TAB 2 — DASHBOARD
    # =====================================================

    with tab2:

        st.header(
            "Dashboard"
        )


        charts = result.get(
            "charts",
            {}
        )


        # -------------------------------------------------
        # AMOUNT OVER TIME
        # -------------------------------------------------

        sales_over_time = charts.get(
            "sales_over_time",
            []
        )


        if sales_over_time:

            st.subheader(
                "📈 Amount Over Time"
            )


            sales_df = pd.DataFrame(
                sales_over_time
            )


            if (
                "period" in sales_df.columns
                and
                "total_amount" in sales_df.columns
            ):

                st.line_chart(
                    sales_df,
                    x="period",
                    y="total_amount"
                )


            with st.expander(
                "View Time Series Data"
            ):

                st.dataframe(
                    sales_df,
                    use_container_width=True
                )


        else:

            st.info(
                "No time-based analysis is available."
            )


        # -------------------------------------------------
        # TOP PRODUCTS
        # -------------------------------------------------

        top_products = charts.get(
            "top_products",
            []
        )


        if top_products:

            st.divider()

            st.subheader(
                "🏆 Top Products"
            )


            products_df = pd.DataFrame(
                top_products
            )


            if (
                "product" in products_df.columns
                and
                "total_amount" in products_df.columns
            ):

                st.bar_chart(
                    products_df,
                    x="product",
                    y="total_amount"
                )


            with st.expander(
                "View Product Data"
            ):

                st.dataframe(
                    products_df,
                    use_container_width=True
                )


        # -------------------------------------------------
        # TOP LOCATIONS
        # -------------------------------------------------

        top_locations = charts.get(
            "top_locations",
            []
        )


        if top_locations:

            st.divider()

            st.subheader(
                "🌍 Top Locations"
            )


            locations_df = pd.DataFrame(
                top_locations
            )


            if (
                "location" in locations_df.columns
                and
                "total_amount" in locations_df.columns
            ):

                st.bar_chart(
                    locations_df,
                    x="location",
                    y="total_amount"
                )


            with st.expander(
                "View Location Data"
            ):

                st.dataframe(
                    locations_df,
                    use_container_width=True
                )


        # -------------------------------------------------
        # TOP CUSTOMERS
        # -------------------------------------------------

        top_customers = charts.get(
            "top_customers",
            []
        )


        if top_customers:

            st.divider()

            st.subheader(
                "👥 Top Customers"
            )


            customers_df = pd.DataFrame(
                top_customers
            )


            if (
                "customer" in customers_df.columns
                and
                "total_amount" in customers_df.columns
            ):

                st.bar_chart(
                    customers_df,
                    x="customer",
                    y="total_amount"
                )


            with st.expander(
                "View Customer Data"
            ):

                st.dataframe(
                    customers_df,
                    use_container_width=True
                )


        # -------------------------------------------------
        # STATUS BREAKDOWN
        # -------------------------------------------------

        status_breakdown = charts.get(
            "status_breakdown",
            []
        )


        if status_breakdown:

            st.divider()

            st.subheader(
                "Invoice Status"
            )


            status_df = pd.DataFrame(
                status_breakdown
            )


            if (
                "status" in status_df.columns
                and
                "count" in status_df.columns
            ):

                st.bar_chart(
                    status_df,
                    x="status",
                    y="count"
                )


    # =====================================================
    # TAB 3 — AI INSIGHTS
    # =====================================================

    with tab3:

        st.header(
            "🤖 AI Insights"
        )


        insights = result.get(
            "ai_insights",
            {}
        )


        # -------------------------------------------------
        # EXECUTIVE SUMMARY
        # -------------------------------------------------

        summary = insights.get(
            "summary"
        )


        if summary:

            st.subheader(
                "Executive Summary"
            )

            st.write(
                summary
            )


        # -------------------------------------------------
        # KEY FINDINGS
        # -------------------------------------------------

        findings = insights.get(
            "key_findings",
            []
        )


        if findings:

            st.divider()

            st.subheader(
                "Key Findings"
            )


            for item in findings:

                st.write(
                    f"• {item}"
                )


        # -------------------------------------------------
        # TRENDS
        # -------------------------------------------------

        trends = insights.get(
            "trends",
            []
        )


        if trends:

            st.divider()

            st.subheader(
                "Trends"
            )


            for item in trends:

                st.write(
                    f"• {item}"
                )


        # -------------------------------------------------
        # ANOMALIES
        # -------------------------------------------------

        anomalies = insights.get(
            "anomalies",
            []
        )


        if anomalies:

            st.divider()

            st.subheader(
                "⚠️ Anomalies"
            )


            for item in anomalies:

                st.write(
                    f"• {item}"
                )


        # -------------------------------------------------
        # RECOMMENDATIONS
        # -------------------------------------------------

        recommendations = insights.get(
            "recommendations",
            []
        )


        if recommendations:

            st.divider()

            st.subheader(
                "Recommendations"
            )


            for item in recommendations:

                st.write(
                    f"• {item}"
                )


        # -------------------------------------------------
        # LIMITATIONS
        # -------------------------------------------------

        limitations = insights.get(
            "limitations",
            []
        )


        if limitations:

            st.divider()

            st.subheader(
                "Limitations"
            )


            for item in limitations:

                st.write(
                    f"• {item}"
                )


    # =====================================================
    # TAB 4 — DATA
    # =====================================================

    with tab4:

        st.header(
            "Data Information"
        )


        dataset = result.get(
            "dataset",
            {}
        )


        # -------------------------------------------------
        # FILE INFORMATION
        # -------------------------------------------------

        filename = st.session_state.get(
            "uploaded_filename"
        )


        if filename:

            st.write(
                "**File:**",
                filename
            )


        st.write(
            "**Rows:**",
            dataset.get(
                "rows",
                0
            )
        )


        st.write(
            "**Columns:**",
            dataset.get(
                "columns",
                0
            )
        )


        st.write(
            "**Missing Values:**",
            dataset.get(
                "missing_values",
                0
            )
        )


        # -------------------------------------------------
        # COLUMN NAMES
        # -------------------------------------------------

        column_names = dataset.get(
            "column_names",
            []
        )


        if column_names:

            st.subheader(
                "Columns"
            )

            st.dataframe(
                pd.DataFrame(
                    {
                        "Column": column_names
                    }
                ),
                use_container_width=True
            )


        # -------------------------------------------------
        # DETECTED SCHEMA
        # -------------------------------------------------

        st.subheader(
            "Detected Schema"
        )


        st.json(
            result.get(
                "detected_schema",
                {}
            )
        )


        # -------------------------------------------------
        # FULL JSON
        # -------------------------------------------------

        with st.expander(
            "View Full Analysis JSON"
        ):

            st.json(
                result
            )


    # =====================================================
    # TAB 5 — ASK YOUR DATA
    # =====================================================

    with tab5:

        st.header(
            "💬 Ask Your Data"
        )


        st.write(
            "Ask questions about the analyzed invoice dataset."
        )


        st.caption(
            "Examples: "
            "What are the top 5 products? • "
            "كم إجمالي المبيعات؟ • "
            "من أعلى العملاء؟ • "
            "اعرض المبيعات مع الوقت"
        )


        # -------------------------------------------------
        # QUESTION INPUT
        # -------------------------------------------------

        question = st.text_input(
            "Enter your question",
            placeholder="Example: What are the top 5 products?",
            key="ask_data_question"
        )


        ask_button = st.button(
            "Ask AI",
            type="primary",
            key="ask_data_button"
        )


        # -------------------------------------------------
        # SEND QUESTION TO N8N
        # -------------------------------------------------

        if ask_button:

            if not question.strip():

                st.warning(
                    "Please enter a question."
                )


            else:

                payload = {
                    "question": question,
                    "analysis": result
                }


                try:

                    with st.spinner(
                        "Analyzing your question..."
                    ):

                        ask_response = requests.post(
                            ASK_WEBHOOK_URL,
                            json=payload,
                            timeout=180
                        )


                    st.write(
                        "Status Code:",
                        ask_response.status_code
                    )


                    if ask_response.status_code == 200:

                        try:

                            ask_result = (
                                ask_response.json()
                            )


                            st.session_state[
                                "last_answer"
                            ] = ask_result


                        except Exception:

                            st.error(
                                "The Ask Data workflow did not "
                                "return valid JSON."
                            )

                            st.code(
                                ask_response.text
                            )


                    else:

                        st.error(
                            "n8n returned an error"
                        )

                        st.code(
                            ask_response.text
                        )


                except requests.exceptions.Timeout:

                    st.error(
                        "The question request timed out."
                    )


                except requests.exceptions.RequestException as e:

                    st.error(
                        f"Connection error: {e}"
                    )


                except Exception as e:

                    st.error(
                        f"Unexpected error: {e}"
                    )


        # -------------------------------------------------
        # DISPLAY LAST ANSWER
        # -------------------------------------------------

        ask_result = st.session_state.get(
            "last_answer"
        )


        if ask_result:

            st.divider()

            st.subheader(
                "AI Answer"
            )


            answer = ask_result.get(
                "answer"
            )


            if answer:

                if isinstance(
                    answer,
                    dict
                ):

                    st.json(
                        answer
                    )

                elif isinstance(
                    answer,
                    list
                ):

                    for item in answer:
                        st.write(
                            f"• {item}"
                        )

                else:

                    st.write(
                        answer
                    )


            # ---------------------------------------------
            # DATA USED FOR ANSWER
            # ---------------------------------------------

            answer_data = ask_result.get(
                "data"
            )


            if answer_data:

                with st.expander(
                    "View Analysis Data"
                ):

                    if isinstance(
                        answer_data,
                        list
                    ):

                        answer_df = (
                            pd.DataFrame(
                                answer_data
                            )
                        )


                        st.dataframe(
                            answer_df,
                            use_container_width=True
                        )


                    elif isinstance(
                        answer_data,
                        dict
                    ):

                        st.json(
                            answer_data
                        )


                    else:

                        st.write(
                            answer_data
                        )


            # ---------------------------------------------
            # GENERATED CHART
            # ---------------------------------------------

            chart = ask_result.get(
                "chart"
            )


            if (
                chart
                and
                isinstance(
                    answer_data,
                    list
                )
                and
                len(answer_data) > 0
            ):

                chart_df = pd.DataFrame(
                    answer_data
                )


                chart_type = chart.get(
                    "type"
                )


                x_column = chart.get(
                    "x"
                )


                y_column = chart.get(
                    "y"
                )


                if (
                    x_column
                    in chart_df.columns
                    and
                    y_column
                    in chart_df.columns
                ):

                    st.subheader(
                        "Generated Chart"
                    )


                    if chart_type == "bar":

                        st.bar_chart(
                            chart_df,
                            x=x_column,
                            y=y_column
                        )


                    elif chart_type == "line":

                        st.line_chart(
                            chart_df,
                            x=x_column,
                            y=y_column
                        )


                    elif chart_type == "area":

                        st.area_chart(
                            chart_df,
                            x=x_column,
                            y=y_column
                        )


                    else:

                        st.dataframe(
                            chart_df,
                            use_container_width=True
                        )


            # ---------------------------------------------
            # ROUTER DEBUG
            # ---------------------------------------------

            route = ask_result.get(
                "route"
            )


            if route:

                with st.expander(
                    "View Query Interpretation"
                ):

                    st.json(
                        route
                    )



