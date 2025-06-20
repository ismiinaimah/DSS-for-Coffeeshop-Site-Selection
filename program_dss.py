import streamlit as st
import numpy as np
import pandas as pd
from rumus import calculate_ahp_weights, topsis, profile_matching 
import matplotlib.pyplot as plt
from io import BytesIO
import base64

# Fungsi untuk encode gambar lokal sebagai base64
def get_base64_of_bin_file(bin_file_path):
    with open(bin_file_path, 'rb') as f:
        return base64.b64encode(f.read()).decode()

# Ganti dengan nama file gambar kamu
image_path = "kopi.jpg"
overlay_image_path = "biji_kopi.jpg"
sidebar_base64 = get_base64_of_bin_file(overlay_image_path)
background_base64 = get_base64_of_bin_file(image_path)
# background_base64 = sidebar_base64  # Use the same image for background, or load a different one if desired

st.set_page_config(page_title="📍 Decision Support System for Coffee Shop Site Selection in D.I. Yogyakarta", layout="wide")

# Sisipkan CSS dengan gambar sebagai latar belakang halaman utama
st.markdown(f"""
    <style>
    /* Set background image for main app */
    .stApp {{
        background-image: url("data:image/jpg;base64,{background_base64}");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
        background-position: center;
        color: #ECD6C2;
    }}
    
    /* Header */
    header[data-testid="stHeader"] {{
        background-color: transparent;
        color: #1C120C;
    }}

    /* Sidebar */
    section[data-testid="stSidebar"] > div:first-child {{
        background-color: rgba(69, 41, 1, 0.9); /* semitransparan */
        background-image: url("data:image/png;base64,{sidebar_base64}");
        background-repeat: repeat; /* atau no-repeat */
        background-position: center;
        background-size: 800px 1200px; /* Sesuaikan ukuran biji kopi */
        color: #7B5C43;
    }}

    /* Sidebar text color + bold */
    section[data-testid="stSidebar"] * {{
        color: #3D2614 !important;  /* Coklat pekat */
        font-weight: bold !important;
    }}

    /* Input fields and widgets */
    .stTextInput, .stNumberInput, .stSelectbox, .stSlider, .stRadio {{
        color: #ECD6C2;
    }}

    /* Dataframe background */
    .stDataFrame {{ background-color: rgba(69, 41, 1, 0.8); }}

    /* Buttons */
    button[kind="primary"] {{
        background-color: #4c2c04;
        color: white;
        border-radius: 5px;
    }}

    /* Titles and Headers */
    h1, h2, h3, h4, h5, h6 {{
        color: #ECD6C2;
    }}

    .stMarkdown, .stSubheader, .stHeader, .stText, .stExpander {{
        color: #ECD6C2 !important;
    }}
    
    .block-container {{
        padding: 1rem;
        background-color: rgba(0, 0, 0, 0.4); /* tambahkan lapisan semi-transparan agar teks tetap terbaca */
        border-radius: 10px;
    }}
    </style>
""", unsafe_allow_html=True)

# Set the title and subheader for the app
st.title("📍 Decision Support System for Coffee Shop Site Selection in D.I. Yogyakarta")
st.subheader("🔎 AHP-Weighted Decision Making Using TOPSIS and Profile Matching")
st.markdown("---")

# Sidebar Navigation
tabs = ["☕ Weighting", "☕ AHP + TOPSIS", "☕ AHP + Profile Matching"]
selected_tab = st.sidebar.radio("Select Tab", tabs)

