import streamlit as st
import pandas as pd
from streamlit import column_config


# -------------------- Title of the app --------------------
st.set_page_config(page_title="Gold Standard Data Viewer", layout="wide")
st.title("VAST Gold Standard Database")

# -------------------- Load your data --------------------
def load_data():
    # df = pd.read_csv('/suphys/sura0296/scripts/gold_std_data.txt', sep='\t')
    df = pd.read_csv('https://github.com/surabhichandra22/vast-gold-std/blob/main/data_files/gold_std_data.txt', sep='\t')
    return df

df = load_data()

# ------------------ Filter widgets ------------------

classification_options = ['point', 'extended', 'noisy', 'artefact', 'undecided']

st.sidebar.header("Filter Columns")

editable_cols = ['Surabhi', 'Dougal', 'Tara', 'Final Classification']
filter_cols = [col for col in df.columns if col not in editable_cols + ['PNG', 'FITS']]

filtered_df = df.copy()

# Add a blank "Comments" column if it's missing
if 'Comments' not in filtered_df.columns:
    filtered_df['Comments'] = ""  # or np.nan

for col in filter_cols:
    if df[col].dtype == 'object':
        options = ['All'] + sorted(df[col].dropna().unique())
        selected = st.sidebar.selectbox(f"Filter {col}", options, key=col)
        if selected != 'All':
            filtered_df = filtered_df[filtered_df[col] == selected]
    else:
        min_val = float(df[col].min())
        max_val = float(df[col].max())
        if min_val == max_val:
            st.sidebar.markdown(f"Only one value in {col}: {min_val}")
        else:
            selected_range = st.sidebar.slider(f"{col} range", min_val, max_val, (min_val, max_val))
            filtered_df = filtered_df[(df[col] >= selected_range[0]) & (df[col] <= selected_range[1])]

st.markdown(f"**Filtered Rows: {len(filtered_df)}**")

# ------------------ Prepare display columns ------------------

# Make PNG view and FITS download columns
def make_fits_link(row):
    url = row['FITS']
    return f'<a href="{url}" download target="_blank">FITS download</a>'

def make_png_block(row):
    return f'<img src="{row["PNG"]}" width="150"><br><a href="{row["PNG"]}" target="_blank">View Full Image</a>'

filtered_df['FITS Download'] = filtered_df.apply(make_fits_link, axis=1)
filtered_df['PNG_Display'] = filtered_df.apply(make_png_block, axis=1)

# Ensure editable fields are actual strings
for col in editable_cols:
    filtered_df[col] = filtered_df[col].astype(str).replace({'nan': ''})

# ------------------ Show editable table ------------------

# List of editable columns (user input)
editable_cols = ['Surabhi', 'Dougal', 'Tara', 'Final Classification', 'Comments']

# List of extra columns you want to display (non-editable)
display_cols = ['Local RMS', 'Compactness', 'RMS median', 'Avg Compactness', 'B min', 'B maj']

# Ensure the 'PNG' column contains only the raw link (not Markdown)
filtered_df['PNG'] = df['PNG']  # Copy from original df in case it was changed

# Add the FITS download link column (just raw URLs)
filtered_df['FITS file'] = df['FITS']

# Force editable columns to be strings and fill missing values
for col in editable_cols:
    filtered_df[col] = filtered_df[col].fillna("").astype(str)

# Insert row numbers starting from 1
filtered_df.insert(0, 'S. No.', range(1, len(filtered_df) + 1))

# Final set of columns to show in the data editor
columns_to_show = ['S. No.', 'Source ID', 'Image ID', 'Expected'] + display_cols + editable_cols + ['PNG'] + ['FITS file']

# Force editable columns to be strings (so they are editable)
for col in editable_cols:
    filtered_df[col] = filtered_df[col].astype(str).replace({'nan': ''})

# Show the data editor
edited_df = st.data_editor(
    filtered_df[columns_to_show],
    column_config={
        'Surabhi': column_config.SelectboxColumn("Surabhi", options=classification_options),
        'Dougal': column_config.SelectboxColumn("Dougal", options=classification_options),
        'Tara': column_config.SelectboxColumn("Tara", options=classification_options),
        'Final Classification': column_config.SelectboxColumn("Final Classification", options=classification_options),
        # 'Comments': column_config.TextColumn("Comments"),
        'Comments': column_config.TextColumn("Comments", width="large"),
        'PNG': column_config.LinkColumn(label="PNG image", display_text="PNG image"),
        'FITS file': column_config.LinkColumn(label="FITS file", display_text="Download FITS")
    },
    use_container_width=True,
    height=600,
    num_rows="dynamic",
    key="editable_table"
)

# ------------------ Save button ------------------

if st.button("Save Changes"):
    edited_df.to_csv("/suphys/sura0296/scripts/gold_std_data_edited.txt", sep='\t', index=False)
    st.success("Changes saved!")

