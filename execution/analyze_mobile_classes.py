import re
from collections import Counter

with open("mobile_category_debug.html", "r", encoding="utf-8") as f:
    content = f.read()

classes = re.findall(r'class="([^"]+)"', content)
class_counts = Counter()
for cl_str in classes:
    for cl in cl_str.split():
        class_counts[cl] += 1

print("Top 20 classes:")
for cl, count in class_counts.most_common(20):
    print(f"{cl}: {count}")

# Find classes near "Rs."
rs_pos = content.find("Rs.")
if rs_pos != -1:
    print(f"\nContext near Rs.: {content[rs_pos-200:rs_pos+200]}")
