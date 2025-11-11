import React, { useState, useMemo } from 'react';
import { Calculator, Settings, FileText, AlertCircle, CheckCircle } from 'lucide-react';

const PistonDesignDashboard = () => {
  // State for all input parameters
  const [inputs, setInputs] = useState({
    // Basic engine parameters
    cylinderBore: 100, // mm
    stroke: 125, // mm
    maxGasPressure: 5, // N/mm²
    imep: 0.75, // N/mm²
    speed: 2000, // rpm
    mechEfficiency: 80, // %
    fuelConsumption: 0.15, // kg/BP/h
    hcv: 42000, // kJ/kg
    
    // Material properties
    pistonMaterial: 'cast_iron',
    bendingStress: 37.5, // MPa (default for cast iron)
    heatConductivity: 46.6, // W/m/°C (cast iron)
    tempDifference: 220, // °C (cast iron)
    
    // Ring parameters
    numRings: 4,
    wallPressure: 0.035, // N/mm²
    ringBendingStress: 97.5, // MPa
    
    // Bearing parameters
    bearingPressureSkirt: 0.35, // N/mm² (medium speed)
    bearingPressurePin: 25, // N/mm²
    pinBendingStress: 84, // MPa (case hardened carbon steel)
  });

  const handleInputChange = (field, value) => {
    setInputs(prev => ({ ...prev, [field]: parseFloat(value) || 0 }));
  };

  const handleMaterialChange = (material) => {
    const materialProps = {
      cast_iron: { bendingStress: 37.5, heatConductivity: 46.6, tempDifference: 220 },
      nickel_cast_iron: { bendingStress: 70, heatConductivity: 46.6, tempDifference: 220 },
      aluminium_alloy: { bendingStress: 70, heatConductivity: 174.75, tempDifference: 75 },
      forged_steel: { bendingStress: 80, heatConductivity: 51.25, tempDifference: 220 },
    };
    
    setInputs(prev => ({
      ...prev,
      pistonMaterial: material,
      ...materialProps[material]
    }));
  };

  // All calculations using useMemo for performance
  const calculations = useMemo(() => {
    const D = inputs.cylinderBore;
    const p = inputs.maxGasPressure;
    const σt = inputs.bendingStress;
    const k = inputs.heatConductivity;
    const ΔT = inputs.tempDifference;
    const nR = inputs.numRings;
    const pw = inputs.wallPressure;
    const σt_ring = inputs.ringBendingStress;
    const pb_skirt = inputs.bearingPressureSkirt;
    const pb1 = inputs.bearingPressurePin;
    const σb = inputs.pinBendingStress;
    
    // 1. PISTON HEAD THICKNESS - Strength consideration (Grashoff's formula)
    const tH_strength = Math.sqrt((3 * p * D * D) / (16 * σt));
    
    // 2. PISTON HEAD THICKNESS - Heat dissipation consideration
    const m = inputs.fuelConsumption / 3600; // kg/BP/s
    const BP_per_cylinder = (inputs.imep * Math.PI * D * D * inputs.stroke * inputs.speed) / 
                            (4 * 1000000 * 60 * 2); // kW (4-stroke)
    const H = 0.05 * inputs.hcv * m * BP_per_cylinder; // kW
    const tH_heat = (H * 1000) / (12.56 * k * ΔT);
    
    const tH = Math.max(tH_strength, tH_heat);
    const needsRibs = tH > 6;
    
    // 3. PISTON RINGS
    const t1 = Math.sqrt((3 * pw * D) / σt_ring); // Radial thickness
    const t2_calc = 0.85 * t1; // Axial thickness (0.7 to 1.0 times t1)
    const t2_empirical = D / (10 * nR);
    const t2 = Math.max(t2_calc, t2_empirical);
    
    const b1 = 1.1 * tH; // Top land width (tH to 1.2*tH)
    const b2 = 0.9 * t2; // Other ring lands (0.75*t2 to t2)
    const ringGap_free = 3.75 * t1; // Gap when free (3.5 to 4 times t1)
    const ringGap_fitted = 0.003 * D; // Gap when fitted (0.002D to 0.004D)
    
    // 4. PISTON BARREL
    const b_groove = t1 + 0.4; // Radial depth of ring groove
    const t3 = 0.03 * D + t1 + 4.9; // Maximum barrel thickness
    const t4 = 0.3 * t3; // Wall thickness at open end (0.25 to 0.35 times t3)
    
    // 5. PISTON SKIRT
    const P_gas = (Math.PI * D * D * p) / 4; // Maximum gas load
    const R_thrust = P_gas / 10; // Side thrust
    const l_skirt = (0.1 * Math.PI * D * D * p) / (4 * pb_skirt * D);
    const l_skirt_practical = 0.725 * D; // 0.65 to 0.8 times D
    const l_skirt_final = Math.max(l_skirt, l_skirt_practical);
    
    const ringSection = (nR - 1) * b2 + b1 + nR * t2;
    const L_total = l_skirt_final + ringSection + b1;
    
    // 6. PISTON PIN
    const l1 = 0.45 * D; // Length in connecting rod bush
    const d0 = Math.sqrt((Math.PI * D * D * p) / (4 * pb1 * l1));
    const di = 0.6 * d0; // Inside diameter
    
    const l2 = D - l1; // Length between supports
    const M_pin = (P_gas * D) / 8; // Maximum bending moment
    const Z_pin = (Math.PI / 32) * (Math.pow(d0, 4) - Math.pow(di, 4)) / d0;
    const σb_induced = M_pin / Z_pin;
    const pinSafe = σb_induced <= σb;
    
    return {
      tH_strength,
      tH_heat,
      tH,
      needsRibs,
      H,
      BP_per_cylinder,
      t1,
      t2,
      t2_calc,
      t2_empirical,
      b1,
      b2,
      ringGap_free,
      ringGap_fitted,
      b_groove,
      t3,
      t4,
      P_gas,
      R_thrust,
      l_skirt,
      l_skirt_practical,
      l_skirt_final,
      ringSection,
      L_total,
      l1,
      d0,
      di,
      l2,
      M_pin,
      Z_pin,
      σb_induced,
      pinSafe
    };
  }, [inputs]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-800 text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-center gap-3">
            <Calculator className="w-10 h-10" />
            <div>
              <h1 className="text-3xl font-bold">IC Engine Piston Design Dashboard</h1>
              <p className="text-blue-100 mt-1">Comprehensive design calculations based on Machine Design principles</p>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Sidebar - Input Parameters */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-xl shadow-lg p-6 sticky top-6">
              <div className="flex items-center gap-2 mb-6">
                <Settings className="w-6 h-6 text-blue-600" />
                <h2 className="text-xl font-bold text-gray-800">Input Parameters</h2>
              </div>

              <div className="space-y-4 max-h-[calc(100vh-200px)] overflow-y-auto pr-2">
                {/* Engine Parameters */}
                <div className="border-b pb-4">
                  <h3 className="font-semibold text-sm text-gray-700 mb-3">Engine Specifications</h3>
                  
                  <label className="block text-xs font-medium text-gray-600 mb-1">
                    Cylinder Bore (mm)
                  </label>
                  <input
                    type="number"
                    value={inputs.cylinderBore}
                    onChange={(e) => handleInputChange('cylinderBore', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />

                  <label className="block text-xs font-medium text-gray-600 mb-1 mt-3">
                    Stroke (mm)
                  </label>
                  <input
                    type="number"
                    value={inputs.stroke}
                    onChange={(e) => handleInputChange('stroke', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />

                  <label className="block text-xs font-medium text-gray-600 mb-1 mt-3">
                    Max Gas Pressure (N/mm²)
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    value={inputs.maxGasPressure}
                    onChange={(e) => handleInputChange('maxGasPressure', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />

                  <label className="block text-xs font-medium text-gray-600 mb-1 mt-3">
                    IMEP (N/mm²)
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    value={inputs.imep}
                    onChange={(e) => handleInputChange('imep', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />

                  <label className="block text-xs font-medium text-gray-600 mb-1 mt-3">
                    Speed (rpm)
                  </label>
                  <input
                    type="number"
                    value={inputs.speed}
                    onChange={(e) => handleInputChange('speed', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />

                  <label className="block text-xs font-medium text-gray-600 mb-1 mt-3">
                    Mechanical Efficiency (%)
                  </label>
                  <input
                    type="number"
                    value={inputs.mechEfficiency}
                    onChange={(e) => handleInputChange('mechEfficiency', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />

                  <label className="block text-xs font-medium text-gray-600 mb-1 mt-3">
                    Fuel Consumption (kg/BP/h)
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    value={inputs.fuelConsumption}
                    onChange={(e) => handleInputChange('fuelConsumption', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />

                  <label className="block text-xs font-medium text-gray-600 mb-1 mt-3">
                    HCV (kJ/kg)
                  </label>
                  <input
                    type="number"
                    value={inputs.hcv}
                    onChange={(e) => handleInputChange('hcv', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                {/* Material Selection */}
                <div className="border-b pb-4">
                  <h3 className="font-semibold text-sm text-gray-700 mb-3">Material Selection</h3>
                  
                  <label className="block text-xs font-medium text-gray-600 mb-1">
                    Piston Material
                  </label>
                  <select
                    value={inputs.pistonMaterial}
                    onChange={(e) => handleMaterialChange(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="cast_iron">Cast Iron</option>
                    <option value="nickel_cast_iron">Nickel Cast Iron</option>
                    <option value="aluminium_alloy">Aluminium Alloy</option>
                    <option value="forged_steel">Forged Steel</option>
                  </select>

                  <label className="block text-xs font-medium text-gray-600 mb-1 mt-3">
                    Bending Stress (MPa)
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    value={inputs.bendingStress}
                    onChange={(e) => handleInputChange('bendingStress', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                {/* Ring Parameters */}
                <div className="border-b pb-4">
                  <h3 className="font-semibold text-sm text-gray-700 mb-3">Ring Parameters</h3>
                  
                  <label className="block text-xs font-medium text-gray-600 mb-1">
                    Number of Rings
                  </label>
                  <input
                    type="number"
                    value={inputs.numRings}
                    onChange={(e) => handleInputChange('numRings', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />

                  <label className="block text-xs font-medium text-gray-600 mb-1 mt-3">
                    Wall Pressure (N/mm²)
                  </label>
                  <input
                    type="number"
                    step="0.001"
                    value={inputs.wallPressure}
                    onChange={(e) => handleInputChange('wallPressure', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />

                  <label className="block text-xs font-medium text-gray-600 mb-1 mt-3">
                    Ring Bending Stress (MPa)
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    value={inputs.ringBendingStress}
                    onChange={(e) => handleInputChange('ringBendingStress', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                {/* Bearing Parameters */}
                <div>
                  <h3 className="font-semibold text-sm text-gray-700 mb-3">Bearing Parameters</h3>
                  
                  <label className="block text-xs font-medium text-gray-600 mb-1">
                    Skirt Bearing Pressure (N/mm²)
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    value={inputs.bearingPressureSkirt}
                    onChange={(e) => handleInputChange('bearingPressureSkirt', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />

                  <label className="block text-xs font-medium text-gray-600 mb-1 mt-3">
                    Pin Bearing Pressure (N/mm²)
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    value={inputs.bearingPressurePin}
                    onChange={(e) => handleInputChange('bearingPressurePin', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />

                  <label className="block text-xs font-medium text-gray-600 mb-1 mt-3">
                    Pin Bending Stress (MPa)
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    value={inputs.pinBendingStress}
                    onChange={(e) => handleInputChange('pinBendingStress', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Main Content - Calculations */}
          <div className="lg:col-span-3 space-y-6">
            {/* 1. PISTON HEAD DESIGN */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-2xl font-bold text-gray-800 mb-4 flex items-center gap-2">
                <FileText className="w-6 h-6 text-blue-600" />
                1. Piston Head (Crown) Design
              </h2>

              <div className="space-y-4">
                <div className="bg-blue-50 border-l-4 border-blue-600 p-4 rounded">
                  <h3 className="font-semibold text-gray-800 mb-2">A. Strength Consideration (Grashoff's Formula)</h3>
                  <p className="text-sm text-gray-600 mb-3">
                    The piston head is treated as a flat circular plate fixed at edges under uniform gas pressure.
                  </p>
                  
                  <div className="bg-white p-3 rounded border border-blue-200 mb-3">
                    <div className="text-sm font-mono text-center">
                      t<sub>H</sub> = √[(3 × p × D²) / (16 × σ<sub>t</sub>)]
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="font-medium">p =</span> {inputs.maxGasPressure} N/mm²
                    </div>
                    <div>
                      <span className="font-medium">D =</span> {inputs.cylinderBore} mm
                    </div>
                    <div>
                      <span className="font-medium">σ<sub>t</sub> =</span> {inputs.bendingStress} MPa
                    </div>
                    <div className="col-span-2 bg-green-50 p-2 rounded border border-green-300">
                      <span className="font-bold">t<sub>H</sub> (strength) =</span> {calculations.tH_strength.toFixed(2)} mm
                    </div>
                  </div>
                </div>

                <div className="bg-orange-50 border-l-4 border-orange-600 p-4 rounded">
                  <h3 className="font-semibold text-gray-800 mb-2">B. Heat Dissipation Consideration</h3>
                  <p className="text-sm text-gray-600 mb-3">
                    Ensures adequate heat transfer from combustion to cylinder walls.
                  </p>
                  
                  <div className="bg-white p-3 rounded border border-orange-200 mb-3">
                    <div className="text-sm font-mono text-center mb-2">
                      H = 0.05 × HCV × m × BP
                    </div>
                    <div className="text-sm font-mono text-center">
                      t<sub>H</sub> = H / [12.56 × k × (T<sub>C</sub> - T<sub>E</sub>)]
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="font-medium">BP/cylinder =</span> {calculations.BP_per_cylinder.toFixed(2)} kW
                    </div>
                    <div>
                      <span className="font-medium">H =</span> {calculations.H.toFixed(3)} kW
                    </div>
                    <div>
                      <span className="font-medium">k =</span> {inputs.heatConductivity} W/m/°C
                    </div>
                    <div>
                      <span className="font-medium">ΔT =</span> {inputs.tempDifference} °C
                    </div>
                    <div className="col-span-2 bg-green-50 p-2 rounded border border-green-300">
                      <span className="font-bold">t<sub>H</sub> (heat) =</span> {calculations.tH_heat.toFixed(2)} mm
                    </div>
                  </div>
                </div>

                <div className="bg-gradient-to-r from-green-500 to-green-600 text-white p-4 rounded-lg">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-bold text-lg mb-1">Final Piston Head Thickness</h3>
                      <p className="text-sm text-green-100">Maximum of strength and heat considerations</p>
                    </div>
                    <div className="text-3xl font-bold">
                      {calculations.tH.toFixed(2)} mm
                    </div>
                  </div>
                  
                  {calculations.needsRibs && (
                    <div className="mt-3 bg-yellow-500 text-yellow-900 p-2 rounded flex items-center gap-2">
                      <AlertCircle className="w-5 h-5" />
                      <span className="text-sm font-medium">
                        Ribs required (t<sub>H</sub> &gt; 6 mm). Use ribs with thickness = t<sub>H</sub>/3 to t<sub>H</sub>/2
                      </span>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* 2. PISTON RINGS */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-2xl font-bold text-gray-800 mb-4 flex items-center gap-2">
                <FileText className="w-6 h-6 text-blue-600" />
                2. Piston Rings Design
              </h2>

              <div className="space-y-4">
                <div className="bg-purple-50 border-l-4 border-purple-600 p-4 rounded">
                  <h3 className="font-semibold text-gray-800 mb-2">Ring Dimensions</h3>
                  
                  <div className="bg-white p-3 rounded border border-purple-200 mb-3">
                    <div className="text-sm font-mono text-center mb-2">
                      t<sub>1</sub> = √[(3 × p<sub>w</sub> × D) / σ<sub>t</sub>] (Radial thickness)
                    </div>
                    <div className="text-sm font-mono text-center mb-2">
                      t<sub>2</sub> = 0.85 × t<sub>1</sub> or D / (10 × n<sub>R</sub>) (Axial thickness)
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div className="bg-green-50 p-2 rounded">
                      <span className="font-bold">Radial thickness (t<sub>1</sub>) =</span> {calculations.t1.toFixed(2)} mm
                    </div>
                    <div className="bg-green-50 p-2 rounded">
                      <span className="font-bold">Axial thickness (t<sub>2</sub>) =</span> {calculations.t2.toFixed(2)} mm
                    </div>
                    <div>
                      <span className="font-medium">From formula:</span> {calculations.t2_calc.toFixed(2)} mm
                    </div>
                    <div>
                      <span className="font-medium">Empirical:</span> {calculations.t2_empirical.toFixed(2)} mm
                    </div>
                  </div>
                </div>

                <div className="bg-indigo-50 border-l-4 border-indigo-600 p-4 rounded">
                  <h3 className="font-semibold text-gray-800 mb-2">Ring Lands and Gaps</h3>
                  
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div className="bg-white p-3 rounded border">
                      <div className="font-medium text-gray-600 mb-1">Top Land Width (b<sub>1</sub>)</div>
                      <div className="text-lg font-bold text-indigo-600">{calculations.b1.toFixed(2)} mm</div>
                      <div className="text-xs text-gray-500 mt-1">= 1.1 × t<sub>H</sub></div>
                    </div>
                    <div className="bg-white p-3 rounded border">
                      <div className="font-medium text-gray-600 mb-1">Other Lands Width (b<sub>2</sub>)</div>
                      <div className="text-lg font-bold text-indigo-600">{calculations.b2.toFixed(2)} mm</div>
                      <div className="text-xs text-gray-500 mt-1">= 0.9 × t<sub>2</sub></div>
                    </div>
                    <div className="bg-white p-3 rounded border">
                      <div className="font-medium text-gray-600 mb-1">Gap (Free Ends)</div>
                      <div className="text-lg font-bold text-indigo-600">{calculations.ringGap_free.toFixed(2)} mm</div>
                      <div className="text-xs text-gray-500 mt-1">= 3.75 × t<sub>1</sub></div>
                    </div>
                    <div className="bg-white p-3 rounded border">
                      <div className="font-medium text-gray-600 mb-1">Gap (Fitted)</div>
                      <div className="text-lg font-bold text-indigo-600">{calculations.ringGap_fitted.toFixed(2)} mm</div>
                      <div className="text-xs text-gray-500 mt-1">= 0.003 × D</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* 3. PISTON BARREL */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-2xl font-bold text-gray-800 mb-4 flex items-center gap-2">
                <FileText className="w-6 h-6 text-blue-600" />
                3. Piston Barrel Design
              </h2>

              <div className="bg-cyan-50 border-l-4 border-cyan-600 p-4 rounded">
                <div className="bg-white p-3 rounded border border-cyan-200 mb-3">
                  <div className="text-sm font-mono text-center mb-2">
                    t<sub>3</sub> = 0.03 × D + t<sub>1</sub> + 4.9 (Maximum barrel thickness)
                  </div>
                  <div className="text-sm font-mono text-center">
                    t<sub>4</sub> = 0.3 × t<sub>3</sub> (Wall thickness at open end)
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div className="bg-white p-3 rounded border">
                    <div className="font-medium text-gray-600 mb-1">Ring Groove Depth (b)</div>
                    <div className="text-lg font-bold text-cyan-600">{calculations.b_groove.toFixed(2)} mm</div>
                    <div className="text-xs text-gray-500 mt-1">= t<sub>1</sub> + 0.4</div>
                  </div>
                  <div className="bg-white p-3 rounded border">
                    <div className="font-medium text-gray-600 mb-1">Max Barrel Thickness (t<sub>3</sub>)</div>
                    <div className="text-lg font-bold text-cyan-600">{calculations.t3.toFixed(2)} mm</div>
                  </div>
                  <div className="bg-white p-3 rounded border col-span-2">
                    <div className="font-medium text-gray-600 mb-1">Wall Thickness at Open End (t<sub>4</sub>)</div>
                    <div className="text-lg font-bold text-cyan-600">{calculations.t4.toFixed(2)} mm</div>
                    <div className="text-xs text-gray-500 mt-1">Range: 0.25 to 0.35 times t<sub>3</sub></div>
                  </div>
                </div>
              </div>
            </div>

            {/* 4. PISTON SKIRT */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-2xl font-bold text-gray-800 mb-4 flex items-center gap-2">
                <FileText className="w-6 h-6 text-blue-600" />
                4. Piston Skirt Design
              </h2>

              <div className="space-y-4">
                <div className="bg-rose-50 border-l-4 border-rose-600 p-4 rounded">
                  <h3 className="font-semibold text-gray-800 mb-2">Side Thrust Analysis</h3>
                  <p className="text-sm text-gray-600 mb-3">
                    Maximum side thrust = 1/10 of maximum gas load
                  </p>
                  
                  <div className="bg-white p-3 rounded border border-rose-200 mb-3">
                    <div className="text-sm font-mono text-center mb-2">
                      P = (π × D² × p) / 4 (Maximum gas load)
                    </div>
                    <div className="text-sm font-mono text-center mb-2">
                      R = P / 10 (Side thrust)
                    </div>
                    <div className="text-sm font-mono text-center">
                      l = R / (p<sub>b</sub> × D) (Skirt length)
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div className="bg-white p-2 rounded border">
                      <span className="font-medium">Max Gas Load (P) =</span> {calculations.P_gas.toFixed(1)} N
                    </div>
                    <div className="bg-white p-2 rounded border">
                      <span className="font-medium">Side Thrust (R) =</span> {calculations.R_thrust.toFixed(1)} N
                    </div>
                    <div className="bg-white p-2 rounded border">
                      <span className="font-medium">Calculated Length =</span> {calculations.l_skirt.toFixed(2)} mm
                    </div>
                    <div className="bg-white p-2 rounded border">
                      <span className="font-medium">Practical (0.725D) =</span> {calculations.l_skirt_practical.toFixed(2)} mm
                    </div>
                    <div className="col-span-2 bg-green-50 p-3 rounded border border-green-300">
                      <span className="font-bold text-lg">Final Skirt Length =</span> 
                      <span className="text-xl font-bold text-green-600 ml-2">{calculations.l_skirt_final.toFixed(2)} mm</span>
                    </div>
                  </div>
                </div>

                <div className="bg-amber-50 border-l-4 border-amber-600 p-4 rounded">
                  <h3 className="font-semibold text-gray-800 mb-2">Total Piston Length</h3>
                  
                  <div className="bg-white p-3 rounded border border-amber-200 mb-3">
                    <div className="text-sm font-mono text-center">
                      L = Skirt Length + Ring Section + Top Land
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-4 text-sm">
                    <div className="bg-white p-2 rounded border text-center">
                      <div className="text-xs text-gray-600 mb-1">Skirt</div>
                      <div className="font-bold">{calculations.l_skirt_final.toFixed(2)} mm</div>
                    </div>
                    <div className="bg-white p-2 rounded border text-center">
                      <div className="text-xs text-gray-600 mb-1">Ring Section</div>
                      <div className="font-bold">{calculations.ringSection.toFixed(2)} mm</div>
                    </div>
                    <div className="bg-white p-2 rounded border text-center">
                      <div className="text-xs text-gray-600 mb-1">Top Land</div>
                      <div className="font-bold">{calculations.b1.toFixed(2)} mm</div>
                    </div>
                  </div>

                  <div className="mt-3 bg-gradient-to-r from-amber-500 to-amber-600 text-white p-3 rounded">
                    <div className="flex items-center justify-between">
                      <span className="font-bold">Total Piston Length (L)</span>
                      <span className="text-2xl font-bold">{calculations.L_total.toFixed(2)} mm</span>
                    </div>
                    <div className="text-xs text-amber-100 mt-1">
                      Typical range: {inputs.cylinderBore} to {(1.5 * inputs.cylinderBore).toFixed(0)} mm (D to 1.5D)
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* 5. PISTON PIN */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-2xl font-bold text-gray-800 mb-4 flex items-center gap-2">
                <FileText className="w-6 h-6 text-blue-600" />
                5. Piston Pin (Gudgeon Pin) Design
              </h2>

              <div className="space-y-4">
                <div className="bg-teal-50 border-l-4 border-teal-600 p-4 rounded">
                  <h3 className="font-semibold text-gray-800 mb-2">Pin Diameter Calculation</h3>
                  <p className="text-sm text-gray-600 mb-3">
                    Based on bearing pressure at connecting rod bushing
                  </p>
                  
                  <div className="bg-white p-3 rounded border border-teal-200 mb-3">
                    <div className="text-sm font-mono text-center mb-2">
                      Gas Load = Bearing Load
                    </div>
                    <div className="text-sm font-mono text-center mb-2">
                      (π × D² × p) / 4 = p<sub>b1</sub> × d<sub>0</sub> × l<sub>1</sub>
                    </div>
                    <div className="text-sm font-mono text-center">
                      d<sub>0</sub> = √[(π × D² × p) / (4 × p<sub>b1</sub> × l<sub>1</sub>)]
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div className="bg-white p-2 rounded border">
                      <span className="font-medium">Length in Bush (l<sub>1</sub>) =</span> {calculations.l1.toFixed(2)} mm
                      <div className="text-xs text-gray-500">= 0.45 × D</div>
                    </div>
                    <div className="bg-white p-2 rounded border">
                      <span className="font-medium">Bearing Pressure =</span> {inputs.bearingPressurePin} N/mm²
                    </div>
                    <div className="bg-green-50 p-3 rounded border border-green-300">
                      <span className="font-bold">Outer Diameter (d<sub>0</sub>) =</span> 
                      <span className="text-lg font-bold text-green-600 ml-2">{calculations.d0.toFixed(2)} mm</span>
                    </div>
                    <div className="bg-green-50 p-3 rounded border border-green-300">
                      <span className="font-bold">Inner Diameter (d<sub>i</sub>) =</span> 
                      <span className="text-lg font-bold text-green-600 ml-2">{calculations.di.toFixed(2)} mm</span>
                      <div className="text-xs text-gray-600 mt-1">= 0.6 × d<sub>0</sub></div>
                    </div>
                  </div>
                </div>

                <div className="bg-violet-50 border-l-4 border-violet-600 p-4 rounded">
                  <h3 className="font-semibold text-gray-800 mb-2">Bending Stress Check</h3>
                  <p className="text-sm text-gray-600 mb-3">
                    Pin treated as beam with uniform load and supports at boss centers
                  </p>
                  
                  <div className="bg-white p-3 rounded border border-violet-200 mb-3">
                    <div className="text-sm font-mono text-center mb-2">
                      M = (P × D) / 8 (Maximum bending moment)
                    </div>
                    <div className="text-sm font-mono text-center mb-2">
                      Z = (π / 32) × [(d<sub>0</sub><sup>4</sup> - d<sub>i</sub><sup>4</sup>) / d<sub>0</sub>]
                    </div>
                    <div className="text-sm font-mono text-center">
                      σ<sub>b(induced)</sub> = M / Z
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4 text-sm mb-4">
                    <div className="bg-white p-2 rounded border">
                      <span className="font-medium">Support Span (l<sub>2</sub>) =</span> {calculations.l2.toFixed(2)} mm
                    </div>
                    <div className="bg-white p-2 rounded border">
                      <span className="font-medium">Bending Moment (M) =</span> {calculations.M_pin.toFixed(0)} N·mm
                    </div>
                    <div className="bg-white p-2 rounded border">
                      <span className="font-medium">Section Modulus (Z) =</span> {calculations.Z_pin.toFixed(0)} mm³
                    </div>
                    <div className="bg-white p-2 rounded border">
                      <span className="font-medium">Allowable Stress =</span> {inputs.pinBendingStress} MPa
                    </div>
                  </div>

                  <div className={`p-4 rounded-lg ${calculations.pinSafe ? 'bg-green-500' : 'bg-red-500'} text-white`}>
                    <div className="flex items-center gap-3">
                      {calculations.pinSafe ? (
                        <CheckCircle className="w-8 h-8" />
                      ) : (
                        <AlertCircle className="w-8 h-8" />
                      )}
                      <div className="flex-1">
                        <div className="font-bold text-lg mb-1">
                          Induced Bending Stress: {calculations.σb_induced.toFixed(2)} MPa
                        </div>
                        <div className="text-sm">
                          {calculations.pinSafe 
                            ? '✓ Design is SAFE - Induced stress is within allowable limits' 
                            : '✗ Design UNSAFE - Increase pin diameter or change material'}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* 6. DESIGN SUMMARY */}
            <div className="bg-gradient-to-br from-slate-800 to-slate-900 text-white rounded-xl shadow-lg p-6">
              <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
                <Calculator className="w-6 h-6" />
                Final Design Summary
              </h2>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-3">
                  <h3 className="font-bold text-lg text-blue-300 mb-3">Piston Head & Barrel</h3>
                  <div className="bg-slate-700 p-3 rounded">
                    <div className="text-sm text-gray-300">Head Thickness (t<sub>H</sub>)</div>
                    <div className="text-xl font-bold">{calculations.tH.toFixed(2)} mm</div>
                  </div>
                  <div className="bg-slate-700 p-3 rounded">
                    <div className="text-sm text-gray-300">Max Barrel Thickness (t<sub>3</sub>)</div>
                    <div className="text-xl font-bold">{calculations.t3.toFixed(2)} mm</div>
                  </div>
                  <div className="bg-slate-700 p-3 rounded">
                    <div className="text-sm text-gray-300">Min Barrel Thickness (t<sub>4</sub>)</div>
                    <div className="text-xl font-bold">{calculations.t4.toFixed(2)} mm</div>
                  </div>
                </div>

                <div className="space-y-3">
                  <h3 className="font-bold text-lg text-green-300 mb-3">Piston Rings</h3>
                  <div className="bg-slate-700 p-3 rounded">
                    <div className="text-sm text-gray-300">Radial Thickness (t<sub>1</sub>)</div>
                    <div className="text-xl font-bold">{calculations.t1.toFixed(2)} mm</div>
                  </div>
                  <div className="bg-slate-700 p-3 rounded">
                    <div className="text-sm text-gray-300">Axial Thickness (t<sub>2</sub>)</div>
                    <div className="text-xl font-bold">{calculations.t2.toFixed(2)} mm</div>
                  </div>
                  <div className="bg-slate-700 p-3 rounded">
                    <div className="text-sm text-gray-300">Top Land Width (b<sub>1</sub>)</div>
                    <div className="text-xl font-bold">{calculations.b1.toFixed(2)} mm</div>
                  </div>
                </div>

                <div className="space-y-3">
                  <h3 className="font-bold text-lg text-purple-300 mb-3">Piston Dimensions</h3>
                  <div className="bg-slate-700 p-3 rounded">
                    <div className="text-sm text-gray-300">Skirt Length</div>
                    <div className="text-xl font-bold">{calculations.l_skirt_final.toFixed(2)} mm</div>
                  </div>
                  <div className="bg-slate-700 p-3 rounded">
                    <div className="text-sm text-gray-300">Total Length (L)</div>
                    <div className="text-xl font-bold">{calculations.L_total.toFixed(2)} mm</div>
                  </div>
                  <div className="bg-slate-700 p-3 rounded">
                    <div className="text-sm text-gray-300">L/D Ratio</div>
                    <div className="text-xl font-bold">{(calculations.L_total / inputs.cylinderBore).toFixed(2)}</div>
                  </div>
                </div>

                <div className="space-y-3">
                  <h3 className="font-bold text-lg text-orange-300 mb-3">Piston Pin</h3>
                  <div className="bg-slate-700 p-3 rounded">
                    <div className="text-sm text-gray-300">Outer Diameter (d<sub>0</sub>)</div>
                    <div className="text-xl font-bold">{calculations.d0.toFixed(2)} mm</div>
                  </div>
                  <div className="bg-slate-700 p-3 rounded">
                    <div className="text-sm text-gray-300">Inner Diameter (d<sub>i</sub>)</div>
                    <div className="text-xl font-bold">{calculations.di.toFixed(2)} mm</div>
                  </div>
                  <div className={`p-3 rounded ${calculations.pinSafe ? 'bg-green-600' : 'bg-red-600'}`}>
                    <div className="text-sm">Stress Status</div>
                    <div className="text-xl font-bold">{calculations.pinSafe ? 'SAFE' : 'UNSAFE'}</div>
                  </div>
                </div>
              </div>
            </div>

            {/* 7. DESIGN NOTES */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-2xl font-bold text-gray-800 mb-4 flex items-center gap-2">
                <AlertCircle className="w-6 h-6 text-blue-600" />
                Design Notes & Recommendations
              </h2>

              <div className="space-y-3 text-sm">
                <div className="bg-blue-50 border-l-4 border-blue-500 p-4 rounded">
                  <h3 className="font-semibold text-blue-900 mb-2">Piston Head</h3>
                  <ul className="list-disc list-inside space-y-1 text-gray-700">
                    <li>Thickness calculated from both strength and heat considerations</li>
                    {calculations.needsRibs && (
                      <li className="text-orange-600 font-medium">
                        Ribs required as t<sub>H</sub> &gt; 6 mm. Use thickness = {(calculations.tH/3).toFixed(2)} to {(calculations.tH/2).toFixed(2)} mm
                      </li>
                    )}
                    <li>For L/D ratio up to 1.5, consider providing a cup with radius = 0.7D for combustion chamber</li>
                  </ul>
                </div>

                <div className="bg-green-50 border-l-4 border-green-500 p-4 rounded">
                  <h3 className="font-semibold text-green-900 mb-2">Piston Rings</h3>
                  <ul className="list-disc list-inside space-y-1 text-gray-700">
                    <li>Ring groove depth should be more than ring depth to prevent side thrust</li>
                    <li>Gap when free: {calculations.ringGap_free.toFixed(2)} mm (3.5 to 4 times t<sub>1</sub>)</li>
                    <li>Gap when fitted: {calculations.ringGap_fitted.toFixed(2)} mm (0.002D to 0.004D)</li>
                    <li>Use diagonal or step cut for ring ends</li>
                  </ul>
                </div>

                <div className="bg-purple-50 border-l-4 border-purple-500 p-4 rounded">
                  <h3 className="font-semibold text-purple-900 mb-2">Piston Skirt</h3>
                  <ul className="list-disc list-inside space-y-1 text-gray-700">
                    <li>Bearing pressure: {inputs.bearingPressureSkirt} N/mm² (0.25 for low speed, 0.5 for high speed engines)</li>
                    <li>Pin center should be 0.02D to 0.04D above skirt center: {(0.03 * inputs.cylinderBore).toFixed(2)} mm</li>
                    <li>Total piston length typically ranges from D to 1.5D</li>
                  </ul>
                </div>

                <div className="bg-orange-50 border-l-4 border-orange-500 p-4 rounded">
                  <h3 className="font-semibold text-orange-900 mb-2">Piston Pin</h3>
                  <ul className="list-disc list-inside space-y-1 text-gray-700">
                    <li>Pin is hollow and tapered internally with smallest diameter at center</li>
                    <li>Mean boss diameter: {(1.45 * calculations.d0).toFixed(2)} mm (1.4 to 1.5 times d<sub>0</sub>)</li>
                    <li>Secure end movement with spring circlips (full floating type)</li>
                    <li>Material: Case hardened steel alloy (710-910 MPa tensile strength)</li>
                  </ul>
                </div>

                <div className="bg-gray-50 border-l-4 border-gray-500 p-4 rounded">
                  <h3 className="font-semibold text-gray-900 mb-2">Material Properties Used</h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-2">
                    <div>
                      <div className="text-xs text-gray-600">Material</div>
                      <div className="font-medium">{inputs.pistonMaterial.replace('_', ' ').toUpperCase()}</div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-600">Bending Stress</div>
                      <div className="font-medium">{inputs.bendingStress} MPa</div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-600">Heat Conductivity</div>
                      <div className="font-medium">{inputs.heatConductivity} W/m/°C</div>
                    </div>
                    <div>
                      <div className="text-xs text-gray-600">Temp Difference</div>
                      <div className="font-medium">{inputs.tempDifference} °C</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="bg-slate-800 text-white py-6 mt-12">
        <div className="max-w-7xl mx-auto px-6 text-center">
          <p className="text-sm text-slate-300">
            Based on "A Textbook of Machine Design" - IC Engine Piston Design Methodology
          </p>
          <p className="text-xs text-slate-400 mt-2">
            All calculations follow standard mechanical engineering formulas and empirical relations
          </p>
        </div>
      </div>
    </div>
  );
};

export default PistonDesignDashboard;
