import React, { useEffect } from 'react';
import NextPreviousNav from '../../../components/navigation/NextPreviousNav';
import RelatedComponents from '../../../components/search/RelatedComponents';
import SemanticTags from '../../../components/learning/SemanticTags';
import { useProgressTracking } from '../../../hooks/useProgressTracking';
import { COMPONENT_METADATA } from '../../../data/componentMetadata';

const SimulinkFirstPrinciples: React.FC = () => {
  useEffect(() => { document.title = 'DC Motor — Simulink from First Principles — CtrlHub'; }, []);
  
  // Track progress automatically
  const { markCompleted } = useProgressTracking({
    componentId: 'dc-motor',
    sectionId: 'simulink-first-principles'
  });

  const dcMotorComponent = COMPONENT_METADATA.find(c => c.id === 'dc-motor');

  return (
    <>
      <div className="section">
        <h3>Simulink from First Principles</h3>
        <p>Build the electromechanical model using fundamental equations and simulate step responses.</p>
        
        <div className="section">
          <h4>Learning Objectives</h4>
          <ul>
            <li>Derive the DC motor differential equations from first principles</li>
            <li>Implement the mathematical model in Simulink</li>
            <li>Simulate step responses and analyze system behavior</li>
            <li>Understand the relationship between electrical and mechanical dynamics</li>
          </ul>
        </div>
        
        <div className="section">
          <h4>Mathematical Foundation</h4>
          <p>The DC motor combines electrical and mechanical systems. Key equations:</p>
          <ul>
            <li><strong>Electrical:</strong> V = L(di/dt) + Ri + Ke·ω</li>
            <li><strong>Mechanical:</strong> J(dω/dt) = Kt·i - B·ω - TL</li>
            <li><strong>Coupling:</strong> Kt = Ke (in SI units)</li>
          </ul>
        </div>

        <div className="section">
          <h4>Step-by-Step Implementation</h4>
          <ol>
            <li><strong>Create New Simulink Model:</strong> Start with a blank model and set up the basic structure</li>
            <li><strong>Electrical Subsystem:</strong> Implement the voltage equation using integrators and gain blocks</li>
            <li><strong>Mechanical Subsystem:</strong> Model the torque balance equation with proper feedback</li>
            <li><strong>Connect Systems:</strong> Link electrical current to mechanical torque using motor constant</li>
            <li><strong>Add Step Input:</strong> Configure step input for voltage and observe responses</li>
            <li><strong>Tune Parameters:</strong> Use realistic motor parameters (R, L, J, B, Kt, Ke)</li>
          </ol>
        </div>

        <div className="section">
          <h4>Key Insights</h4>
          <ul>
            <li>The electrical time constant (L/R) is typically much smaller than mechanical (J/B)</li>
            <li>Back EMF provides natural speed feedback that stabilizes the system</li>
            <li>Motor constant relationships ensure energy conservation in the model</li>
            <li>Step responses reveal both electrical and mechanical settling behaviors</li>
          </ul>
        </div>

        <div className="section">
          <h4>Practice Exercise</h4>
          <p>Build your own Simulink model and experiment with different parameter values:</p>
          <ul>
            <li><strong>Resistance (R):</strong> 2-10 Ω - affects electrical time constant</li>
            <li><strong>Inductance (L):</strong> 0.1-1 mH - electrical transient response</li>
            <li><strong>Inertia (J):</strong> 1e-6 to 1e-4 kg·m² - mechanical settling time</li>
            <li><strong>Friction (B):</strong> 1e-6 to 1e-4 N·m·s/rad - damping behavior</li>
          </ul>
          
          <div style={{ textAlign: 'center', margin: '2rem 0' }}>
            <button 
              onClick={() => markCompleted('dc-motor')}
              className="btn btn-success"
            >
              Mark Section Complete ✓
            </button>
          </div>
        </div>
      </div>
      
      {dcMotorComponent && (
        <SemanticTags 
          component={dcMotorComponent} 
          onTagClick={(tag) => console.log('Clicked tag:', tag)}
        />
      )}
      
      <RelatedComponents currentComponentId="dc-motor" />
      <NextPreviousNav />
    </>
  );
};

export default SimulinkFirstPrinciples;
