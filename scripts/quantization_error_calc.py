import numpy as np
import matplotlib.pyplot as plt


# ************************************************************
# Ideal Sine
# ************************************************************

num_samples = 2**20

t = np.linspace(
    0,
    100,
    num_samples,
    endpoint=False
)

ideal = np.sin(
    2*np.pi*t
)


# ************************************************************
# Quantization Study
# ************************************************************

bit_values = [
    4,
    6,
    8,
    10,
    12,
    14,
    16
]

mse_results = []
snr_results = []
snr_theoritical_results=[]

print()
print("Amplitude Quantization Analysis")
print()

for A in bit_values:

    # ****************************************
    # Quantizer
    # ****************************************

    max_code = 2**(A-1)-1

    quantized = np.round(
        ideal * max_code
    )

    quantized = (
        quantized /
        max_code
    )

    # ****************************************
    # Error
    # ****************************************

    error = (
        ideal -
        quantized
    )

    # ****************************************
    # MSE
    # ****************************************

    mse = np.mean(
        error**2
    )

    mse_results.append(
        mse
    )

    # ****************************************
    # SNR
    # ****************************************

    signal_power = np.mean(
        ideal**2
    )

    noise_power = np.mean(
        error**2
    )

    snr = 10*np.log10(
        signal_power /
        noise_power
    )

    snr_results.append(
        snr
    )


    # ************************************************************
    # Theoretical SNR
    # ************************************************************

    theoretical_snr =  6.02 * A + 1.76

    snr_theoritical_results.append(
        theoretical_snr
    )


    print(
        f"A = {A:2d} bits | "
        f"MSE = {mse:.6e} | "
        f"SNR = {snr:8.7f} dB | "
        f"SNR Theoritical= {theoretical_snr:8.7f} dB"
    )


# ************************************************************
# MSE Plot
# ************************************************************

plt.figure(figsize=(8,5))

plt.plot(
    bit_values,
    mse_results,
    marker='o'
)

plt.grid(True)

plt.xlabel(
    "Αριθμός bit πλάτους, Α"
)

plt.ylabel(
    "MSE"
)

plt.title(
    "Κβαντοποίηση πλάτους\n"
    "MSE - Αριθμός bit Α"
)

plt.show()


# ************************************************************
# SNR Plot
# ************************************************************

plt.figure(figsize=(8,5))

plt.plot(
    bit_values,
    snr_results,
    marker='o',
    label='Simulation'
)

plt.plot(
    bit_values,
    snr_theoritical_results,
    '--',
    label='6.02B + 1.76'
)

plt.grid(True)

plt.xlabel(
    "Αριθμός bit πλάτους, Α"
)

plt.ylabel(
    "SNR (dB)"
)

plt.title(
    "Κβαντοποίηση πλάτους\n"
    "SNR - Αριθμός bit Α"
)

plt.legend()

plt.show()