# Tab 1: Weighting (AHP)
if selected_tab == "☕ Weighting":
    st.header("☕ Weighting Criteria with AHP")
    st.subheader("1️⃣ Input Criteria and Alternatives")

    # Input for criteria and alternatives
    num_criteria = st.number_input("Number of Criteria", min_value=2, value=3, step=1, key="num_criteria")
    num_alternatives = st.number_input("Number of Alternatives", min_value=2, value=3, step=1, key="num_alternatives")

    criteria = [st.text_input(f"Criterion Name {i+1}", key=f"crit_{i}") for i in range(num_criteria)]
    alternatives = [st.text_input(f"Alternative Name {i+1}", key=f"alt_{i}") for i in range(num_alternatives)]
    
    # Ensure criteria names are unique and non-empty
    if len(set([c.strip() for c in criteria if c.strip() != ""])) != len(criteria) or any(c.strip() == "" for c in criteria):
        st.error("All criteria names must be unique and non-empty.")
    
    if all(criteria) and all(alternatives) and len(set([c.strip() for c in criteria])) == len(criteria):
        st.markdown("---")
        st.header("2️⃣ Pairwise Comparison of Criteria")
    
    # if all(criteria) and all(alternatives):
    #     st.markdown("---")
    #     st.header("2️⃣ Pairwise Comparison of Criteria")

        A = np.ones((num_criteria, num_criteria))
        # Pairwise comparison (AHP)
        st.write("""
        **Pairwise Comparison Scale:**
        - **1**: Equally Preferred
        - **2**: Equally to Moderately
        - **3**: Moderately Preferred
        - **4**: Moderately to Strongly
        - **5**: Strongly Preferred
        - **6**: Strongly to Very Strongly
        - **7**: Very Strongly Preferred
        - **8**: Very Strongly to Extremely
        - **9**: Extremely Preferred
        """)
        for i in range(num_criteria):
            for j in range(i + 1, num_criteria):
                with st.expander(f"Compare {criteria[i]} vs {criteria[j]}"):
                    col1, col2 = st.columns([1, 3])

                    with col1:
                        higher_priority = st.radio(
                            "Select the more important criterion",
                            [criteria[i], criteria[j]],
                            # index=0 if default_radio == criteria[i] else 1,
                            key=f"crit_radio_{i}_{j}",
                            horizontal=True
                        )

                    with col2:
                        if higher_priority == criteria[i]:
                            prompt = f"How much more important is {criteria[i]} compared to {criteria[j]}?"
                        else:
                            prompt = f"How much more important is {criteria[j]} compared to {criteria[i]}?"

                        value = st.slider(prompt, 1, 9, key=f"crit_slider_{i}_{j}")

                        if higher_priority == criteria[i]:
                            A[i][j] = value
                            A[j][i] = 1 / value
                        else:
                            A[j][i] = value
                            A[i][j] = 1 / value

        weights, cr = calculate_ahp_weights(A)

        st.subheader("⚖️  Criteria Weights")
        weight_table = {"Criteria": criteria, "Weight": [round(w, 4) for w in weights]}
        st.dataframe(weight_table, use_container_width=True)

        st.info(f"Consistency Ratio (CR): {cr:.4f}")
        if cr > 0.1:
            st.error("Consistency Ratio exceeds 0.1. Please review your pairwise comparisons for consistency.")
        else:
            st.success("Consistency Ratio is within acceptable limits. Weights calculated successfully.")

        # Save weights and criteria for use in the next tab
        st.session_state["criteria"] = criteria
        st.session_state["weights"] = weights
        st.session_state["alternatives"] = alternatives

