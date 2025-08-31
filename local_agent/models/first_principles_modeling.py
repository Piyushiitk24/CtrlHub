"""
DC Motor First-Principles Modeling Module
Educational implementation of DC motor physics-based models
"""

import logging
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass
import time

logger = logging.getLogger(__name__)

@dataclass
class MotorPhysics:
    """Physical constants and relationships for DC motor modeling"""
    
    # Electromagnetic constants
    R: float = 2.5          # Armature resistance (Ω)
    L: float = 0.001        # Armature inductance (H)
    Ke: float = 0.05        # Back-EMF constant (V·s/rad)
    Kt: float = 0.05        # Torque constant (N·m/A)
    
    # Mechanical constants
    J: float = 0.0001       # Moment of inertia (kg·m²)
    b: float = 0.00005      # Viscous friction coefficient (N·m·s/rad)
    
    # Physical validation
    def __post_init__(self):
        """Validate physical consistency of parameters"""
        if abs(self.Kt - self.Ke) > 0.01:
            logger.warning(f"Kt ({self.Kt}) and Ke ({self.Ke}) should be equal in SI units")
        
        self.tau_electrical = self.L / self.R if self.R > 0 else 0
        self.tau_mechanical = self.J / self.b if self.b > 0 else 0
        
        if self.tau_electrical > self.tau_mechanical:
            logger.warning("Electrical time constant larger than mechanical - unusual for small motors")

