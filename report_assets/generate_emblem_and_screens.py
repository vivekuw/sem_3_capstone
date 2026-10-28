import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

os.makedirs('report_assets', exist_ok=True)

# 1. College Emblem Seal
fig, ax = plt.subplots(figsize=(4, 4), dpi=250)
ax.axis('off')

# Outer red ring
circle_outer = plt.Circle((0.5, 0.5), 0.46, color='#991b1b', ec='#7f1d1d', lw=3)
circle_inner_ring = plt.Circle((0.5, 0.5), 0.44, color='white')
circle_inner_red = plt.Circle((0.5, 0.5), 0.32, color='#991b1b')
circle_center_white = plt.Circle((0.5, 0.5), 0.30, color='#fff7ed')

ax.add_patch(circle_outer)
ax.add_patch(circle_inner_ring)
ax.add_patch(circle_inner_red)
ax.add_patch(circle_center_white)

# Text in ring
ax.text(0.5, 0.88, "KANDIVLI EDUCATION SOCIETY'S", ha='center', va='center', fontsize=7.5, weight='bold', color='#991b1b')
ax.text(0.5, 0.82, "CHARACTER IS DESTINY", ha='center', va='center', fontsize=6.8, weight='bold', color='#991b1b', style='italic')
ax.text(0.5, 0.12, "MUMBAI - 400067", ha='center', va='center', fontsize=7.5, weight='bold', color='#991b1b')

# Center emblem (Torch / Gear / Book symbol)
ax.plot([0.5, 0.5], [0.38, 0.58], color='#991b1b', lw=3.5) # Torch stem
flame = mpatches.Polygon([[0.5, 0.68], [0.46, 0.60], [0.5, 0.63], [0.54, 0.60]], color='#ea580c')
ax.add_patch(flame)
book = mpatches.Polygon([[0.40, 0.38], [0.5, 0.34], [0.60, 0.38], [0.60, 0.44], [0.5, 0.40], [0.40, 0.44]], color='#991b1b')
ax.add_patch(book)

ax.text(0.5, 0.48, "1989", ha='center', va='center', fontsize=8.5, weight='bold', color='#991b1b')

ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
plt.tight_layout()
fig.savefig('report_assets/college_emblem.png', bbox_inches='tight', transparent=False, dpi=250)
plt.close(fig)

print("College emblem generated successfully.")
