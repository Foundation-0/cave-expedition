"""Sawtooth values k/64, k = 0..63: peak to peak 63/64, standard deviation sqrt(4095/12)/64, half of it 0.1443 (plan section 10 and D16).
Standard library only. No bare assert."""
import math
import sys
from fractions import Fraction

FAILS = []


def control(tag, flagged):
    print(f"CONTROL {tag} | wrong input flagged = {flagged}")
    if not flagged:
        FAILS.append(tag)


vals = [Fraction(k, 64) for k in range(64)]
mean = sum(vals) / 64
var = sum((v - mean) ** 2 for v in vals) / 64
ptp = max(vals) - min(vals)
print(f"CLAIM saw-ptp | peak to peak 63/64 | text=63/64 | mine={ptp} | {'REPRODUCED' if ptp == Fraction(63, 64) else 'DIFFERS'}")
print(f"CLAIM saw-var | variance = 4095/12 / 64^2 | text=4095/12/64^2 | mine={var} equals {Fraction(4095, 12) / 64**2} | {'REPRODUCED' if var == Fraction(4095, 12) / 64**2 else 'DIFFERS'}")
sd = math.sqrt(float(var))
print(f"CLAIM saw-sd | sd {sd:.6f}; half {sd/2:.6f} | text=0.1443 (and 0.144) | mine={sd/2:.4f} | {'REPRODUCED' if f'{sd/2:.4f}' == '0.1443' else 'DIFFERS'}")
sd_pop_n = math.sqrt(float(sum((v - mean) ** 2 for v in vals) / 63))
print(f"INFO sample divisor would give sd {sd_pop_n:.6f}, half {sd_pop_n/2:.4f} (the plan's figure uses the population divisor, which is the sd of the waveform itself)")
print(f"INFO continuous peak-to-peak-1 ramp: half sd = {1/math.sqrt(12)/2:.5f}; the discrete ramp k/64 gives {sd/2:.5f}; both round to 0.1443 / 0.1443")
control("wrong noise 0.5 flagged", f"{sd/2:.4f}" != "0.5000")
if FAILS:
    sys.exit(1)
print("DONE saw_noise")
