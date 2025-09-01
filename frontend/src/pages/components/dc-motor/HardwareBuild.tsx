import React from 'react';
import NextPreviousNav from '../../../components/navigation/NextPreviousNav';
import ContentOutline from '../../../components/navigation/ContentOutline';

const HardwareBuild: React.FC = () => {
  return (
    <div className="content-with-outline">
      <div className="content-main">
        <div className="section">
          <h2 id="overview">Hardware Overview</h2>
          <p>This section details the necessary components and wiring for the DC motor experiment.</p>
        </div>

        <div className="section">
          <h2 id="components">Component List</h2>
          <p>You will need the following components to build the circuit:</p>
          <ul>
            <li>Arduino UNO or similar microcontroller</li>
            <li>L298N Motor Driver</li>
            <li>12V DC Motor with Encoder</li>
            <li>12V Power Supply</li>
            <li>Jumper Wires</li>
            <li>Breadboard (optional)</li>
          </ul>
        </div>

        <div className="section">
          <h2 id="wiring">Wiring Diagram</h2>
          <p>Follow this diagram carefully to connect your components.</p>
          
          <h3 id="motor-driver-connections">Motor Driver Connections</h3>
          <p>Connect the L298N to the Arduino and the motor.</p>
          
          <h4 id="power-connections">Power Connections</h4>
          <p>Ensure the 12V power supply is connected correctly to the L298N.</p>

          <h4 id="signal-connections">Signal Connections</h4>
          <p>Connect the IN1, IN2, and ENA pins to the Arduino's digital pins.</p>

          <h3 id="encoder-connections">Encoder Connections</h3>
          <p>Connect the encoder outputs to the Arduino's interrupt-capable pins.</p>
        </div>

        <div className="section">
          <h2 id="troubleshooting">Troubleshooting</h2>
          <p>Common issues and their solutions.</p>
        </div>

        <NextPreviousNav />
      </div>
      <ContentOutline />
    </div>
  );
};

export default HardwareBuild;