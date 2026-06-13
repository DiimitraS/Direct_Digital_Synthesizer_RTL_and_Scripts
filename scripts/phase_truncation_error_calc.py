import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft

# ************************************************************
# DDS Parameters
# ************************************************************

N = 32          # Phase accumulator bits

num_samples = 2**20
P_values = [8,10,12,14,16,18]
#P_values = [26,28]

mse_results = []
rms_results = []
sfdr_results = []
sfdr_fft_results = []
worst_case_k_samples = []

for P in P_values:

# Tuning word that yields worst truncation error
    k = 2**(N-P-1)

    acc = (
        np.arange(num_samples,
                  dtype=np.uint64)
        * k
    ) % (2**N)

# ************************************************************
# Ideal DDS
# ************************************************************

    acc = (
        np.arange(num_samples, dtype=np.uint64)
        * k
    ) % (2**N)

    phi_ideal = (
        acc.astype(np.float64)
        / (2**N)
    ) * 2*np.pi

    ideal = np.sin(phi_ideal)

    # ****************************************
    # Keep only P MSBs
    # ****************************************

    acc_trunc = acc >> (N - P)

    phi_trunc = (
        acc_trunc.astype(np.float64)
        / (2**P)
    ) * 2*np.pi

    trunc_signal = np.sin(phi_trunc)

    # ****************************************
    # FFT-based SFDR
    # ****************************************

    window = np.hanning(len(trunc_signal))

    fft_result = fft(
        trunc_signal * window
    )

    magnitude = np.abs(
        fft_result[:len(fft_result)//2]
    )

    # Fundamental

    fund_idx = np.argmax(
        magnitude
    )

    fund_mag = magnitude[
        fund_idx
    ]   

    # Remove fundamental + leakage

    magnitude_no_fund = magnitude.copy()

    guard_bins = 20

    start = max(
        0,
        fund_idx - guard_bins
    )

    stop = min(
        len(magnitude),
        fund_idx + guard_bins + 1
    )

    magnitude_no_fund[
        start:stop
    ] = 0

    # Largest spur

    spur_idx = np.argmax(
        magnitude_no_fund
    )

    spur_mag = magnitude_no_fund[
        spur_idx
    ]

    sfdr_fft = 20*np.log10(
        fund_mag /
        (spur_mag + 1e-15)
    )

    # ****************************************
    # Error
    # ****************************************

    error = ideal - trunc_signal

    mse = np.mean(
        error**2
    )

    rms = np.sqrt(
        mse
    )

    sfdr_theory = 6.02 * P

    sfdr_results.append(
        sfdr_theory
    )

    sfdr_fft_results.append(
        sfdr_fft
    )   

    mse_results.append(
        mse
    )

    rms_results.append(
        rms
    )
    worst_case_k_states = 2**(P+1)

    worst_case_k_samples.append(
        worst_case_k_states
    )

print(f"\nResults for all P values")
print(
    f"{'P':>4} "
    f"{'No. Samples':>15} "
    f"{'MSE':>15} "
    f"{'RMS':>15} "
    f"{'SFDR Theory':>15} "
    f"{'SFDR FFT':>15}"
)

for P, states, mse, rms, sfdr_th, sfdr_fft in zip(
        P_values,
        worst_case_k_samples,
        mse_results,
        rms_results,
        sfdr_results,
        sfdr_fft_results):

    print(
        f"{P:4d} "
        f"{states:15d} "
        f"{mse:15.6e} "
        f"{rms:15.6e} "
        f"{sfdr_th:15.2f} "
        f"{sfdr_fft:15.2f}"
    )
# ************************************************************
# MSE Plot
# ************************************************************

plt.figure(figsize=(8,5))

plt.plot(
    P_values,
    mse_results,
    marker='o'
)

plt.grid(True)

plt.xlabel(
    "Bit Περικομμένης φάσης (MSB) (P)"
)

plt.ylabel(
    "MSE"
)

plt.title(
    "Σφάλμα περικοπής φάσης\n"
    "MSE - Bit Περικομμένης φάσης"
)

plt.show()


# ************************************************************
# RMS Plot
# ************************************************************

plt.figure(figsize=(8,5))

plt.plot(
    P_values,
    rms_results,
    marker='o'
)

plt.grid(True)

plt.xlabel(
    "Bit Περικομμένης φάσης (MSB) (P)"
)

plt.ylabel(
    "Σφάλμα RMS"
)

plt.title(
    "Σφάλμα περικοπής φάσης\n"
    "RMS Error - Bit Περικομμένης φάσης"
)

plt.show()

# ************************************************************
# SFDR Plot
# ************************************************************

plt.figure(figsize=(8,5))

# Θεωρητικό SFDR
plt.plot(
    P_values,
    sfdr_results,
    marker='o',
    label='Θεωρητικό SFDR (6.02P)'
)

# FFT SFDR
plt.plot(
    P_values,
    sfdr_fft_results,
    marker='s',
    label='FFT SFDR'
)

plt.grid(True)

plt.xlabel(
    "Bit Περικομμένης Φάσης (P)"
)

plt.ylabel(
    "SFDR (dBc)"
)

plt.title(
    "Περικοπή Φάσης\n"
    "Θεωρητικό και FFT SFDR"
)

plt.legend()

plt.show()
