import numpy as np

t = np.loadtxt("time_c.txt")

# Remove accidental zero 
t = t[t > 0]

print(f"count: {len(t)}")
print(f"min: {np.min(t):.0f} ns")
print(f"mean: {np.mean(t):.2f} ns")
print(f"median: {np.median(t):.0f} ns")
print(f"90th percentile: {np.percentile(t, 90):.0f} ns")
print(f"99th percentile: {np.percentile(t, 99):.0f} ns")
print(f"max: {np.max(t):.0f} ns")
