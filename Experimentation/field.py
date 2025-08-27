import matplotlib.pyplot as plt
import matplotlib.patches as patches

# This is a simple script to draw a college football field. 
# It is used to visualize the field and the lines.
# Source: ChatGPT   

# Field dimensions (college football in yards)
FIELD_LENGTH = 120  # 100 yards + 2 endzones
FIELD_WIDTH = 53.3

fig, ax = plt.subplots(figsize=(12, 6))

# Draw the field rectangle
field = patches.Rectangle((0, 0), FIELD_LENGTH, FIELD_WIDTH, linewidth=2,
                          edgecolor='black', facecolor='green')
ax.add_patch(field)

# Yard lines every 5 yards
for x in range(10, FIELD_LENGTH, 5):
    ax.plot([x, x], [0, FIELD_WIDTH], color="white", linewidth=1)

# Thicker lines every 10 yards
for x in range(10, FIELD_LENGTH, 10):
    ax.plot([x, x], [0, FIELD_WIDTH], color="white", linewidth=2)

# College hash marks (20 yards from each sideline)
HASH_Y_BOTTOM = 20.0
HASH_Y_TOP = FIELD_WIDTH - 20.0
HASH_LEN = 0.5  # length of each hash mark in yards

# Place hash marks at each yard between the 10s, skip full 5-yard lines
for x in range(11, 110):
    if x % 5 == 0:
        continue
    # Bottom hashes
    ax.plot([x, x], [HASH_Y_BOTTOM - HASH_LEN / 2, HASH_Y_BOTTOM + HASH_LEN / 2], color="white", linewidth=2)
    # Top hashes
    ax.plot([x, x], [HASH_Y_TOP - HASH_LEN / 2, HASH_Y_TOP + HASH_LEN / 2], color="white", linewidth=2)

# End zones
endzone1 = patches.Rectangle((0, 0), 10, FIELD_WIDTH, linewidth=1,
                             edgecolor="white", facecolor="darkblue", alpha=0.6)
endzone2 = patches.Rectangle((110, 0), 10, FIELD_WIDTH, linewidth=1,
                             edgecolor="white", facecolor="darkred", alpha=0.6)
ax.add_patch(endzone1)
ax.add_patch(endzone2)

# Yard numbers (every 10 yards from each side)
for x in range(20, 110, 10):
    ax.text(x, 5, str(x-10), color="white", fontsize=8, ha="center", va="center", rotation=0)
    ax.text(x, FIELD_WIDTH-5, str(x-10), color="white", fontsize=8, ha="center", va="center", rotation=180)

# Set axis
ax.set_xlim(0, FIELD_LENGTH)
ax.set_ylim(0, FIELD_WIDTH)
ax.set_aspect('equal')
ax.axis("off")

plt.show()