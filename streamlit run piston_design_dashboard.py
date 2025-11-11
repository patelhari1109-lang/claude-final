```python
import streamlit as st
import math

st.set_page_config(page_title="Piston Design Calculator", layout="wide")

st.title("IC Engine Piston Design Calculator")

# Sidebar inputs
st.sidebar.header("Input Parameters")

material = st.sidebar.selectbox("Material", ["Cast Iron", "Aluminium Alloy", "Forged Steel"])

D = st.sidebar.number_input("Cylinder Bore D (mm)", value=100.0)
L = st.sidebar.number_input("Stroke L (mm)", value=125.0)
p = st.sidebar.number_input("Max Gas Pressure p (N/mm²)", value=5.0)
N = st.sidebar.number_input("Speed N (rpm)", value=2000)

# Material properties
if material == "Cast Iron":
    sigma_t_default = 38.0
    k = 46.6
    temp_diff = 220
elif material == "Aluminium Alloy":
    sigma_t_default = 70.0
    k = 174.75
    temp_diff = 75
else:
    sigma_t_default = 80.0
    k = 51.25
    temp_diff = 220

sigma_t = st.sidebar.number_input("σₜ for head (MPa)", value=sigma_t_default)
n_R = st.sidebar.number_input("Number of rings", value=4, min_value=3, max_value=7)
p_m = st.sidebar.number_input("IMEP (N/mm²)", value=0.75)
mech_eff = st.sidebar.number_input("Mechanical efficiency", value=0.8)
m_fuel = st.sidebar.number_input("Fuel consumption (kg/BP/hr)", value=0.15)
HCV = st.sidebar.number_input("HCV (kJ/kg)", value=42000)

p_w = st.sidebar.number_input("Ring pressure pᵥᵥ (N/mm²)", value=0.035)
sigma_t_ring = st.sidebar.number_input("σₜ for ring (MPa)", value=90.0)
p_b_skirt = st.sidebar.number_input("Skirt bearing pressure (N/mm²)", value=0.45)
p_b1_pin = st.sidebar.number_input("Pin bearing pressure (N/mm²)", value=25.0)
sigma_b_pin = st.sidebar.number_input("Pin bending stress (MPa)", value=140.0)

if st.sidebar.button("Calculate"):
    
    st.header("1. Piston Head Thickness")
    
    # Grashof's formula
    t_H_strength = math.sqrt((3 * p * D**2) / (16 * sigma_t))
    st.latex(r"t_H = \sqrt{\frac{3pD^2}{16\sigma_t}}")
    st.write(f"From strength: **t_H = {t_H_strength:.2f} mm**")
    
    # Heat dissipation
    n_strokes = N / 2  # 4-stroke
    A = math.pi * D**2 / 4
    IP = (p_m * (L/1000) * (A/1e6) * n_strokes) / 60  # kW
    BP = IP * mech_eff
    m_fuel_sec = m_fuel / 3600
    H = 0.05 * HCV * m_fuel_sec * BP * 1000  # Watts
    
    t_H_heat = H / (12.56 * k * temp_diff)
    st.latex(r"t_H = \frac{H}{12.56 \cdot k \cdot (T_C - T_E)}")
    st.write(f"Heat flow H = {H:.2f} W")
    st.write(f"From heat: **t_H = {t_H_heat:.2f} mm**")
    
    t_H = max(t_H_strength, t_H_heat)
    st.success(f"**Adopted t_H = {t_H:.2f} mm**")
    
    if t_H > 6:
        st.info(f"Ribs required: thickness {t_H/3:.2f} to {t_H/2:.2f} mm")
    
    st.divider()
    
    # Piston rings
    st.header("2. Piston Rings")
    
    t_1 = math.sqrt((3 * p_w * D) / sigma_t_ring)
    st.latex(r"t_1 = \sqrt{\frac{3p_wD}{\sigma_t}}")
    st.write(f"**Radial thickness t₁ = {t_1:.2f} mm**")
    
    t_2 = 0.7 * t_1
    t_2_empirical = D / (10 * n_R)
    t_2 = max(t_2, t_2_empirical)
    st.latex(r"t_2 = 0.7t_1 \text{ to } t_1")
    st.write(f"**Axial thickness t₂ = {t_2:.2f} mm**")
    
    b_1 = 1.1 * t_H
    b_2 = 0.85 * t_2
    st.write(f"**Top land b₁ = {b_1:.2f} mm**")
    st.write(f"**Other lands b₂ = {b_2:.2f} mm**")
    
    st.divider()
    
    # Piston barrel
    st.header("3. Piston Barrel")
    
    t_3 = 0.03 * D + t_1 + 4.9
    st.latex(r"t_3 = 0.03D + t_1 + 4.9")
    st.write(f"**Max thickness t₃ = {t_3:.2f} mm**")
    
    t_4 = 0.3 * t_3
    st.write(f"**Open end thickness t₄ = {t_4:.2f} mm** (0.25t₃ to 0.35t₃)")
    
    st.divider()
    
    # Piston skirt
    st.header("4. Piston Skirt")
    
    R = 0.1 * (math.pi * D**2 * p) / 4
    st.latex(r"R = 0.1 \times \frac{\pi D^2 p}{4}")
    st.write(f"Side thrust R = {R:.2f} N")
    
    l_skirt = R / (p_b_skirt * D)
    st.latex(r"l = \frac{R}{p_b \times D}")
    st.write(f"**Skirt length l = {l_skirt:.2f} mm**")
    
    length_ring = n_R * t_2 + (n_R - 1) * b_2
    L_total = l_skirt + length_ring + b_1
    st.write(f"**Total piston length L = {L_total:.2f} mm**")
    
    st.divider()
    
    # Piston pin
    st.header("5. Piston Pin")
    
    l_1 = 0.45 * D
    P_gas = (math.pi * D**2 * p) / 4
    
    d_0 = P_gas / (p_b1_pin * l_1)
    st.latex(r"d_0 = \frac{\pi D^2 p}{4 \times p_{b1} \times l_1}")
    st.write(f"**Outside diameter d₀ = {d_0:.2f} mm**")
    
    d_i = 0.6 * d_0
    st.write(f"**Inside diameter dᵢ = {d_i:.2f} mm** (0.6d₀)")
    
    # Bending check
    M = (P_gas * D) / 8
    Z = (math.pi * (d_0**4 - d_i**4)) / (32 * d_0)
    sigma_b_induced = M / Z
    
    st.write(f"Bending moment M = {M:.2f} N-mm")
    st.write(f"Induced stress σb = {sigma_b_induced:.2f} MPa")
    
    if sigma_b_induced <= sigma_b_pin:
        st.success("✅ Pin is SAFE")
    else:
        st.error("❌ Pin UNSAFE - increase diameter")
    
    st.divider()
    
    # Summary
    st.header("Design Summary")
    st.write(f"""
    **Piston Head:** t_H = {t_H:.2f} mm  
    **Rings:** t₁ = {t_1:.2f} mm, t₂ = {t_2:.2f} mm  
    **Barrel:** t₃ = {t_3:.2f} mm, t₄ = {t_4:.2f} mm  
    **Skirt:** l = {l_skirt:.2f} mm  
    **Pin:** d₀ = {d_0:.2f} mm, dᵢ = {d_i:.2f} mm  
    **Total Length:** {L_total:.2f} mm
    """)
```
