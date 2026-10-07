import numpy as np
from scipy import constants as const
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.ticker as ticker
from matplotlib.lines import Line2D


def plot_trade_space():
    # Baseline ideal-dipole configuration
    B_base = 2.0       # T
    R_base = 0.2      # m

    # Upper radius considered in the preliminary hardware study.
    # This is a packaging/design-space bound, not a physical optimum.
    R_max = 1.15       # m

    # Plot limits
    B_min = 0.005      # T
    B_max = 2.5        # T

    mu0 = const.mu_0

    # Ideal-dipole moment associated with the baseline reference field.
    M_base = 4.0 * np.pi * B_base * R_base**3 / mu0


    # Design space

    R_1d = np.linspace(0.15, R_max, 900)
    B_1d = np.geomspace(B_min, B_max, 900)
    R_grid, B_grid = np.meshgrid(R_1d, B_1d)

    # M = 4*pi*B_ref*R^3/mu0
    M_grid = 4.0 * np.pi * B_grid * R_grid**3 / mu0

    # For fixed particle rigidity in the dipole/Størmer approximation,
    # the characteristic shielding length scales as M^(1/3).
    # Therefore, the corresponding characteristic protected volume scales
    # approximately as M. This is used only as a first-order proxy.
    moment_ratio = M_grid / M_base

    # First-order system-level power proxy:
    # P_proxy ~ M/R.
    #
    # This is intentionally normalized rather than converted to kW,
    # because the coefficient is technology-dependent and has not been
    # established by a detailed REBCO/cryogenic design.
    power_ratio = (M_grid / R_grid) / (M_base / R_base)

    # Candidate region:
    #   - at least baseline magnetic moment
    #   - no greater first-order power proxy than baseline
    candidate = (moment_ratio >= 1.0) & (power_ratio <= 1.0)


    # "Best" point within the stated design-space bound

    # For fixed M = M_base, B scales as R^(-3).
    B_equal_moment = B_base * (R_base / R_max)**3
    power_equal_moment = R_base / R_max

    # Engineering point retained for the subsequent preliminary sizing.
    # 0.02 T provides a modest moment margin relative to the
    # baseline-equivalent 0.016 T point at R = 1 m.
    R_selected = 1
    B_selected = 0.02

    M_selected = 4.0 * np.pi * B_selected * R_selected**3 / mu0
    moment_ratio_selected = M_selected / M_base
    power_ratio_selected = (
        (M_selected / R_selected) / (M_base / R_base)
    )


    # Console output

    print("Baseline configuration")
    print(f"  R_base = {R_base:.3f} m")
    print(f"  B_base = {B_base:.3f} T")
    print(f"  M_base = {M_base:.3e} A m^2")

    # print("\nBaseline-equivalent point at maximum radius")
    # print(f"  R = {R_max:.3f} m")
    # print(f"  B = {B_equal_moment:.4f} T")
    # print(f"  M/M_base = 1.000")
    # print(f"  P_proxy/P_base = {power_equal_moment:.3f}")

    print("\nSelected engineering point")
    print(f"  R = {R_selected:.3f} m")
    print(f"  B = {B_selected:.4f} T")
    print(f"  M/M_base = {moment_ratio_selected:.3f}")
    print(f"  P_proxy/P_base = {power_ratio_selected:.3f}")


    # Figure

    fig, ax = plt.subplots(figsize=(9.5, 7.2))

    # Normalized power-proxy contours
    levels = np.geomspace(0.001, 10.0, 64)
    contour_p = ax.contourf(
        R_grid,
        B_grid,
        power_ratio,
        levels=levels,
        norm=colors.LogNorm(vmin=0.001, vmax=10.0),  # This maps the colors logarithmically
        alpha=0.78,
        extend="both",
    )
    cbar = fig.colorbar(contour_p, ax=ax)
    cbar.set_ticks([0.001, 0.01, 0.1, 1.0, 10.0])

    cbar.ax.yaxis.set_major_formatter(ticker.PercentFormatter(xmax=1.0))
    cbar.set_label(
        r"Normalized power proxy, $P_{\mathrm{proxy}}/P_{\mathrm{base}}$"
    )

    # Baseline-equivalent magnetic moment:
