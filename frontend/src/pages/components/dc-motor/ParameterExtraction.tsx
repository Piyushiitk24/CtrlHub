import React, { useEffect } from 'react';
import NextPreviousNav from '../../../components/navigation/NextPreviousNav';

const ParameterExtraction: React.FC = () => {
  useEffect(() => { document.title = 'DC Motor — Parameter Extraction — CtrlHub'; }, []);
  return (
    <>
      <div className="section">
        <h3>Extract Parameters (No Datasheet)</h3>
        <p>Experimental methods to determine motor parameters when datasheets are unavailable or unreliable.</p>
        
        <div className="section">
          <h4>Resistance (R) and Inductance (L)</h4>
          <ul>
            <li><strong>DC Resistance:</strong> Measure with multimeter when rotor is locked</li>
            <li><strong>AC Impedance:</strong> Apply small AC signal, measure voltage/current ratio</li>
            <li><strong>Time Constant:</strong> τ = L/R from current step response</li>
            <li>Typical values: R = 1-10Ω, L = 1-10mH for small motors</li>
          </ul>
        </div>
        
        <div className="section">
          <h4>Rotor Inertia (J)</h4>
          <ul>
            <li><strong>Acceleration Test:</strong> Apply constant voltage, measure ω(t)</li>
            <li><strong>Calculation:</strong> J = Kt·i / (dω/dt) - accounting for friction</li>
            <li><strong>Coast-down Method:</strong> Analyze deceleration from known speed</li>
            <li>Cross-validate with geometric/material properties if possible</li>
          </ul>
        </div>
        
        <div className="section">
          <h4>Motor Constants (Kt, Ke)</h4>
          <ul>
            <li><strong>Torque Constant (Kt):</strong> Measure torque vs current with brake/scale</li>
            <li><strong>Back-EMF Constant (Ke):</strong> Measure generated voltage at known speed</li>
            <li><strong>Validation:</strong> Kt = Ke in SI units (theoretical relationship)</li>
            <li>Use both methods to verify consistency and identify losses</li>
          </ul>
        </div>
        
        <div className="section">
          <h4>Friction Coefficient (B)</h4>
          <ul>
            <li><strong>Coast-down Test:</strong> ω(t) = ω₀·e^(-B/J)t for pure viscous friction</li>
            <li><strong>Steady-state Analysis:</strong> At constant speed, T_motor = B·ω</li>
            <li><strong>Multiple Speeds:</strong> Test at various speeds to check linearity</li>
            <li>Separate viscous and Coulomb friction components if needed</li>
          </ul>
        </div>
      </div>
      
      <NextPreviousNav />
    </>
  );
};

export default ParameterExtraction;
