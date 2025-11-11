import streamlit as st
import math

# Page configuration
st.set_page_config(page_title="Piston Design Dashboard", layout="wide")

# Title and description
st.title("🔧 IC Engine Piston Design Calculator")
st.markdown("""
This application calculates piston design parameters for Internal Combustion (IC) engines 
using standard design formulas from machine design textbooks.
""")

# Sidebar for inputs
st.sidebar.header("📊 Input Parameters")

# Material selection
material = st.sidebar.selectbox(
    "Piston Material",
    ["Grey Cast Iron", "Nickel Cast Iron", "Aluminium Alloy", "Forged Steel"]
)

# Material properties mapping
material_properties = {
    "Grey Cast Iron": {
        "sigma_t": 37.5,  # MPa (35-40)
        "k": 46.6,  # W/m/°C
        "temp_diff": 220,  # °C
        "coefficient_expansion": 0.1e-6,  # m/°C
        "density": 7200  # kg/m³
    },
    "Nickel Cast Iron": {
        "sigma_t": 70,  # MPa (50-90)
        "k": 46.6,  # W/m/°C
        "temp_diff": 220,  # °C
        "coefficient_expansion": 0.1e-6,  # m/°C
        "density": 7200  # kg/m³
    },
    "Aluminium Alloy": {
        "sigma_t": 70,  # MPa (50-90)
        "k": 174.75,  # W/m/°C
        "temp_diff": 75,  # °C
        "coefficient_expansion": 0.24e-6,  # m/°C
        "density": 2700  # kg/m³
    },
    "Forged Steel": {
        "sigma_t": 80,  # MPa (60-100)
        "k": 51.25,  # W/m/°C
        "temp_diff": 220,  # °C
        "coefficient_expansion": 0.1e-6,  # m/°C
        "density": 7850  # kg/m³
    }
}

# Engine parameters
st.sidebar.subheader("Engine Specifications")
D = st.sidebar.number_input("Cylinder Bore (D) [mm]", min_value=50.0, max_value=500.0, value=100.0, step=5.0)
L = st.sidebar.number_input("Stroke Length (L) [mm]", min_value=50.0, max_value=500.0, value=125.0, step=5.0)
p = st.sidebar.number_input("Maximum Gas Pressure (p) [N/mm²]", min_value=1.0, max_value=20.0, value=5.0, step=0.5)
N = st.sidebar.number_input("Engine Speed (N) [rpm]", min_value=500, max_value=5000, value=2000, step=100)

# Advanced parameters
st.sidebar.subheader("Advanced Parameters")
sigma_t = st.sidebar.number_input(
    "Allowable Bending Stress (σₜ) [MPa]", 
    min_value=30.0, 
    max_value=150.0, 
    value=material_properties[material]["sigma_t"], 
    step=5.0
)
n_R = st.sidebar.number_input("Number of Piston Rings", min_value=3, max_value=7, value=5, step=1)

# Heat dissipation parameters
st.sidebar.subheader("Heat Dissipation Parameters")
fuel_type = st.sidebar.selectbox("Fuel Type", ["Diesel", "Petrol"])
HCV = st.sidebar.number_input(
    "Higher Calorific Value (HCV) [kJ/kg]", 
    min_value=30000, 
    max_value=50000, 
    value=45000 if fuel_type == "Diesel" else 47000, 
    step=1000
)
m_fuel = st.sidebar.number_input("Fuel Consumption [kg/BP/hour]", min_value=0.1, max_value=0.3, value=0.15, step=0.01)
mech_eff = st.sidebar.number_input("Mechanical Efficiency [%]", min_value=70.0, max_value=95.0, value=80.0, step=1.0) / 100

# Ring parameters
st.sidebar.subheader("Piston Ring Parameters")
p_w = st.sidebar.number_input("Gas Pressure on Cylinder Wall (pₘ) [N/mm²]", min_value=0.025, max_value=0.042, value=0.035, step=0.001)
sigma_t_ring = st.sidebar.number_input("Allowable Bending Stress for Ring (σₜ) [MPa]", min_value=85.0, max_value=110.0, value=95.0, step=5.0)

