import pandas as pd
import re
def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    patterns = [
        r'^\d',           # starts with number
        r'[.\s-]',        # contains dot, space, or hyphen
        r'[^a-zA-Z0-9_]',  # contains special chars other than underscore
    ]
    def clean(col):
        new_col = col
        # Replace dots, spaces, hyphens with underscore
        new_col = re.sub(r'[.\s-]+', '_', new_col)
        # Remove special characters except underscore
        new_col = re.sub(r'[^a-zA-Z0-9_]', '', new_col)
        # If starts with number, prepend 'col_'
        if re.match(r'^\d', new_col):
            new_col = 'col_' + new_col
        return new_col
    df = df.rename(columns={col: clean(col) for col in df.columns})
    return df