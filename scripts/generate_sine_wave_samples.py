#************************************************************
# File name: generate_sine_wave_samples.py
# Description: A table that holds the sine waves sample values
# ************************************************************

import numpy as np
import matplotlib.pyplot as plt
import argparse
import os

############################## Ask user for parameters ##############################

parser = argparse.ArgumentParser(description="Generate DDS sine LUT and VHDL package")

parser.add_argument("-a","--addr_width", type=int, required=True,
                    help="ROM address width")

parser.add_argument("-d","--data-width", type=int, required=True,
                    help="Amplitude quantization bits (Used for DAC input)")

parser.add_argument("-o","--out", type=str, default=".",
                    help="Output directory for generated files")

parser.add_argument("-p","--plots", type=str, default=".",
                    help="Do you want to plot the sine wave?")

parser.add_argument("-s","--save-plots", action="store_true",
                    help="Save plots to output directory")

args = parser.parse_args()

output_path = args.out
os.makedirs(output_path, exist_ok=True)
plot = args.plots

print(f"Generating 1/4 of a sine wave cycle\n")

############################## Sampling sine wave ##############################

rom_addr_width = args.addr_width - 2 # for an P bit truncation, P-2 bits are used for a ROM that holds 1/4 of the cycle
N = 2**rom_addr_width  # Number of samples in 1/4 of a sine wave cycle

phase_step = np.linspace(0, np.pi/2, N, endpoint=False) # We divide the 0-pi/2 interval of 
                                                        # the phase into N equal pieces.
sine_samples = np.sin(phase_step)                       # linspace makes phase_step into 
                                                        # an array from 0 to N-1

############################## Quantization of sine wave samples #####################

dac_bits = args.data_width
rom_bits = dac_bits -1
amplitude_bits = rom_bits   # one bit reserved for sign later
max_amplitude = (2**amplitude_bits) - 1  # 2047 for 12-bit system

quantized_values = np.round(sine_samples * max_amplitude).astype(int)

lut_samples = quantized_values / max_amplitude
error = sine_samples - lut_samples
mse = np.mean(error**2)
print("\nLUT Quantization Analysis")
print("_________________________")
print(f"MSE  : {mse:.6e}")
max_error = np.max(np.abs(error))

print(f"MAX ERROR : {max_error:.6e}")

############################## Save quantized values in a .txt file ######################

txt_filename = os.path.join(
    output_path,
    f"sine_lut.txt"
)

with open(txt_filename, "w") as f:
    for value in quantized_values:
        f.write(f"{value}\n")

print(f"LUT saved to {txt_filename}")

############################## Generate .vhd file with LUT samples ##############################

rtl_filename = os.path.join(
    output_path,
    f"sine_table_pkg.vhd"
)

with open(rtl_filename, "w") as f:
    f.write(f"-- ************************************************************\n")
    f.write(f"-- File name: {rtl_filename}\n")
    f.write(f"-- Description: A table that holds the sine waves sample values\n")
    f.write(f"-- Dimensions:  {N} x {rom_bits}\n")
    f.write(f"-- ************************************************************\n\n")
    f.write(f"library ieee;\n")
    f.write(f"use ieee.std_logic_1164.all;\n")
    f.write(f"use ieee.numeric_std.all;\n")
    f.write(f"use work.rom_types_pkg.all;\n\n")
    f.write(f"package sine_table_pkg is\n\n")
    f.write(f"    -- ******************************************************\n")
    f.write(f"    -- Constants\n")
    f.write(f"    -- ******************************************************\n")
    f.write(f"    constant DATA_WIDTH : integer := {rom_bits};\n")
    f.write(f"    constant ADDR_WIDTH : integer := {rom_addr_width};\n")
    f.write(f"    constant ROM_DEPTH  : integer := {N};\n\n")
    f.write(f"    -- ******************************************************\n")
    f.write(f"    -- Table of constant values\n")
    f.write(f"    -- ******************************************************\n\n")
    f.write(f"    constant sine_table : rom_type(0 to ROM_DEPTH-1) := (\n")

    for i in range(N):
        if i == N-1:
            f.write(f"        {i} => to_unsigned({quantized_values[i]}, DATA_WIDTH)\n")
        else:
            f.write(f"        {i} => to_unsigned({quantized_values[i]}, DATA_WIDTH),\n")

    f.write("    );\n")
    f.write("end package sine_table_pkg;\n\n")

    f.write("package body sine_table_pkg is\n")
    f.write("end package body sine_table_pkg;\n")

print(f"VHDL Memory package {rtl_filename} generated\n")

print("DDS LUT configuration")
print("_____________________")
print(f"ROM depth      : {N}")
print(f"Address width  : {rom_addr_width}")
print(f"Amplitude bits : {rom_bits}\n")
print(f"Output path    : {output_path}\n")

############################## Create Plots ##############################

answers_str = ["yes", "no"]

# Plots created:
#   - Ideal sine wave
#   - Sampled sine wave compared on ideal
#   - Quantized

if plot == answers_str[1]:
    print("No plots created")
elif plot == answers_str[0]:
    
    # Ideal sine wave
    plt.figure()
    plt.plot(phase_step, sine_samples, label="Sampled sine")
    plt.title("Sampled Sine Wave (Quarter Cycle)")
    plt.xlabel("Phase")
    plt.ylabel("Amplitude")
    plt.grid(True)

    plt.savefig("ideal_sine.png")

    # Sampled sine wave compared on ideal
    plt.figure()
    plt.step(phase_step, quantized_values, where="mid", label="Quantized")
    plt.plot(phase_step, quantized_values, '.', markersize=2)
    plt.title("Quantized Sine LUT")
    plt.xlabel("Phase")
    plt.ylabel("Amplitude")
    plt.grid(True)

    plt.show()

    plt.savefig("quantized_sine.png")
else:
    print(f"Acceptable answers in -p argument are "'yes'" or "'no'"")