# M/M_base = 1
    ax.contour(
        R_grid,
        B_grid,
        moment_ratio,
        levels=[1.0],
        linewidths=2.0,
        linestyles="--",
        colors="green"
    )
    proxy_line1 = Line2D(
        [0], [0], 
        color="green", 
        linewidth=2.0, 
        linestyle="--", 
        label=r"Iso-Volume"
    )

    # P_proxy/P_base = 1
    ax.contour(
        R_grid,
        B_grid,
        power_ratio,
        levels=[1.0],
        linewidths=2.0,
        linestyles="-.",
        colors="red"
    )
    proxy_line2 = Line2D(
        [0], [0], 
        color="red", 
        linewidth=2.0, 
        linestyle="-.", 
        label=r"Iso-Power"
    )

    # Passa direttamente i proxy creati in un'unica chiamata finale
    ax.legend(handles=[proxy_line1, proxy_line2])

    # Boundary of the candidate region
    # ax.contour(
    #     R_grid,
    #     B_grid,
    #     candidate.astype(float),
    #     levels=[0.5],
    #     linewidths=1.2,
    #     linestyles=":",
    # )

    # Baseline point
    ax.plot(
        R_base,
        B_base,
        marker="o",
        markersize=9,
        markeredgecolor="black",
        markerfacecolor="white",
        label=r"Baseline ($R=0.2~\mathrm{m},\ B=2~\mathrm{T}$)",
    )

    # Baseline-equivalent point at R_max
    # ax.plot(
    #     R_max,
    #     B_equal_moment,
    #     marker="s",
    #     markersize=8,
    #     markeredgecolor="black",
    #     markerfacecolor="white",
    #     label=(
    #         rf"Baseline-equivalent at $R=1.0~\mathrm{{m}}$ "
    #         rf"($B={B_equal_moment:.3f}~\mathrm{{T}}$)"
    #     ),
    # )

    # Selected engineering point
    ax.plot(
        R_selected,
        B_selected,
        marker="*",
        markersize=14,
        markeredgecolor="black",
        markerfacecolor="white",
        label=r"Selected sizing point ($R=1~\mathrm{m},\ B=0.02~\mathrm{T}$)",
    )

    ax.annotate(
        rf"$V/V_{{\mathrm{{base}}}}={moment_ratio_selected**(3/2):.2f}$"
        "\n"
        rf"$P_{{\mathrm{{proxy}}}}/P_{{\mathrm{{base}}}}={power_ratio_selected:.2f}$",
        xy=(R_selected, B_selected),
        xytext=(0.72, 0.050),
        arrowprops=dict(arrowstyle="->", linewidth=1.1),
        fontsize=10,
        ha="left",
        va="bottom",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.90),
    )

    ax.set_xlim(0.15, R_max)
    ax.set_ylim(B_min, B_max)
    ax.set_yscale("log")
    ax.set_xscale("log")

    ax.set_xlabel(r"Characteristic radius, $R$ (m)")
    ax.set_ylabel(r"Reference magnetic field, $B_{\mathrm{ref}}$ (T)")
    ax.set_title("Active-Shielding Magnetic Design Trade Space")

    ax.text(
        0.63,
        0.57,
        "Candidate region",
        transform=ax.transAxes,
        fontsize=10,
        ha="center",
        va="center",
        rotation=-30,
    )

    handles, labels = ax.get_legend_handles_labels()

    # 2. Aggiungi alla lista i tuoi proxy line creati a metà script
    handles.extend([proxy_line1, proxy_line2])

    # 3. Genera l'unica vera legenda finale passando la lista completa
    ax.legend(handles=handles, loc="upper right", fontsize=9, framealpha=0.93)

    plt.tight_layout()
    return fig, ax


if __name__ == "__main__":
    fig, ax = plot_trade_space()
    # output_pdf = Path(__file__).with_name("dipole_trade_space_AIAA.pdf")
    # fig.savefig(output_pdf, bbox_inches="tight")
    plt.show()
