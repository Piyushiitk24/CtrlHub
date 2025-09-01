import React, { useEffect } from 'react';
import NextPreviousNav from '../../../components/navigation/NextPreviousNav';

const TransferFunctionTF: React.FC = () => {
  useEffect(() => { document.title = 'DC Motor — Transfer Function & Simulink TF — CtrlHub'; }, []);
  return (
    <>
      <div className="section">
        <h3>Transfer Function & Simulink TF</h3>
        <p>Derive the motor transfer function and validate with Simulink linear blocks.</p>
        
        <div className="section">
          <h4>Transfer Function Derivation</h4>
          <p>From the differential equations, we can derive the transfer function:</p>
          <ul>
            <li><strong>Voltage to Speed:</strong> G(s) = Kt / (Ls + R)(Js + B) + KtKe</li>
            <li><strong>Voltage to Position:</strong> H(s) = G(s)/s</li>
            <li>Simplification leads to second-order system characteristics</li>
          </ul>
        </div>
        
        <div className="section">
          <h4>Simulink Implementation</h4>
          <p>Compare the first-principles model with Transfer Function blocks:</p>
          <ul>
            <li>Use Transfer Fcn block with derived coefficients</li>
            <li>Validate against differential equation model</li>
            <li>Analyze frequency response and step response</li>
          </ul>
        </div>
      </div>
      
      <NextPreviousNav />
    </>
  );
};

export default TransferFunctionTF;