# Skirt and pin parameters
st.sidebar.subheader("Skirt & Pin Parameters")
p_b_skirt = st.sidebar.number_input("Bearing Pressure on Skirt [N/mm²]", min_value=0.25, max_value=0.5, value=0.35, step=0.05)
p_b1_pin = st.sidebar.number_input("Bearing Pressure at Pin Bush [N/mm²]", min_value=20.0, max_value=30.0, value=25.0, step=1.0)
sigma_b_pin = st.sidebar.number_input("Allowable Bending Stress for Pin [MPa]", min_value=80.0, max_value=150.0, value=84.0, step=5.0)

# Calculate button
calculate = st.sidebar.button("🔍 Calculate Piston Design", type="primary")

if calculate:
    # Main calculations
    st.header("📐 Design Calculations")
    
    # ========== 1. PISTON HEAD DESIGN ==========
    st.subheader("1️⃣ Piston Head (Crown) Design")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Based on Strength (Grashof's Formula)")
        st.markdown("For a flat circular plate under uniform pressure:")
        st.latex(r"t_H = \sqrt{\frac{3 \cdot p \cdot D^2}{16 \cdot \sigma_t}}")
        
        # From Grashof's formula for flat circular plate fixed at edges
        t_H_strength = math.sqrt((3 * p * D**2) / (16 * sigma_t))
        
        st.markdown(f"**Calculation:**")
        st.latex(rf"t_H = \sqrt{{\frac{{3 \times {p} \times {D}^2}}{{16 \times {sigma_t}}}}}")
        st.success(f"**tₕ (Strength) = {t_H_strength:.2f} mm**")
    
    with col2:
        st.markdown("#### Based on Heat Dissipation")
        st.markdown("For effective heat transfer from combustion:")
        st.latex(r"t_H = \frac{H}{12.56 \cdot k \cdot (T_C - T_E)}")
        
        # Calculate brake power
        # BP = (p_m × L × A × N) / (60 × 2 × η_m × 1000) for 4-stroke
        p_m = 0.75  # Assumed IMEP in N/mm²
        A = (math.pi * D**2) / 4  # mm²
        BP_per_cylinder = (p_m * (L/1000) * (A/1e6) * N) / (60 * 2 * 1000)  # kW
        
        # Heat flowing through piston head
        C = 0.05  # Constant for heat absorbed by piston
        m_fuel_per_sec = m_fuel / 3600  # kg/BP/s
        H = C * HCV * m_fuel_per_sec * BP_per_cylinder * 1000  # Watts
        
        # Temperature difference based on material
        k = material_properties[material]["k"]
        temp_diff = material_properties[material]["temp_diff"]
        
        # From heat transfer equation for circular plate
        t_H_heat = H / (12.56 * k * temp_diff) if (k * temp_diff) > 0 else 0
        
        st.markdown(f"**Heat Flow (H):** {H:.2f} W")
        st.markdown(f"**Heat Conductivity (k):** {k} W/m/°C")
        st.markdown(f"**Temp. Difference (ΔT):** {temp_diff}°C")
        st.latex(rf"t_H = \frac{{{H:.2f}}}{{12.56 \times {k} \times {temp_diff}}}")
        st.success(f"**tₕ (Heat) = {t_H_heat:.2f} mm**")
    
    # Select larger value
    t_H = max(t_H_strength, t_H_heat)
    st.info(f"✅ **Adopted Piston Head Thickness: tₕ = {t_H:.2f} mm** (larger value selected)")
    
    # Ribs requirement
    if t_H > 6:
        st.warning(f"⚠️ Since tₕ > 6 mm, ribs should be provided. Rib thickness: {t_H/3:.2f} to {t_H/2:.2f} mm")
    
    st.divider()
    
    # ========== 2. PISTON RINGS DESIGN ==========
    st.subheader("2️⃣ Piston Rings Design")
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("#### Radial Thickness (t₁)")
        st.latex(r"t_1 = \sqrt{\frac{3 \cdot p_w \cdot D}{\sigma_t}}")
        
        # From bending stress consideration in ring
        t_1 = math.sqrt((3 * p_w * D) / sigma_t_ring)
        
        st.markdown(f"**Calculation:**")
        st.latex(rf"t_1 = \sqrt{{\frac{{3 \times {p_w} \times {D}}}{{{sigma_t_ring}}}}}")
        st.success(f"**t₁ = {t_1:.2f} mm**")
        
        # Ring gap
        gap_free = 3.5 * t_1
        gap_in_cylinder_min = 0.002 * D
        gap_in_cylinder_max = 0.004 * D
        
        st.markdown(f"**Gap (free ends):** {gap_free:.2f} mm")
        st.markdown(f"**Gap (in cylinder):** {gap_in_cylinder_min:.2f} - {gap_in_cylinder_max:.2f} mm")
    
    with col4:
        st.markdown("#### Axial Thickness (t₂)")
        st.latex(r"t_2 = 0.7 \cdot t_1 \text{ to } 1.0 \cdot t_1")
        
        t_2_min = 0.7 * t_1
        t_2_max = 1.0 * t_1
        
        st.markdown(f"**Range:** {t_2_min:.2f} - {t_2_max:.2f} mm")
        
        # Empirical relation check
        t_2_empirical = D / (10 * n_R)
        st.markdown(f"**Empirical check:** t₂ = D/(10×nᵣ) = {t_2_empirical:.2f} mm")
        
        t_2 = max(t_2_min, t_2_empirical)
        st.success(f"**Adopted t₂ = {t_2:.2f} mm**")
    
    # Ring lands
    st.markdown("#### Ring Land Dimensions")
    b_1 = 1.1 * t_H  # Width of top land
    b_2 = 0.85 * t_2  # Width of other ring lands
    
    col5, col6 = st.columns(2)
    with col5:
        st.latex(r"b_1 = t_H \text{ to } 1.2 \cdot t_H")
        st.info(f"**Top Land Width (b₁) = {b_1:.2f} mm**")
    
    with col6:
        st.latex(r"b_2 = 0.75 \cdot t_2 \text{ to } t_2")
        st.info(f"**Other Land Width (b₂) = {b_2:.2f} mm**")
    
    # Radial depth of groove
    b_groove = t_1 + 0.4
    st.markdown(f"**Radial Depth of Ring Groove:** b = t₁ + 0.4 = {b_groove:.2f} mm")
    
    st.divider()
    
    # ========== 3. PISTON BARREL DESIGN ==========
    st.subheader("3️⃣ Piston Barrel Design")
    
    st.markdown("#### Maximum Wall Thickness (t₃)")
    st.latex(r"t_3 = 0.03 \cdot D + t_1 + 4.9")
    
    # From empirical relation for barrel thickness
    t_3 = 0.03 * D + t_1 + 4.9
    
    st.markdown(f"**Calculation:**")
    st.latex(rf"t_3 = 0.03 \times {D} + {t_1:.2f} + 4.9")
    st.success(f"**t₃ = {t_3:.2f} mm**")
    
    # Wall thickness at open end
    t_4_min = 0.25 * t_3
    t_4_max = 0.35 * t_3
    t_4 = 0.3 * t_3
    
    st.markdown("#### Wall Thickness at Open End (t₄)")
    st.latex(r"t_4 = 0.25 \cdot t_3 \text{ to } 0.35 \cdot t_3")
    st.info(f"**t₄ Range: {t_4_min:.2f} - {t_4_max:.2f} mm** (Adopted: {t_4:.2f} mm)")
    
    st.divider()
    
    # ========== 4. PISTON SKIRT DESIGN ==========
    st.subheader("4️⃣ Piston Skirt Design")
    
    st.markdown("#### Skirt Length Calculation")
    
    # Maximum gas load on piston
    P = (math.pi * D**2 * p) / 4
    
    # Maximum side thrust (1/10 of gas load)
    R = P / 10
    
    st.latex(r"P = \frac{\pi \cdot D^2 \cdot p}{4}")
    st.markdown(f"**Gas Load:** P = {P:.2f} N")
    
    st.latex(r"R = \frac{P}{10}")
    st.markdown(f"**Side Thrust:** R = {R:.2f} N")
    
    # Length of skirt from bearing pressure
    st.latex(r"l = \frac{R}{p_b \cdot D}")
    
    l_skirt_calculated = R / (p_b_skirt * D)
    
    st.markdown(f"**Calculated:** l = {l_skirt_calculated:.2f} mm")
    
    # Empirical range check
    l_skirt_min = 0.65 * D
    l_skirt_max = 0.8 * D
    
    st.latex(r"l = 0.65 \cdot D \text{ to } 0.8 \cdot D")
    st.markdown(f"**Empirical Range:** {l_skirt_min:.2f} - {l_skirt_max:.2f} mm")
    
    l_skirt = max(l_skirt_calculated, l_skirt_min)
    l_skirt = min(l_skirt, l_skirt_max)
    
    st.success(f"**Adopted Skirt Length: l = {l_skirt:.2f} mm**")
    
    # Total piston length
    length_ring_section = n_R * t_2 + (n_R) * b_2
    L_total = l_skirt + length_ring_section + b_1
    
    st.markdown(f"**Ring Section Length:** {length_ring_section:.2f} mm")
    st.info(f"**Total Piston Length: L = {L_total:.2f} mm** (Range: {D:.2f} - {1.5*D:.2f} mm)")
    
    st.divider()
    
    # ========== 5. PISTON PIN DESIGN ==========
    st.subheader("5️⃣ Piston Pin (Gudgeon Pin) Design")
    
    st.markdown("#### Outside Diameter (d₀)")
    
    # Length in connecting rod bushing
    l_1 = 0.45 * D
    
    st.latex(r"l_1 = 0.45 \cdot D")
    st.markdown(f"**Pin Length in Bush:** l₁ = {l_1:.2f} mm")
    
    # Equating gas load to bearing load
    st.latex(r"\frac{\pi \cdot D^2 \cdot p}{4} = p_{b1} \cdot d_0 \cdot l_1")
    
    st.latex(r"d_0 = \frac{\pi \cdot D^2 \cdot p}{4 \cdot p_{b1} \cdot l_1}")
    
    d_0 = (math.pi * D**2 * p) / (4 * p_b1_pin * l_1)
    
    st.markdown(f"**Calculation:**")
    st.latex(rf"d_0 = \frac{{\pi \times {D}^2 \times {p}}}{{4 \times {p_b1_pin} \times {l_1:.2f}}}")
    st.success(f"**Pin Outside Diameter: d₀ = {d_0:.2f} mm**")
    
    # Inside diameter (assumed)
    d_i = 0.6 * d_0
    st.markdown(f"**Assumed Inside Diameter:** dᵢ = 0.6 × d₀ = {d_i:.2f} mm")
    
    # Bending stress check
    st.markdown("#### Bending Stress Verification")
    
    # Maximum bending moment
    M = (P * D) / 8
    
    st.latex(r"M = \frac{P \cdot D}{8}")
    st.markdown(f"**Bending Moment:** M = {M:.2f} N·mm")
    
    # Section modulus
    Z = (math.pi * (d_0**4 - d_i**4)) / (32 * d_0)
    
    st.latex(r"Z = \frac{\pi \cdot (d_0^4 - d_i^4)}{32 \cdot d_0}")
    st.markdown(f"**Section Modulus:** Z = {Z:.2f} mm³")
    
    # Induced bending stress
    sigma_b_induced = M / Z
    
    st.latex(r"\sigma_b = \frac{M}{Z}")
    st.markdown(f"**Induced Bending Stress:** σb = {sigma_b_induced:.2f} MPa")
    st.markdown(f"**Allowable Bending Stress:** σb(allow) = {sigma_b_pin:.2f} MPa")
    
    if sigma_b_induced <= sigma_b_pin:
        st.success("✅ Pin design is SAFE in bending")
    else:
        st.error("❌ Pin design FAILS - increase diameter or use stronger material")
    
    # Boss dimensions
    d_boss_mean = 1.5 * d_0  # For aluminium
    st.markdown(f"**Mean Diameter of Piston Bosses:** {d_boss_mean:.2f} mm")
    
    st.divider()
    
    # ========== 6. DESIGN SUMMARY ==========
    st.header("📋 Design Summary")
    
    summary_col1, summary_col2, summary_col3 = st.columns(3)
    
    with summary_col1:
        st.markdown("### Piston Head")
        st.markdown(f"- **Thickness (tₕ):** {t_H:.2f} mm")
        st.markdown(f"- **Top Land (b₁):** {b_1:.2f} mm")
        st.markdown(f"- **Material:** {material}")
        
        st.markdown("### Piston Rings")
        st.markdown(f"- **Number of Rings:** {n_R}")
        st.markdown(f"- **Radial Thickness (t₁):** {t_1:.2f} mm")
        st.markdown(f"- **Axial Thickness (t₂):** {t_2:.2f} mm")
        st.markdown(f"- **Other Lands (b₂):** {b_2:.2f} mm")
    
    with summary_col2:
        st.markdown("### Piston Barrel")
        st.markdown(f"- **Max Thickness (t₃):** {t_3:.2f} mm")
        st.markdown(f"- **Open End Thickness (t₄):** {t_4:.2f} mm")
        st.markdown(f"- **Groove Depth:** {b_groove:.2f} mm")
        
        st.markdown("### Piston Skirt")
        st.markdown(f"- **Length (l):** {l_skirt:.2f} mm")
        st.markdown(f"- **Total Piston Length:** {L_total:.2f} mm")
        st.markdown(f"- **Bearing Pressure:** {p_b_skirt} N/mm²")
    
    with summary_col3:
        st.markdown("### Piston Pin")
        st.markdown(f"- **Outside Diameter (d₀):** {d_0:.2f} mm")
        st.markdown(f"- **Inside Diameter (dᵢ):** {d_i:.2f} mm")
        st.markdown(f"- **Length in Bush (l₁):** {l_1:.2f} mm")
        st.markdown(f"- **Boss Mean Dia.:** {d_boss_mean:.2f} mm")
        st.markdown(f"- **Bending Stress:** {sigma_b_induced:.2f} MPa")
    
    # Download summary
    st.divider()
    st.markdown("### 📥 Export Summary")
    
    summary_text = f"""
PISTON DESIGN SUMMARY
=====================
Engine: {D} mm bore × {L} mm stroke, {N} rpm
Material: {material}
Max Gas Pressure: {p} N/mm²

PISTON HEAD
-----------
Thickness (tH): {t_H:.2f} mm
Top Land (b1): {b_1:.2f} mm

PISTON RINGS ({n_R} rings)
------------
Radial Thickness (t1): {t_1:.2f} mm
Axial Thickness (t2): {t_2:.2f} mm
Other Lands (b2): {b_2:.2f} mm
Groove Depth: {b_groove:.2f} mm

PISTON BARREL
-------------
Max Thickness (t3): {t_3:.2f} mm
Open End Thickness (t4): {t_4:.2f} mm

PISTON SKIRT
------------
Length: {l_skirt:.2f} mm
Total Piston Length: {L_total:.2f} mm

PISTON PIN
----------
Outside Diameter (d0): {d_0:.2f} mm
Inside Diameter (di): {d_i:.2f} mm
Length in Bush (l1): {l_1:.2f} mm
Boss Mean Diameter: {d_boss_mean:.2f} mm
Induced Bending Stress: {sigma_b_induced:.2f} MPa
Allowable Bending Stress: {sigma_b_pin:.2f} MPa
Status: {"SAFE" if sigma_b_induced <= sigma_b_pin else "UNSAFE"}
"""
    
    st.download_button(
        label="📄 Download Design Summary",
        data=summary_text,
        file_name=f"piston_design_{D}mm_bore.txt",
        mime="text/plain"
    )

else:
    st.info("👈 Please enter the required parameters in the sidebar and click 'Calculate Piston Design' to begin.")
    
    # Show example
    st.markdown("### Example Parameters")
    st.markdown("""
    Try these values for a typical IC engine:
    - **Cylinder Bore:** 100 mm
    - **Stroke:** 125 mm
    - **Max Gas Pressure:** 5 N/mm²
    - **Engine Speed:** 2000 rpm
    - **Material:** Cast Iron or Aluminium Alloy
    - **Number of Rings:** 5
    """)

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>Piston Design Calculator | Based on Standard Machine Design Formulas</p>
    <p style='font-size: 0.8em;'>Formulas reference: Grashof's formula, heat dissipation equations, and empirical relations for IC engines</p>
</div>
""", unsafe_allow_html=True)