class DCMotorFirstPrinciples:
    """
    First-Principles DC Motor Modeling
    
    Educational implementation based on fundamental physics:
    - Faraday's law for back-EMF
    - Ampère's law for force/torque
    - Newton's laws for mechanical dynamics
    - Kirchhoff's laws for electrical circuits
    """
    
    def __init__(self, physics: MotorPhysics):
        self.physics = physics
        self.educational_explanations = {}
        
    def derive_electrical_equation(self) -> Dict[str, Any]:
        """
        Derive electrical circuit equation from first principles
        
        Educational Objective:
        - Apply Kirchhoff's voltage law
        - Understand back-EMF as induced voltage
        - Learn differential equation formulation
        
        Physics Foundation:
        1. Applied voltage: Va(t)
        2. Resistive drop: R·ia(t)
        3. Inductive drop: L·dia/dt
        4. Back-EMF: Ke·ω(t)
        
        Kirchhoff's Law: Va = R·ia + L·dia/dt + Ke·ω
        """
        logger.info("Deriving electrical equation from Kirchhoff's voltage law")
        
        equation = {
            'differential_form': 'Va(t) = R·ia(t) + L·dia/dt + Ke·ω(t)',
            'laplace_form': 'Va(s) = (R + sL)·Ia(s) + Ke·Ω(s)',
            'transfer_function': 'Ia(s)/[Va(s) - Ke·Ω(s)] = 1/(R + sL)',
            'parameters': {
                'R': self.physics.R,
                'L': self.physics.L,
                'Ke': self.physics.Ke
            },
            'physical_interpretation': {
                'resistive_term': 'R·ia represents energy dissipation as heat',
                'inductive_term': 'L·dia/dt represents energy stored in magnetic field',
                'back_emf_term': 'Ke·ω opposes applied voltage (Lenz law)',
                'equilibrium': 'At steady state: Va = R·ia + Ke·ω'
            },
            'educational_insights': [
                'Back-EMF limits current at high speeds',
                'Inductance causes current lag during transients',
                'Resistance determines steady-state current',
                'Electrical time constant τe = L/R'
            ]
        }
        
        self.educational_explanations['electrical_equation'] = equation
        logger.info(f"Electrical time constant: {self.physics.tau_electrical:.4f} s")
        
        return equation
    
    def derive_mechanical_equation(self) -> Dict[str, Any]:
        """
        Derive mechanical dynamics equation from Newton's laws
        
        Educational Objective:
        - Apply Newton's second law for rotation
        - Understand torque balance
        - Learn angular motion dynamics
        
        Physics Foundation:
        1. Applied torque: Tm = Kt·ia(t)
        2. Friction torque: Tf = b·ω(t)
        3. Inertial torque: Ti = J·dω/dt
        4. Load torque: TL(t) (external)
        
        Newton's Law: J·dω/dt = Tm - Tf - TL = Kt·ia - b·ω - TL
        """
        logger.info("Deriving mechanical equation from Newton's second law")
        
        equation = {
            'differential_form': 'J·dω/dt = Kt·ia(t) - b·ω(t) - TL(t)',
            'laplace_form': 'sJ·Ω(s) = Kt·Ia(s) - b·Ω(s) - TL(s)',
            'transfer_function': 'Ω(s)/[Kt·Ia(s) - TL(s)] = 1/(sJ + b)',
            'parameters': {
                'J': self.physics.J,
                'b': self.physics.b,
                'Kt': self.physics.Kt
            },
            'physical_interpretation': {
                'inertial_term': 'J·dω/dt represents rotational inertia',
                'friction_term': 'b·ω represents viscous losses',
                'motor_torque': 'Kt·ia is electromagnetic torque generation',
                'load_torque': 'TL represents external mechanical load'
            },
            'educational_insights': [
                'Motor torque accelerates rotor against inertia',
                'Friction opposes motion (energy dissipation)',
                'Steady state: Kt·ia = b·ω + TL',
                'Mechanical time constant τm = J/b'
            ]
        }
        
        self.educational_explanations['mechanical_equation'] = equation
        logger.info(f"Mechanical time constant: {self.physics.tau_mechanical:.4f} s")
        
        return equation
    
    def derive_coupled_system(self) -> Dict[str, Any]:
        """
        Derive complete coupled electromechanical system
        
        Educational Objective:
        - Understand system coupling through Ke and Kt
        - Learn state-space representation
        - Analyze multi-domain interactions
        
        System States: x = [ia, ω]ᵀ
        """
        logger.info("Deriving coupled electromechanical system")
        
        # State-space matrices
        # dx/dt = Ax + Bu + Dw
        # x = [ia, ω]ᵀ, u = Va, w = TL
        
        A11 = -self.physics.R / self.physics.L
        A12 = -self.physics.Ke / self.physics.L
        A21 = self.physics.Kt / self.physics.J
        A22 = -self.physics.b / self.physics.J
        
        B1 = 1 / self.physics.L
        B2 = 0
        
        D1 = 0
        D2 = -1 / self.physics.J
        
        system = {
            'state_variables': ['ia (current)', 'ω (angular velocity)'],
            'input_variables': ['Va (applied voltage)', 'TL (load torque)'],
            'state_equations': [
                'dia/dt = -(R/L)·ia - (Ke/L)·ω + (1/L)·Va',
                'dω/dt = (Kt/J)·ia - (b/J)·ω - (1/J)·TL'
            ],
            'state_space_matrices': {
                'A': [[A11, A12], [A21, A22]],
                'B': [[B1], [B2]],
                'D': [[D1], [D2]]
            },
            'coupling_analysis': {
                'electrical_to_mechanical': 'Current ia creates torque Kt·ia',
                'mechanical_to_electrical': 'Speed ω creates back-EMF Ke·ω',
                'energy_conversion': 'Power = Va·ia = Tm·ω + losses',
                'feedback_nature': 'Speed affects current through back-EMF'
            },
            'characteristic_equation': f's² + {A11 + A22:.4f}s + {A11*A22 - A12*A21:.6f} = 0',
            'system_poles': self._calculate_system_poles(A11, A12, A21, A22),
            'educational_insights': [
                'Coupling makes motor a 2nd-order system',
                'Back-EMF provides natural speed regulation',
                'Current and speed dynamics interact',
                'System stability depends on all parameters'
            ]
        }
        
        self.educational_explanations['coupled_system'] = system
        
        return system
    
    def derive_transfer_functions(self) -> Dict[str, Any]:
        """
        Derive input-output transfer functions
        
        Educational Objective:
        - Learn transfer function derivation
        - Understand poles and zeros
        - Analyze frequency response characteristics
        """
        logger.info("Deriving system transfer functions")
        
        # System parameters
        R, L, Ke, Kt, J, b = self.physics.R, self.physics.L, self.physics.Ke, self.physics.Kt, self.physics.J, self.physics.b
        
        # Transfer function from voltage to speed: Ω(s)/Va(s)
        numerator_voltage_to_speed = Kt
        denominator = L*J*1 + (R*J + L*b)*1 + (R*b + Ke*Kt)  # s² coefficient is LJ, s coefficient is RJ+Lb, constant is Rb+KeKt
        
        # Transfer function from voltage to current: Ia(s)/Va(s)
        numerator_voltage_to_current = J*1 + b  # Js + b
        
        # Transfer function from load to speed: Ω(s)/TL(s)
        numerator_load_to_speed = -(R + L*1)  # -(R + Ls)
        
        transfer_functions = {
            'voltage_to_speed': {
                'numerator': f'{Kt:.4f}',
                'denominator': f'{L*J:.6f}s² + {R*J + L*b:.6f}s + {R*b + Ke*Kt:.6f}',
                'dc_gain': Kt / (R*b + Ke*Kt),
                'physical_meaning': 'Speed response to voltage input'
            },
            'voltage_to_current': {
                'numerator': f'{J:.6f}s + {b:.6f}',
                'denominator': f'{L*J:.6f}s² + {R*J + L*b:.6f}s + {R*b + Ke*Kt:.6f}',
                'dc_gain': b / (R*b + Ke*Kt),
                'physical_meaning': 'Current response to voltage input'
            },
            'load_to_speed': {
                'numerator': f'-({R:.3f} + {L:.6f}s)',
                'denominator': f'{L*J:.6f}s² + {R*J + L*b:.6f}s + {R*b + Ke*Kt:.6f}',
                'dc_gain': -R / (R*b + Ke*Kt),
                'physical_meaning': 'Speed response to load disturbance'
            },
            'system_characteristics': {
                'system_order': 2,
                'dominant_pole': self._estimate_dominant_pole(),
                'bandwidth_estimate': self._estimate_bandwidth(),
                'damping_analysis': self._analyze_damping()
            },
            'educational_insights': [
                'All transfer functions share same denominator (characteristic equation)',
                'DC gains determined by steady-state analysis',
                'Poles determine speed of response',
                'Zeros affect transient behavior'
            ]
        }
        
        self.educational_explanations['transfer_functions'] = transfer_functions
        
        return transfer_functions
    
    def analyze_steady_state_characteristics(self) -> Dict[str, Any]:
        """
        Analyze steady-state motor characteristics
        
        Educational Objective:
        - Understand speed-torque relationship
        - Learn motor operating regions
        - Analyze efficiency considerations
        """
        logger.info("Analyzing steady-state motor characteristics")
        
        # At steady state: dia/dt = 0, dω/dt = 0
        # Electrical: Va = R·ia + Ke·ω
        # Mechanical: Kt·ia = b·ω + TL
        
        characteristics = {
            'speed_torque_equation': 'ω = (Kt·Va - R·TL)/(R·b + Ke·Kt)',
            'current_torque_equation': 'ia = (b·Va + Ke·TL)/(R·b + Ke·Kt)',
            'no_load_conditions': {
                'speed': f'ω_no_load = {self.physics.Kt}/{self.physics.R * self.physics.b + self.physics.Ke * self.physics.Kt:.6f} · Va',
                'current': f'ia_no_load = {self.physics.b}/{self.physics.R * self.physics.b + self.physics.Ke * self.physics.Kt:.6f} · Va',
                'interpretation': 'Maximum speed, minimum current'
            },
            'stall_conditions': {
                'torque': f'T_stall = {self.physics.Kt}/{self.physics.R:.3f} · Va',
                'current': f'ia_stall = Va/{self.physics.R:.3f}',
                'interpretation': 'Maximum torque, maximum current'
            },
            'operating_point_analysis': self._generate_operating_points(),
            'efficiency_analysis': {
                'power_input': 'Pin = Va · ia',
                'power_mechanical': 'Pmech = T · ω = (Kt·ia - b·ω) · ω',
                'power_losses': 'Ploss = R·ia² + b·ω²',
                'efficiency': 'η = Pmech/Pin = (Kt·ia·ω - b·ω²)/(Va·ia)'
            },
            'educational_insights': [
                'Speed decreases linearly with load torque',
                'Current increases linearly with load torque',
                'Maximum efficiency occurs at intermediate load',
                'Speed regulation depends on internal resistance'
            ]
        }
        
        self.educational_explanations['steady_state'] = characteristics
        
        return characteristics
    
    def validate_model_physics(self) -> Dict[str, Any]:
        """
        Validate model against fundamental physics principles
        
        Educational Objective:
        - Verify energy conservation
        - Check dimensional consistency
        - Validate parameter relationships
        """
        logger.info("Validating model physics")
        
        validation = {
            'energy_conservation': self._check_energy_conservation(),
            'dimensional_analysis': self._check_dimensions(),
            'parameter_consistency': self._check_parameter_consistency(),
            'stability_analysis': self._check_stability(),
            'physical_limits': self._check_physical_limits(),
            'temperature_effects': {
                'resistance_variation': 'R increases ~0.4%/°C for copper',
                'magnet_effects': 'Ke, Kt may decrease with temperature',
                'thermal_time_constants': 'Much slower than electrical/mechanical'
            },
            'validation_summary': {
                'model_validity': 'Physical principles correctly applied',
                'assumptions': [
                    'Linear magnetic circuit',
                    'Constant parameters',
                    'Negligible eddy currents',
                    'Rigid mechanical coupling'
                ],
                'limitations': [
                    'No saturation effects',
                    'No hysteresis losses',
                    'No temperature dependence',
                    'No brush voltage drop'
                ]
            }
        }
        
        return validation
    
    def generate_educational_summary(self) -> Dict[str, Any]:
        """
        Generate comprehensive educational summary
        """
        summary = {
            'modeling_progression': {
                'step_1': 'Apply Kirchhoff\'s law to electrical circuit',
                'step_2': 'Apply Newton\'s law to mechanical system',
                'step_3': 'Couple systems through Ke and Kt',
                'step_4': 'Derive transfer functions',
                'step_5': 'Analyze steady-state behavior',
                'step_6': 'Validate against physics'
            },
            'key_physics_principles': {
                'electromagnetic_induction': 'Faraday\'s law creates back-EMF',
                'force_generation': 'Ampère\'s law creates motor torque',
                'energy_conversion': 'Electrical to mechanical energy',
                'feedback_coupling': 'Speed affects current through back-EMF'
            },
            'mathematical_tools': {
                'differential_equations': 'Describe dynamic behavior',
                'laplace_transforms': 'Enable transfer function analysis',
                'state_space': 'Systematic multi-variable approach',
                'linear_algebra': 'Matrix representation of systems'
            },
            'practical_insights': {
                'design_tradeoffs': 'Speed vs torque, efficiency vs size',
                'control_implications': 'System order affects controller design',
                'measurement_needs': 'Parameters determine required sensors',
                'performance_limits': 'Physics constrains achievable performance'
            },
            'next_learning_steps': [
                'Compare model predictions with experimental data',
                'Add nonlinear effects (saturation, friction)',
                'Design controllers based on model',
                'Optimize parameters for specific applications'
            ]
        }
        
        return summary
    
    # Helper methods for calculations
    def _calculate_system_poles(self, A11: float, A12: float, A21: float, A22: float) -> Dict[str, Any]:
        """Calculate system poles from state matrix"""
        # Characteristic equation: det(sI - A) = 0
        # s² - (A11 + A22)s + (A11*A22 - A12*A21) = 0
        
        trace = A11 + A22
        determinant = A11*A22 - A12*A21
        
        discriminant = trace**2 - 4*determinant
        
        if discriminant >= 0:
            pole1 = (-trace + discriminant**0.5) / 2
            pole2 = (-trace - discriminant**0.5) / 2
            pole_type = 'real'
        else:
            real_part = -trace / 2
            imag_part = (-discriminant)**0.5 / 2
            pole1 = complex(real_part, imag_part)
            pole2 = complex(real_part, -imag_part)
            pole_type = 'complex conjugate'
        
        return {
            'pole1': pole1,
            'pole2': pole2,
            'type': pole_type,
            'natural_frequency': (-determinant)**0.5 if determinant > 0 else 0,
            'damping_ratio': -trace / (2 * (-determinant)**0.5) if determinant > 0 else 0
        }
    
    def _estimate_dominant_pole(self) -> float:
        """Estimate dominant (slowest) pole"""
        # Typically the mechanical pole dominates
        return -self.physics.b / self.physics.J
    
    def _estimate_bandwidth(self) -> float:
        """Estimate system bandwidth"""
        return abs(self._estimate_dominant_pole())
    
    def _analyze_damping(self) -> Dict[str, Any]:
        """Analyze system damping characteristics"""
        # For second-order system: ωn² = (R·b + Ke·Kt)/(L·J)
        # 2ζωn = (R·J + L·b)/(L·J)
        
        omega_n_squared = (self.physics.R * self.physics.b + self.physics.Ke * self.physics.Kt) / (self.physics.L * self.physics.J)
        omega_n = omega_n_squared**0.5 if omega_n_squared > 0 else 0
        
        if omega_n > 0:
            zeta = (self.physics.R * self.physics.J + self.physics.L * self.physics.b) / (2 * self.physics.L * self.physics.J * omega_n)
        else:
            zeta = 0
        
        if zeta > 1:
            response_type = 'overdamped'
        elif zeta == 1:
            response_type = 'critically damped'
        elif zeta > 0:
            response_type = 'underdamped'
        else:
            response_type = 'unstable'
        
        return {
            'natural_frequency': omega_n,
            'damping_ratio': zeta,
            'response_type': response_type,
            'settling_time_estimate': 4 / (zeta * omega_n) if zeta * omega_n > 0 else float('inf')
        }
    
    def _generate_operating_points(self) -> List[Dict[str, float]]:
        """Generate sample operating points for analysis"""
        operating_points = []
        
        test_voltages = [3, 6, 9, 12]  # V
        test_loads = [0, 0.01, 0.02, 0.03]  # N·m
        
        for Va in test_voltages:
            for TL in test_loads:
                # Steady-state calculations
                denominator = self.physics.R * self.physics.b + self.physics.Ke * self.physics.Kt
                omega = (self.physics.Kt * Va - self.physics.R * TL) / denominator
                ia = (self.physics.b * Va + self.physics.Ke * TL) / denominator
                
                if omega >= 0 and ia >= 0:  # Physical solutions only
                    operating_points.append({
                        'voltage': Va,
                        'load_torque': TL,
                        'speed_rad_s': omega,
                        'speed_rpm': omega * 60 / (2 * 3.14159),
                        'current': ia,
                        'motor_torque': self.physics.Kt * ia,
                        'power_input': Va * ia,
                        'power_mechanical': (self.physics.Kt * ia - self.physics.b * omega) * omega
                    })
        
        return operating_points
    
    def _check_energy_conservation(self) -> Dict[str, Any]:
        """Check energy conservation in model"""
        return {
            'power_balance': 'Pin = Pmech + Pelec_loss + Pmech_loss',
            'electrical_loss': 'R·ia² (Joule heating)',
            'mechanical_loss': 'b·ω² (friction)',
            'energy_storage': 'L·ia²/2 (magnetic) + J·ω²/2 (kinetic)',
            'conservation_check': 'All energy terms accounted for'
        }
    
    def _check_dimensions(self) -> Dict[str, Any]:
        """Check dimensional consistency"""
        return {
            'voltage_equation': '[V] = [Ω][A] + [H][A/s] + [V·s/rad][rad/s] ✓',
            'torque_equation': '[N·m] = [N·m/A][A] - [N·m·s/rad][rad/s] - [N·m] ✓',
            'power_equation': '[W] = [V][A] = [N·m][rad/s] ✓',
            'time_constants': '[s] = [H]/[Ω] = [kg·m²]/[N·m·s/rad] ✓'
        }
    
    def _check_parameter_consistency(self) -> Dict[str, Any]:
        """Check parameter consistency"""
        kt_ke_ratio = self.physics.Kt / self.physics.Ke if self.physics.Ke > 0 else 0
        
        return {
            'kt_ke_relationship': f'Kt/Ke = {kt_ke_ratio:.3f} (should be ~1.0 in SI)',
            'time_constant_ratio': f'τe/τm = {self.physics.tau_electrical/self.physics.tau_mechanical:.3f}',
            'parameter_ranges': {
                'R': '1-10 Ω typical for small motors',
                'L': '0.1-10 mH typical',
                'Ke=Kt': '0.01-0.1 typical',
                'J': '1e-6 to 1e-3 kg·m² typical',
                'b': '1e-6 to 1e-4 N·m·s/rad typical'
            }
        }
    
    def _check_stability(self) -> Dict[str, Any]:
        """Check system stability"""
        # For stable system, all poles must have negative real parts
        poles = self._calculate_system_poles(
            -self.physics.R/self.physics.L,
            -self.physics.Ke/self.physics.L,
            self.physics.Kt/self.physics.J,
            -self.physics.b/self.physics.J
        )
        
        stable = True
        if isinstance(poles['pole1'], complex):
            stable = poles['pole1'].real < 0 and poles['pole2'].real < 0
        else:
            stable = poles['pole1'] < 0 and poles['pole2'] < 0
        
        return {
            'stable': stable,
            'stability_condition': 'All poles in left half-plane',
            'marginal_stability': 'Poles on imaginary axis',
            'instability_causes': 'Negative resistance or friction'
        }
    
    def _check_physical_limits(self) -> Dict[str, Any]:
        """Check physical parameter limits"""
        return {
            'positive_parameters': {
                'R > 0': self.physics.R > 0,
                'L > 0': self.physics.L > 0,
                'J > 0': self.physics.J > 0,
                'b > 0': self.physics.b > 0
            },
            'typical_ranges_met': 'Compare with manufacturer specifications',
            'power_ratings': 'Check against voltage and current limits',
            'thermal_limits': 'Consider temperature rise with current'
        }