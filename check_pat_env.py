#!/usr/bin/env python3
import os

pat = os.getenv("MY_APP_GITHUB_PAT")
if pat:
    # Corrected f-string: removed backslashes from around '*' and '***'
    print(f"PAT_FOUND:{'*' * (len(pat) - 4) + pat[-4:] if len(pat) > 4 else '***'}")
else:
    print("PAT_NOT_FOUND")

