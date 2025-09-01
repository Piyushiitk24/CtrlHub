import React, { useEffect } from 'react';
import NextPreviousNav from '../../../components/navigation/NextPreviousNav';
import RelatedComponents from '../../../components/search/RelatedComponents';

const HardwareBuild: React.FC = () => {
  useEffect(() => { document.title = 'DC Motor — Hardware Build — CtrlHub'; }, []);
  return (
    <>
      <div className="section">
        <h3>Hardware Build (Arduino + L298N + Encoder)</h3>
        <p>Wiring diagrams, serial protocol, and test procedures for the motor rig.</p>
        
        <div className="section">
          <h4>Required Components</h4>
          <ul>
            <li><strong>Arduino Uno:</strong> Main controller for PWM and sensor reading</li>
            <li><strong>L298N Driver:</strong> H-bridge for bidirectional motor control</li>
            <li><strong>DC Motor:</strong> Geared motor with reasonable torque</li>
            <li><strong>Encoder:</strong> Quadrature encoder for position feedback</li>
            <li><strong>Power Supply:</strong> 12V for motor, 5V for logic</li>
            <li><strong>Current Sensor:</strong> ACS712 for real-time current monitoring</li>
          </ul>
        </div>
        
        <div className="section">
          <h4>Wiring Configuration</h4>
          <p>Critical connections for safe operation:</p>
          <ul>
            <li><strong>Motor Power:</strong> Motor terminals to L298N output (OUT1, OUT2)</li>
            <li><strong>PWM Control:</strong> Arduino pins 9, 10 to ENA, IN1, IN2</li>
            <li><strong>Encoder Feedback:</strong> A/B phases to interrupt pins 2, 3</li>
            <li><strong>Current Sensing:</strong> ACS712 output to analog pin A0</li>
            <li><strong>Power Distribution:</strong> 12V to L298N VCC, 5V to Arduino and encoder</li>
          </ul>
        </div>
        
        <div className="section">
          <h4>Safety Considerations</h4>
          <ul>
            <li><strong>Isolation:</strong> Keep motor power separate from logic power</li>
            <li><strong>Current Limiting:</strong> Monitor motor current to prevent damage</li>
            <li><strong>Emergency Stop:</strong> Implement software and hardware emergency stops</li>
            <li><strong>Thermal Protection:</strong> Monitor L298N temperature during operation</li>
          </ul>
        </div>
        
        <div className="section">
          <h4>Testing Protocol</h4>
          <ol>
            <li><strong>Power On Test:</strong> Verify all voltage levels (12V, 5V, 3.3V)</li>
            <li><strong>Encoder Verification:</strong> Count pulses with manual rotation</li>
            <li><strong>PWM Validation:</strong> Test speed control with incremental commands</li>
            <li><strong>Current Monitoring:</strong> Measure and log current consumption</li>
            <li><strong>Direction Control:</strong> Verify both forward and reverse operation</li>
            <li><strong>Closed-Loop Test:</strong> Implement basic PI speed control</li>
          </ol>
        </div>

        <div className="section">
          <h4>Common Issues & Solutions</h4>
          <ul>
            <li><strong>Encoder Noise:</strong> Add pull-up resistors and debouncing</li>
            <li><strong>Motor Stalling:</strong> Check power supply capacity and connections</li>
            <li><strong>Erratic Behavior:</strong> Verify ground connections and EMI shielding</li>
            <li><strong>Current Spikes:</strong> Add flyback diodes and capacitive filtering</li>
          </ul>
        </div>
      </div>
      
      <RelatedComponents currentComponentId="dc-motor" />
      <NextPreviousNav />
    </>
  );
};

export default HardwareBuild;
