import numpy as np

vref = 3.3
dac_bits = 12
fclk = 100e6  # 100 MHz
T = 1/fclk
max_value = (2**dac_bits) - 1

with open("dds_samples.txt", "r") as file_in:
    samples = [int(line.strip()) for line in file_in if line.strip()]

with open("dds_pwl.txt", "w") as fout:

    for i, sample in enumerate(samples):
        t0 = i * T
        t1 = (i + 1) * T
        voltage = sample * vref / max_value

        fout.write(f"{t0:.12e} {voltage:.6f}\n")
        fout.write(f"{t1-1e-12:.12e} {voltage:.6f}\n")

print("File 'dds_pwl.txt' was generated")
