import numpy as np
import matplotlib.pyplot as plt
from pysnr.sfdr import sfdr_signal
from scipy.fft import fft


# ************************************************************
# Ideal Sine
# ************************************************************

def ideal_sine(t, freq, amp=1.0):
    return amp * np.sin(2*np.pi*freq*t)


# ************************************************************
# ZOH Reconstruction
# ************************************************************

def zoh_method(t_sample, sampled_values, t_eval):

    idx = np.searchsorted(
        t_sample,
        t_eval,
        side='right'
    ) - 1

    idx = np.clip(
        idx,
        0,
        len(sampled_values)-1
    )

    return sampled_values[idx]


# ************************************************************
# Parameters
# ************************************************************

fsamp = 100e6

fout_list = [1e3,1e4,5e5,1e6,8e6,1e7,125e5,2e7,25e6,3e7,35e6,40e6,45e6,49e6]

samples_per_cycle_list = [16,32,64,128,256,512,1024,2048,4096,8192]
#samples_per_cycle_list = [16]
samples_per_cycle_results = []
# ************************************************************
# Error calculation (SFDR, MSE, RMS)
# ************************************************************
def evaluate_sampling_error(fout):

    samples_per_cycle = fsamp / fout

    # *****************************************
    # Simulate 100 output periods
    # *****************************************

    duration = 100 / fout

    # High resolution time axis
    eval_points = 2**20

    t_true = np.linspace(0,duration,eval_points,endpoint=False)

    ideal = ideal_sine(t_true,fout)

	# *****************************************
	# DDS samples at 100 MHz
	# *****************************************
	
    t_sample = np.arange(0, duration,1/fsamp)
	
    sampled = ideal_sine(t_sample,fout)
	
    # *****************************************
    # ZOH DAC
    # *****************************************
	
    reconstructed = zoh_method(t_sample,sampled, t_true)
	
    # *****************************************
    # FFT Analysis
    # *****************************************
	
    N = len(reconstructed)
    window = np.hanning(N)
	
    fft_result = fft(reconstructed * window)
	
    magnitude = np.abs(fft_result[:N//2])
	
    freqs_fft = np.fft.fftfreq(N,1/(eval_points/duration))[:N//2]
	
    # Fundamental
	
    fund_idx = np.argmax(magnitude)
	
    magnitude_no_fund = magnitude.copy()
	
    magnitude_no_fund[fund_idx] = 0
	
    spur_idx = np.argmax(magnitude_no_fund)
	
    #print()
    #print("Fundamental =", freqs_fft[fund_idx]/1e6, "MHz")
    #print("Largest Spur =", freqs_fft[spur_idx]/1e6, "MHz")
    #print()
	
    # Top 20 peaks
	
    sorted_idx = np.argsort(magnitude)[::-1]
	
    for i in range(20):
	
    	idx = sorted_idx[i]
	
    	#print(
    		#f"{freqs_fft[idx]/1e6:.3f} MHz   "
    		#f"{20*np.log10(magnitude[idx]+1e-15):.2f} dB")
	
    # *****************************************
    # MSE and RMS
    # *****************************************
	
    error = ideal - reconstructed

    mse = np.mean(error**2)
	
    rms_error = np.sqrt(mse)

    # *****************************************
    # Interpolation error
    # *****************************************

    interpolation_error = ((2*np.pi/samples_per_cycle)**2)/8    
    
    # *****************************************
    # SFDR
    # *****************************************
	
    sfdr_db, spur_mag = sfdr_signal(reconstructed,fs=eval_points/duration,msd=5)
	
    return mse, rms_error, sfdr_db, interpolation_error

mse_results_fout = []
rms_results_fout = []
sfdr_results_fout = []
fout_results_samples = []
interp_results = []
samples_per_cycle_results_fout = []

for fout in fout_list:

    samples_per_cycle = fsamp / fout

    mse, rms, sfdr, interp_err = evaluate_sampling_error(fout)

    samples_per_cycle_results_fout.append(samples_per_cycle)
    fout_results_samples.append(fout)
    mse_results_fout.append(mse)
    rms_results_fout.append(rms)
    interp_results.append(interp_err)
    sfdr_results_fout.append(sfdr)

print("\nResults for all fout values")
print("-"*90)

print(
    f"{'Fout (MHz)':>12} "
    f"{'Samples/Cycle':>15} "
    f"{'MSE':>15} "
    f"{'RMS Error':>15} "
    f"{'Interp. Max Error':>18} "
    f"{'SFDR (dBc)':>12}"
)

print("-"*90)

for fout, spc, mse, rms, interp, sfdr in zip(
        fout_results_samples,
        samples_per_cycle_results_fout,
        mse_results_fout,
        rms_results_fout,
        interp_results,
        sfdr_results_fout):

    print(
        f"{fout/1e6:12.4f} "
        f"{spc:15.2f} "
        f"{mse:15.6e} "
        f"{rms:15.6e} "
        f"{interp:18.6e} "
        f"{sfdr:12.2f}"
    )

mse_results_samples = []
rms_results_samples = []
sfdr_results_samples = []
samples_per_cycle_results_samples = []
interp_results_samples = []

for samples in samples_per_cycle_list:

    fout = fsamp / samples

    mse, rms, sfdr, interp = evaluate_sampling_error(fout)

    samples_per_cycle_results_samples.append(samples)
    mse_results_samples.append(mse)
    rms_results_samples.append(rms)
    interp_results_samples.append(interp)
    sfdr_results_samples.append(sfdr)

print("\nResults for different sample numbers")
print("-"*90)

print(
    f"{'Samples/Cycle':>15} "
    f"{'MSE':>15} "
    f"{'RMS Error':>15} "
    f"{'Interp. Max Error':>18} "
    f"{'SFDR (dBc)':>12}"
)

print("-"*90)

for spc, mse, rms, interp, sfdr in zip(
        samples_per_cycle_results_samples,
        mse_results_samples,
        rms_results_samples,
        interp_results_samples,
        sfdr_results_samples):

    print(
        f"{spc:15.2f} "
        f"{mse:15.6e} "
        f"{rms:15.6e} "
        f"{interp:18.6e} "
        f"{sfdr:12.2f}"
    )


# ************************************************************
# Plot
# ************************************************************

plt.figure(figsize=(8,5))

plt.semilogy(
    samples_per_cycle_results_samples,
    rms_results_samples,
    marker='o',
    linewidth=2,
    label='RMS σφάλμα'
)

plt.semilogy(
    samples_per_cycle_results_samples,
    interp_results_samples,
    marker='s',
    linewidth=2,
    label='Θεωρητικό όριο γραμμικής παρεμβολής'
)

plt.grid(True, which='both')

plt.xlabel("Δείγματα ανά περίοδο")

plt.ylabel("Σφάλμα")

plt.title(
    "RMS σφάλμα και θεωρητικό όριο\n"
    "γραμμικής παρεμβολής"
)

plt.legend()

plt.show()

# SFDR
plt.figure(figsize=(8,5))

plt.plot(
    np.array(samples_per_cycle_list),
    sfdr_results_samples,
    marker='o')

plt.grid(True)

plt.xlabel("Αιρθμός δειγμάτων ανά κύκλο")
plt.ylabel("SFDR (dBc)")

plt.title(
    "DDS Σφάλμα δειγματοληψίας")

plt.show()

plt.figure(figsize=(8,5))

plt.plot(
    np.array(fout_list)/1e6,
    sfdr_results_fout,
    marker='o')

plt.grid(True)

plt.xlabel("Συχνότητα εξόδου fout (MHz)")
plt.ylabel("SFDR (dBc)")

plt.title(
    "DDS Σφάλμα δειγματοληψίας\n"
    "fsamp = 100 MHz")

plt.show()

# MSE
plt.figure(figsize=(8,5))

plt.plot(
    np.array(samples_per_cycle_list),
    mse_results_samples,
    marker='o')

plt.grid(True)

plt.xlabel("Αιρθμός δειγμάτων ανά κύκλο")
plt.ylabel("MSE")

plt.title(
    "DDS Σφάλμα δειγματοληψίας")

plt.show()

plt.figure(figsize=(8,5))

plt.plot(
    np.array(fout_list)/1e6,
    mse_results_fout,
    marker='o')

plt.grid(True)

plt.xlabel("Συχνότητα εξόδου fout  (MHz)")
plt.ylabel("MSE")

plt.title(
    "DDS Σφάλμα δειγματοληψίας\n"
    "MSE - Συχνότητα εξόδου fout")

plt.show()

# RMS
plt.figure(figsize=(8,5))

plt.plot(
    np.array(samples_per_cycle_list),
    rms_results_samples,
    marker='o'
)

plt.grid(True)

plt.xlabel("Αιρθμός δειγμάτων ανά κύκλο")
plt.ylabel("RMS Error")

plt.title(
    "DDS Σφάλμα δειγματοληψίας")

plt.show()

plt.figure(figsize=(8,5))

plt.plot(
    np.array(fout_list)/1e6,
    rms_results_fout,
    marker='o'
)

plt.grid(True)

plt.xlabel("Συχνότητα εξόδου fout(MHz)")
plt.ylabel("RMS Error")

plt.title(
    "DDS Σφάλμα δειγματοληψίας\n"
    "RMS Error - Συχνότητα εξόδου fout"
)

plt.show()

# Interpolation error
plt.figure(figsize=(8,5))

plt.semilogy(
    samples_per_cycle_results_samples,
    interp_results_samples,
    marker='o'
)

plt.grid(True, which='both')

plt.xlabel("Δείγματα ανά περίοδο")

plt.ylabel("Μέγιστο θεωρητικό σφάλμα παρεμβολής")

plt.title(
    "Θεωρητικό μέγιστο σφάλμα\n"
    "γραμμικής παρεμβολής"
)

plt.show()