# Tab 2: TOPSIS
elif selected_tab == "☕ AHP + TOPSIS":
    st.header("☕ TOPSIS Method")

    if "criteria" not in st.session_state or "alternatives" not in st.session_state or "weights" not in st.session_state:
        st.warning("Please complete the data in the Weighting tab first.")
    else:
        criteria = st.session_state.criteria
        alternatives = st.session_state.alternatives
        weights = st.session_state.weights

        st.subheader("📈 Define Criteria Type (Benefit or Cost)")

        is_benefit = []
        for i in range(len(criteria)):
            previous_type = st.session_state.get(f"type_{i}", "Benefit")
            ctype = st.selectbox(f"Criteria Type for '{criteria[i]}'", ["Benefit", "Cost"], key=f"type_{i}")
            is_benefit.append(ctype == "Benefit")

        st.subheader("📥 Input Decision Matrix")
        st.markdown("🧾 Please fill in values for each alternative against the criteria (in scale 1 to 10):")

        matrix_df = pd.DataFrame(np.ones((len(alternatives), len(criteria))),
                     columns=criteria, index=alternatives)
        
        matrix_df = st.data_editor(matrix_df, use_container_width=True, num_rows="fixed")

        # Check if any value exceeds 10
        if (matrix_df > 10).any().any():
            st.warning("Some values exceed 10 and have been automatically capped at 10.")

        # Cap values at a maximum of 10
        matrix_df = matrix_df.clip(upper=10)

        if st.button("🔍 Calculate Location Ranking (TOPSIS)"):
            st.subheader("🏆 TOPSIS Calculation Results")
            decision_matrix = matrix_df.values.tolist()
            scores, ranking = topsis(decision_matrix, weights, is_benefit)

            result_df = pd.DataFrame({
                "Alternative": alternatives,
                "TOPSIS Score": [round(score, 4) for score in scores],
                "Ranking": [ranking.index(i) + 1 for i in range(len(alternatives))]
            })

            st.dataframe(result_df.sort_values(by="Ranking"), use_container_width=True)
            st.success("TOPSIS calculation completed successfully.")
            best_alternative = result_df[result_df["Ranking"] == 1].iloc[0]
            st.success(f"⭐ The best alternative is **{best_alternative['Alternative']}** with a score of {best_alternative['TOPSIS Score']:.4f}.")
            
            # Visualization of TOPSIS Scores
            st.subheader("📊 Visualization of TOPSIS Scores")

            # Create a bar chart using matplotlib
            fig, ax = plt.subplots()
            result_df_sorted = result_df.sort_values(by="Ranking")
            ax.bar(result_df_sorted["Alternative"], result_df_sorted["TOPSIS Score"], color='saddlebrown')
            ax.set_title("TOPSIS Scores")
            ax.set_xlabel("Alternative")
            ax.set_ylabel("Score")
            fig.set_size_inches(5, 3)
            plt.xticks(rotation=45, ha='right')

            # Display the chart in Streamlit
            st.pyplot(fig)

            # Add a download button for the chart
            buf = BytesIO()
            fig.savefig(buf, format="png")
            buf.seek(0)
            st.download_button(
                label="📥 Download Chart as Image",
                data=buf,
                file_name="topsis_scores.png",
                mime="image/png"
            )
        
            # # Map Overlay (Yogyakarta with Pins)
            # st.subheader("🗺️ Location Overlay: Yogyakarta Map")

            # # Central Yogyakarta coordinate
            # map_center = [-7.7956, 110.3695]
            # m = folium.Map(location=map_center, zoom_start=12, tiles="CartoDB dark_matter")  # dark coffee style

            # # Add pins for each alternative (you can assign coords manually or load from CSV)
            # coords = {
            #     "Malioboro": [-7.7928, 110.3658],
            #     "Sleman": [-7.7160, 110.3550],
            #     "Kotagede": [-7.8269, 110.4029]
            # }

            # for alt in alternatives:
            #     location = coords.get(alt, map_center)  # fallback if unknown
            #     folium.Marker(
            #         location,
            #         popup=f"{alt}",
            #         icon=folium.Icon(color="beige", icon="coffee", prefix="fa")
            #     ).add_to(m)

            # # Display map in Streamlit
            # st_folium(m, width=700, height=450)


