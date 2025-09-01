
import React, { useEffect } from 'react';
import NextPreviousNav from '../../../components/navigation/NextPreviousNav';
import 'katex/dist/katex.min.css';
import { InlineMath } from 'react-katex';

const ParameterExtraction: React.FC = () => {
  useEffect(() => { document.title = 'DC Motor — Parameter Extraction — CtrlHub'; }, []);
  return (
    <>
      <div className="section">
        <h2>Motor Characterization: Creating Your DC Motor's Digital Twin</h2>
        <p>
          Welcome to your workshop! Today, our mission is to become motor detectives. We'll perform a series of experiments on your 12V geared DC motor to uncover its secret parameters. By the end, we'll have all the numbers needed to create a precise mathematical model (a "digital twin") of your motor in Python.
        </p>

        <h3>Our Target Parameters:</h3>
        <ul>
          <li><strong>Armature Resistance (<InlineMath math="R_a" />)</strong> in Ohms (Ω)</li>
          <li><strong>Armature Inductance (<InlineMath math="L_a" />)</strong> in Henries (H)</li>
          <li><strong>Back-EMF Constant (<InlineMath math="K_e" />)</strong> in V·s/rad</li>
          <li><strong>Torque Constant (<InlineMath math="K_t" />)</strong> in N·m/A</li>
          <li><strong>Rotor Inertia (<InlineMath math="J_m" />)</strong> in kg·m²</li>
          <li><strong>Damping Coefficient (<InlineMath math="B_m" />)</strong> in N·m·s/rad</li>
        </ul>

        <h3>Hardware & Software Setup</h3>
        <div className="section">
          <h4>Hardware:</h4>
          <ul>
            <li>12V 300 RPM DC Motor (60:1 Gear Ratio)</li>
            <li>L298N Motor Driver</li>
            <li>Quadrature Encoder (2400 CPR)</li>
            <li>Arduino Mega</li>
            <li>12V Power Supply</li>
            <li>LCR Meter & Multimeter</li>
          </ul>
        </div>

        <div className="section">
          <h4>Complete Pin Configuration:</h4>
          <h5>Arduino Mega:</h5>
          <ul>
            <li>5V Pin → Encoder RED wire (VCC)</li>
            <li>GND Pin → Common Ground Rail</li>
            <li>Pin 2 → Encoder GREEN wire (Signal A)</li>
            <li>Pin 3 → Encoder WHITE wire (Signal B)</li>
            <li>Pin 7 → L298N IN2 (Direction)</li>
            <li>Pin 8 → L298N IN1 (Direction)</li>
            <li>Pin 9 → L298N ENA (PWM Speed)</li>
          </ul>
          <h5>L298N Motor Driver:</h5>
          <ul>
            <li>VCC → 12V from Power Adapter (+)</li>
            <li>GND → Common Ground Rail</li>
            <li>IN1, IN2, ENA → Connected to Arduino pins 8, 7, 9</li>
            <li>OUT1, OUT2 → Connected to the two terminals of DC motor</li>
          </ul>
          <h5>Encoder & Power Supply:</h5>
          <ul>
            <li>Encoder RED → Arduino 5V</li>
            <li>Encoder BLACK → Common Ground Rail</li>
            <li>Encoder SHIELD → Common Ground Rail</li>
            <li>12V Adapter (+) → L298N VCC</li>
            <li>12V Adapter (-) → Common Ground Rail</li>
          </ul>
        </div>

        <div className="section">
          <h4>Software:</h4>
          <p>Python 3 with pandas, numpy, matplotlib, scipy, and the control library.</p>
        </div>

        <h3>Parameter Extraction Procedure</h3>
        <div className="section">
          <h4>Step 1: Measure Armature Resistance (<InlineMath math="R_a" />) and Inductance (<InlineMath math="L_a" />)</h4>
          <p>The simplest parameters to measure are the armature resistance and inductance. These can be measured directly using an LCR meter.</p>
          <ol>
            <li>Disconnect the motor from the driver circuit.</li>
            <li>Connect the LCR meter to the motor terminals.</li>
            <li>Set the LCR meter to measure resistance (R) and record the value. This is your <strong><InlineMath math="R_a" /></strong>.</li>
            <li>Set the LCR meter to measure inductance (L) and record the value. This is your <strong><InlineMath math="L_a" /></strong>.</li>
          </ol>
        </div>

        <div className="section">
          <h4>Step 2: Calculate Back-EMF (<InlineMath math="K_e" />) and Torque (<InlineMath math="K_t" />) Constants</h4>
          <p>These constants are determined by running the motor at a steady speed.</p>
          <ol>
            <li>Connect the motor to the L298N driver and Arduino as per the pin configuration.</li>
            <li>Apply a fixed PWM signal to the ENA pin to run the motor at a constant speed.</li>
            <li>Measure the steady-state RPM of the motor using the encoder data. Convert this to angular velocity (<InlineMath math="\omega" />) in rad/s.</li>
            <li>Measure the voltage (V) across the motor terminals using a multimeter.</li>
            <li>Measure the current (I) in series with the motor using a multimeter.</li>
            <li>Calculate the back-EMF voltage (<InlineMath math="V_{{bemf}}" />) using the formula: <InlineMath math="V_{{bemf}} = V - I \cdot R_a" />.</li>
            <li>Calculate the back-EMF constant (<InlineMath math="K_e" />) with: <InlineMath math="K_e = V_{{bemf}} / \omega" />.</li>
            <li>In SI units, the torque constant (<InlineMath math="K_t" />) is equal to the back-EMF constant (<InlineMath math="K_e" />). So, <strong><InlineMath math="K_t = K_e" /></strong>.</li>
          </ol>
        </div>

        <div className="section">
          <h4>Step 3: Determine Rotor Inertia (<InlineMath math="J_m" />) and Damping (<InlineMath math="B_m" />)</h4>
          <p>We'll use a coast-down test to find the mechanical properties of the motor.</p>
          <ol>
            <li>Run the motor at a steady speed (e.g., the same speed as in Step 2).</li>
            <li>Suddenly cut the power to the motor and record the speed from the encoder as it coasts to a stop.</li>
            <li>Plot the speed (<InlineMath math="\omega" />) vs. time (t) data. You should see an exponential decay.</li>
            <li>Fit an exponential curve of the form <InlineMath math="\omega(t) = \omega_0 e^{-t / \tau_m}" /> to the data to find the mechanical time constant (<strong><InlineMath math="\tau_m" /></strong>).</li>
            <li>The slope of the linearized plot (ln(<InlineMath math="\omega" />) vs t) will be <InlineMath math="-1/\tau_m" />.</li>
            <li>Calculate the damping coefficient (<InlineMath math="B_m" />) using the steady-state data from Step 2: <InlineMath math="B_m = (K_t \cdot I_{{ss}}) / \omega_{{ss}}" />, where <InlineMath math="I_{{ss}}" /> and <InlineMath math="\omega_{{ss}}" /> are the steady-state current and speed.</li>
            <li>Finally, calculate the rotor inertia (<InlineMath math="J_m" />) using the formula: <InlineMath math="J_m = B_m \cdot \tau_m" />.</li>
          </ol>
        </div>

        <h3>Interactive Simulation</h3>
        <p>Once you have all the parameters, you can use Python libraries like `control` to build a digital twin of your motor. This allows you to simulate its behavior and design controllers before implementing them on the real hardware.</p>

        <h3>Choose Your Hardware</h3>
        <p>You have two options for performing these experiments:</p>
        <ul>
          <li><strong>Use Our Hardware:</strong> We provide a fully configured hardware setup that you can access and control directly through this web interface.</li>
          <li><strong>Use Your Own Hardware:</strong> If you have the same or similar hardware, you can install our local agent. The agent uses the Web Serial API to communicate with your Arduino, allowing you to run the experiments on your own setup and visualize the results here.</li>
        </ul>

      </div>
      
      <NextPreviousNav />
    </>
  );
};

export default ParameterExtraction;