# Tab 3: Profile Matching 
elif selected_tab == "☕ AHP + Profile Matching":
    st.header("☕ Profile Matching Method")

    if "criteria" not in st.session_state or "weights" not in st.session_state:
        st.warning("Please complete the data in the 'Weighting' tab first.")
    else:
        criteria = st.session_state.criteria
        weights = st.session_state.weights
        alternatives = st.session_state.alternatives

        # Ideal values for Profile Matching (to be input by user)
        st.subheader("🎯 Define Profile Ideal Values")
        st.markdown(f"**Ideal Values Scale:** 1 (lowest) to 5 (highest)")

        ideal_values = []
        for i, crit in enumerate(criteria):
            ideal_value = st.number_input(f"Enter ideal value for '{crit}' (1-5)", min_value=1, max_value=5, key=f"ideal_{i}")
            
            # Error check: Ensure ideal value is within range
            if ideal_value < 1 or ideal_value > 5:
                st.error(f"Ideal value for '{crit}' must be between 1 and 5.")
            else:
                ideal_values.append(ideal_value)
        
        # st.markdown(f"**Ideal Values Scale:** 1 (lowest) to 5 (highest)")

        # Input for core and secondary factors
        st.subheader("⚙️ Define Core Factor (CF) and Secondary Factor (SF)")
        cf_flags = []

        for i, crit in enumerate(criteria):
            factor = st.selectbox(
                f"Is '{crit}' a Core Factor (CF) or Secondary Factor (SF)?",
                ["CF (Core Factor)", "SF (Secondary Factor)"],
                key=f"cf_sf_{i}"
            )
            cf_flags.append(factor.startswith("CF"))

        # Calculate total weights for CF and SF based on AHP results
        total_weight = sum(weights)
        cf_weight = sum(w for w, is_cf in zip(weights, cf_flags) if is_cf)
        sf_weight = total_weight - cf_weight

        st.markdown("---")
        st.write("📊 Factor Summary:")
        factor_df = pd.DataFrame({
            "Criteria": criteria,
            "AHP Weight": [round(w, 4) for w in weights],
            "Factor": ["CF" if is_cf else "SF" for is_cf in cf_flags]
        })
        st.dataframe(factor_df, use_container_width=True)

        st.markdown(f"**Total CF Weight:** {cf_weight:.4f} ({(cf_weight / total_weight * 100):.2f}%)")
        st.markdown(f"**Total SF Weight:** {sf_weight:.4f} ({(sf_weight / total_weight * 100):.2f}%)")

        if cf_weight / total_weight < 0.5:
            st.error("⚠️ The total CF weight must be greater than 50%. Please adjust the CF/SF selection.")
        else:
            st.success("✅ CF/SF selection is valid. You can proceed to the next step.")
        
        # Input for decision matrix
        st.subheader("📥 Input Decision Matrix")

        # Limit number of alternatives
        if len(alternatives) > 5:
            st.warning("⚠️ Maximum of 5 alternatives allowed. Extra alternatives will be ignored.")
            alternatives = alternatives[:5]

        num_alternatives = len(alternatives)
        num_criteria = len(criteria)

        # Create default decision matrix (all values set to 1)
        decision_matrix_df = pd.DataFrame(
            np.ones((num_alternatives, num_criteria)),
            columns=criteria,
            index=alternatives
        )

        st.markdown("🧾 Please fill in values for each alternative against the criteria (in scale 1 to 5):")
        decision_matrix_df = st.data_editor(
            decision_matrix_df,
            use_container_width=True,
            num_rows="fixed",
            key="pm_matrix_input"
        )
        # Check if any value exceeds 5
        if (decision_matrix_df > 5).any().any():
            st.warning("Some values exceed 5 and have been automatically capped at 5.")
        
        # Auto-correct any input values outside the range [1, 5]
        decision_matrix_df = decision_matrix_df.clip(lower=1, upper=5)

        # Save to session state for further processing
        st.session_state["decision_matrix"] = decision_matrix_df.values.tolist()

        # Setelah input Core Factor (CF) dan Secondary Factor (SF) oleh pengguna
        cf_sf_grouping = ["CF" if is_cf else "SF" for is_cf in cf_flags]
        
        # Button to calculate Profile Matching
        if st.button("🔍 Calculate Location Ranking (Profile Matching)"):
            # ideal_profile = ideal_values
            matrix_pm = decision_matrix_df.values.tolist()
            cf_sf_grouping = ["CF" if is_cf else "SF" for is_cf in cf_flags]
            
            # Use ideal_values from user input
            scores_pm, ranking_order_pm = profile_matching(
                ideal=ideal_values,
                actuals=matrix_pm,
                weights=weights,
                cf_sf_grouping=cf_sf_grouping
            )
            
            # Sorting the scores based on profile matching
            # ranking_order_pm = np.argsort(-np.array(scores_pm))
            result_df_pm = pd.DataFrame({
                "Alternative": np.array(alternatives)[ranking_order_pm],
                "Profile Matching Score": np.round(np.array(scores_pm)[ranking_order_pm], 4),
                "Ranking": np.arange(1, num_alternatives + 1)
            })

            # Display the results
            st.subheader("🏆 Profile Matching Calculation Results")
            st.dataframe(result_df_pm, use_container_width=True, hide_index=True)
                         
            # Display the best alternative and its score
            best_pm = result_df_pm[result_df_pm["Ranking"] == 1].iloc[0]
            st.success("Profile Matching calculation completed successfully.")
            st.success(f"⭐ The best alternative is **{best_pm['Alternative']}** with a Profile Matching score of {best_pm['Profile Matching Score']:.4f}.")

            # Visualization of Profile Matching Scores
            st.subheader("📊 Visualization of Profile Matching Scores")

            # Create a bar chart using matplotlib
            fig_pm, ax_pm = plt.subplots()
            result_df_pm_sorted = result_df_pm.sort_values(by="Ranking")
            ax_pm.bar(result_df_pm_sorted["Alternative"], result_df_pm_sorted["Profile Matching Score"], color='saddlebrown')
            ax_pm.set_title("Profile Matching Scores")
            ax_pm.set_xlabel("Alternative")
            ax_pm.set_ylabel("Score")
            fig_pm.set_size_inches(5, 3)  # Set width=8 inches, height=5 inches
            plt.xticks(rotation=45, ha='right')

            # Display the chart in Streamlit
            st.pyplot(fig_pm)

            # Add a download button for the chart
            buf_pm = BytesIO()
            fig_pm.savefig(buf_pm, format="png")
            buf_pm.seek(0)
            st.download_button(
                label="📥 Download Chart as Image",
                data=buf_pm,
                file_name="profile_matching_scores.png",
                mime="image/png"
            )
            st.success("Profile Matching scores visualization generated successfully.")

            # Radar chart berdasarkan kedekatan ke profil ideal
            st.subheader("🛫️ Closeness to Ideal Profile (Radar Chart)")
            closeness_matrix = []
            range_scale = 4  # assuming 1-5 scale
            for row in matrix_pm:
                closeness_row = [1 - abs(val - ideal) / range_scale for val, ideal in zip(row, ideal_values)]
                closeness_matrix.append(closeness_row)

            fig_radar, ax_radar = plt.subplots(figsize=(8, 7), subplot_kw=dict(polar=True))
            angles = np.linspace(0, 2 * np.pi, num_criteria, endpoint=False).tolist()
            angles += angles[:1]

            bold_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#7a42ad']

            for i, row in enumerate(closeness_matrix):
                values = row + row[:1]
                ax_radar.plot(angles, values, label=alternatives[i], linewidth=2.5, marker='o', color=bold_colors[i % len(bold_colors)])
                ax_radar.fill(angles, values, alpha=0.25, color=bold_colors[i % len(bold_colors)])

            ax_radar.set_thetagrids(np.degrees(angles[:-1]), criteria, fontsize=11, ha='center')
            ax_radar.set_ylim(0, 1)
            ax_radar.set_title("Closeness of Alternatives to Ideal Profile", size=13, pad=30)
            ax_radar.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=2, frameon=False)
            ax_radar.grid(True, linestyle='--', alpha=0.5)

            st.pyplot(fig_radar)

            buf_radar = BytesIO()
            fig_radar.savefig(buf_radar, format="png", transparent=True, bbox_inches='tight')
            buf_radar.seek(0)
            st.download_button(
                label="🗕️ Download Radar Chart as Image",
                data=buf_radar,
                file_name="radar_closeness_to_ideal.png",
                mime="image/png"
            )
            st.success("Radar chart visualizing closeness to ideal profile generated successfully.")


            # st.subheader("🛱️ Closeness to Ideal Profile (Radar Chart)")
            # closeness_matrix = []
            # range_scale = 4  # assuming 1-5 scale
            # for row in matrix_pm:
            #     closeness_row = [1 - abs(val - ideal) / range_scale for val, ideal in zip(row, ideal_values)]
            #     closeness_matrix.append(closeness_row)

            # fig_radar, ax_radar = plt.subplots(figsize=(8, 7), subplot_kw=dict(polar=True))
            # angles = np.linspace(0, 2 * np.pi, num_criteria, endpoint=False).tolist()
            # angles += angles[:1]

            # bold_colors = ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00']

            # for i, row in enumerate(closeness_matrix):
            #     values = row + row[:1]
            #     ax_radar.plot(angles, values, label=alternatives[i], linewidth=2.5, marker='o', color=bold_colors[i % len(bold_colors)])
            #     ax_radar.fill(angles, values, alpha=0.25, color=bold_colors[i % len(bold_colors)])

            # ax_radar.set_thetagrids(np.degrees(angles[:-1]), criteria, fontsize=10)
            # ax_radar.set_ylim(0, 1)
            # ax_radar.set_title("Closeness of Alternatives to Ideal Profile", size=15, pad=20)
            # ax_radar.legend(loc='lower center', bbox_to_anchor=(0.5, -0.15), ncol=2)

            # st.pyplot(fig_radar)

            # buf_radar = BytesIO()
            # fig_radar.savefig(buf_radar, format="png")
            # buf_radar.seek(0)
            # st.download_button(
            #     label="📅 Download Radar Chart as Image",
            #     data=buf_radar,
            #     file_name="radar_closeness_to_ideal.png",
            #     mime="image/png"
            # )
            # st.success("Radar chart visualizing closeness to ideal profile generated successfully.")

            # # Radar chart with enhanced style
            # st.subheader("📡 Closeness to Ideal Profile (Radar Chart)")
            # closeness_matrix = []
            # range_scale = 4
            # for row in matrix_pm:
            #     closeness_row = [1 - abs(val - ideal) / range_scale for val, ideal in zip(row, ideal_values)]
            #     closeness_matrix.append(closeness_row)

            # fig_radar, ax_radar = plt.subplots(figsize=(7, 6), subplot_kw=dict(polar=True))
            # angles = np.linspace(0, 2 * np.pi, num_criteria, endpoint=False).tolist()
            # angles += angles[:1]

            # custom_colors = ['#A6CEE3', '#B2DF8A', '#FDBF6F', '#CAB2D6', '#FF9999']

            # for i, row in enumerate(closeness_matrix):
            #     values = row + row[:1]
            #     ax_radar.fill(angles, values, color='black', alpha=0.05, zorder=1)  # shadow layer
            #     ax_radar.plot(angles, values, label=alternatives[i], linewidth=2.5, marker='o', color=custom_colors[i % len(custom_colors)], zorder=2)
            #     ax_radar.fill(angles, values, alpha=0.25, color=custom_colors[i % len(custom_colors)], zorder=3)

            # ax_radar.set_thetagrids(np.degrees(angles[:-1]), criteria, fontsize=10)
            # ax_radar.set_ylim(0, 1)
            # ax_radar.set_title("Closeness of Alternatives to Ideal Profile", size=15, pad=20)
            # ax_radar.yaxis.grid(True, color='gray', linestyle='--', linewidth=0.5, alpha=0.3)
            # ax_radar.legend(loc='upper right', bbox_to_anchor=(1.2, 1))

            # st.pyplot(fig_radar)

            # buf_radar = BytesIO()
            # fig_radar.savefig(buf_radar, format="png")
            # buf_radar.seek(0)
            # st.download_button(
            #     label="📅 Download Radar Chart as Image",
            #     data=buf_radar,
            #     file_name="radar_closeness_to_ideal.png",
            #     mime="image/png"
            # )
            # st.success("Radar chart visualizing closeness to ideal profile generated successfully.")

         