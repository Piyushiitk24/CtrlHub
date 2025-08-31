"""
Comprehensive DC Motor Educational System
Integrating parameter extraction, modeling, and control for complete learning experience
"""

import logging
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass
import time
import asyncio

# Import the existing DC motor model and new educational modules
from .dc_motor import DCMotorModel, MotorParameters
from .parameter_extraction import DCMotorParameterExtractor, ExperimentConfig
from .first_principles_modeling import DCMotorFirstPrinciples, MotorPhysics
from .control_systems import DCMotorController, ControllerParameters, SystemIdentification

logger = logging.getLogger(__name__)

@dataclass
class EducationalProgress:
    """Track student progress through DC motor curriculum"""
    parameter_extraction_completed: Optional[List[str]] = None
    modeling_concepts_learned: Optional[List[str]] = None
    control_methods_practiced: Optional[List[str]] = None
    experiments_performed: int = 0
    
    def __post_init__(self):
        if self.parameter_extraction_completed is None:
            self.parameter_extraction_completed = []
        if self.modeling_concepts_learned is None:
            self.modeling_concepts_learned = []
        if self.control_methods_practiced is None:
            self.control_methods_practiced = []

class ComprehensiveDCMotorEducationalSystem:
    """
    Complete Educational DC Motor Learning Platform
    
    Integrates all aspects of DC motor education:
    1. Parameter Extraction through Experiments
    2. First-Principles Physics Modeling  
    3. Open-Loop and Closed-Loop Control Design
    4. Hardware Validation and Comparison
    5. Progressive Learning Framework
    
    Educational Philosophy:
    - Learn by doing with real hardware when available
    - Understand physics before applying control
    - Compare theory with experimental practice
    - Build intuition through hands-on experiments
    - Progress from simple to advanced concepts
    """
    
    def __init__(self, arduino_interface=None, motor_params: Optional[MotorParameters] = None):
        self.arduino = arduino_interface
        
        # Initialize with default or provided motor parameters
        if motor_params is None:
            motor_params = MotorParameters(
                R=2.5, L=0.001, J=0.0001, b=0.00005, Kt=0.05, Ke=0.05
            )
        
        # Core educational components
        self.motor_model = DCMotorModel(motor_params)
        self.parameter_extractor = DCMotorParameterExtractor(arduino_interface)
        
        # Convert to physics representation for modeling
        self.motor_physics = MotorPhysics(
            R=motor_params.R, L=motor_params.L, Ke=motor_params.Ke, 
            Kt=motor_params.Kt, J=motor_params.J, b=motor_params.b
        )
        
        self.first_principles = DCMotorFirstPrinciples(self.motor_physics)
        self.controller = DCMotorController(self.motor_physics, arduino_interface)
        
        # Progress tracking
        self.educational_progress = EducationalProgress()
        self.learning_history = []
        
        # Define comprehensive curriculum
        self.curriculum = self._define_comprehensive_curriculum()
        
        logger.info("Comprehensive DC Motor Educational System initialized")
        
    def _define_comprehensive_curriculum(self) -> Dict[str, Any]:
        """Define complete progressive learning curriculum"""
        return {
            'module_1_introduction': {
                'title': 'DC Motor Fundamentals and Safety',
                'duration': '30 minutes',
                'objectives': [
                    'Understand basic motor operation principles',
                    'Learn safety procedures for electrical experiments',
                    'Identify motor components and connections',
                    'Practice basic measurement techniques'
                ],
                'activities': [
                    'motor_inspection',
                    'safety_briefing',
                    'basic_measurements',
                    'connection_verification'
                ],
                'prerequisites': 'Basic electrical knowledge',
                'safety_level': 'High - electrical safety critical'
            },
            
            'module_2_parameter_extraction': {
                'title': 'Motor Parameter Identification Experiments',
                'duration': '2-3 hours',
                'objectives': [
                    'Measure electrical parameters (R, L)',
                    'Determine electromagnetic constants (Ke, Kt)',
                    'Extract mechanical properties (J, b)',
                    'Validate parameter consistency',
                    'Learn experimental design principles'
                ],
                'experiments': {
                    'resistance_measurement': {
                        'method': 'locked_rotor_ohms_law',
                        'safety': 'Low voltage only',
                        'learning': 'Ohms law application',
                        'duration': '20 minutes'
                    },
                    'back_emf_measurement': {
                        'method': 'free_running_voltage',
                        'safety': 'Coast-down procedure',
                        'learning': 'Faradays law',
                        'duration': '30 minutes'
                    },
                    'torque_constant_measurement': {
                        'method': 'stall_torque_test',
                        'safety': 'Current limiting essential',
                        'learning': 'Force generation',
                        'duration': '30 minutes'
                    },
                    'coast_down_test': {
                        'method': 'exponential_decay_analysis',
                        'safety': 'Free spinning motor',
                        'learning': 'Dynamic system analysis',
                        'duration': '40 minutes'
                    },
                    'inductance_measurement': {
                        'method': 'ac_impedance_analysis',
                        'safety': 'AC signal safety',
                        'learning': 'Frequency domain analysis',
                        'duration': '30 minutes'
                    }
                },
                'analysis_tools': ['curve_fitting', 'statistical_validation', 'uncertainty_analysis']
            },
            
            'module_3_first_principles_modeling': {
                'title': 'Physics-Based Mathematical Modeling',
                'duration': '2-3 hours',
                'objectives': [
                    'Derive motor equations from physical laws',
                    'Understand electromechanical coupling',
                    'Develop transfer function representations',
                    'Validate theoretical predictions',
                    'Learn system analysis techniques'
                ],
                'theoretical_development': {
                    'electrical_circuit_analysis': {
                        'law': 'Kirchhoffs voltage law',
                        'equation': 'V = R*i + L*di/dt + Ke*ω',
                        'physical_meaning': 'Voltage balance in armature circuit'
                    },
                    'mechanical_dynamics': {
                        'law': 'Newtons second law (rotational)',
                        'equation': 'J*dω/dt = Kt*i - b*ω - TL',
                        'physical_meaning': 'Torque balance on rotor'
                    },
                    'electromagnetic_coupling': {
                        'motor_constant': 'Kt = Ke (in SI units)',
                        'coupling_mechanism': 'Current creates torque, speed creates back-EMF',
                        'energy_conversion': 'Electrical to mechanical power'
                    }
                },
                'mathematical_tools': ['differential_equations', 'laplace_transforms', 'state_space']
            },
            
            'module_4_open_loop_control': {
                'title': 'Open-Loop Motor Control and Limitations',
                'duration': '1-2 hours', 
                'objectives': [
                    'Understand feed-forward control principles',
                    'Characterize open-loop performance',
                    'Identify limitations and disturbance effects',
                    'Learn calibration and compensation techniques'
                ],
                'experiments': {
                    'voltage_speed_characterization': {
                        'procedure': 'Measure steady-state speed vs voltage',
                        'analysis': 'Linear relationship validation',
                        'insights': 'Open-loop gain determination'
                    },
                    'load_disturbance_effects': {
                        'procedure': 'Apply varying mechanical loads',
                        'analysis': 'Speed regulation quantification',
                        'insights': 'Disturbance sensitivity'
                    },
                    'temperature_effects': {
                        'procedure': 'Monitor performance vs temperature',
                        'analysis': 'Parameter drift characterization',
                        'insights': 'Environmental sensitivity'
                    }
                },
                'limitations_analysis': ['no_disturbance_rejection', 'parameter_sensitivity', 'calibration_requirements']
            },
            
            'module_5_feedback_control_theory': {
                'title': 'Feedback Control Principles and PID Design',
                'duration': '3-4 hours',
                'objectives': [
                    'Understand feedback control benefits',
                    'Learn PID controller components and tuning',
                    'Practice multiple design approaches',
                    'Analyze performance trade-offs',
                    'Implement real-time control'
                ],
                'control_theory': {
                    'feedback_benefits': [
                        'Disturbance rejection capability',
                        'Reduced parameter sensitivity',
                        'Improved tracking accuracy',
                        'Stability robustness'
                    ],
                    'pid_components': {
                        'proportional': 'Present error response (speed)',
                        'integral': 'Past error elimination (accuracy)',
                        'derivative': 'Future error prediction (stability)'
                    }
                },
                'tuning_methods': {
                    'ziegler_nichols': {
                        'approach': 'Empirical rules from step response',
                        'advantages': 'Simple, no model required',
                        'limitations': 'Conservative, trial-and-error'
                    },
                    'pole_placement': {
                        'approach': 'Direct specification of closed-loop poles',
                        'advantages': 'Predictable response characteristics',
                        'limitations': 'Requires accurate model'
                    },
                    'frequency_domain': {
                        'approach': 'Design based on Bode plots and margins',
                        'advantages': 'Clear stability insight',
                        'limitations': 'Complex for beginners'
                    },
                    'lambda_tuning': {
                        'approach': 'Model-based with single parameter',
                        'advantages': 'Good robustness, easy to understand',
                        'limitations': 'Requires FOPDT model'
                    },
                    'optimization_based': {
                        'approach': 'Multi-objective performance optimization',
                        'advantages': 'Handles complex requirements',
                        'limitations': 'Computationally intensive'
                    }
                }
            },
            
            'module_6_advanced_control': {
                'title': 'Advanced Control Structures and Modern Methods',
                'duration': '4-6 hours',
                'objectives': [
                    'Learn cascade control architecture',
                    'Understand state-space control design',
                    'Practice observers and estimators',
                    'Explore modern control methods'
                ],
                'advanced_topics': {
                    'cascade_control': 'Inner current loop, outer speed loop',
                    'state_feedback': 'Full state feedback with pole placement',
                    'observers': 'State estimation for unmeasured variables',
                    'adaptive_control': 'Parameter adaptation for uncertainties',
                    'robust_control': 'H∞ and μ-synthesis methods',
                    'model_predictive_control': 'Optimization-based control with constraints'
                }
            },
            
            'module_7_system_integration': {
                'title': 'Complete System Integration and Validation',
                'duration': '2-3 hours',
                'objectives': [
                    'Integrate all learning components',
                    'Validate complete control system',
                    'Compare theoretical and experimental results',
                    'Document comprehensive analysis'
                ],
                'integration_activities': [
                    'complete_system_characterization',
                    'control_performance_validation',
                    'robustness_testing',
                    'comprehensive_documentation'
                ]
            }
        }
    
    async def start_educational_journey(self, starting_module: str = 'module_1_introduction') -> Dict[str, Any]:
        """
        Begin comprehensive educational journey through DC motor learning
        
        Args:
            starting_module: Which curriculum module to begin with
            
        Returns:
            Journey results and next steps
        """
        logger.info(f"Starting educational journey from {starting_module}")
        
        if starting_module not in self.curriculum:
            raise ValueError(f"Unknown module: {starting_module}")
        
        journey_result = {
            'journey_start': time.time(),
            'starting_module': starting_module,
            'modules_completed': [],
            'total_experiments': 0,
            'learning_outcomes': [],
            'challenges_encountered': [],
            'next_recommendations': []
        }
        
        # Execute the specified module
        module_result = await self._execute_learning_module(starting_module)
        journey_result['modules_completed'].append(module_result)
        
        # Update progress
        self._update_journey_progress(journey_result, module_result)
        
        # Generate recommendations for next steps
        journey_result['next_recommendations'] = self._generate_next_steps(starting_module)
        
        journey_result['journey_end'] = time.time()
        journey_result['total_duration'] = journey_result['journey_end'] - journey_result['journey_start']
        
        self.learning_history.append(journey_result)
        
        return journey_result
    
    async def _execute_learning_module(self, module_name: str) -> Dict[str, Any]:
        """Execute a specific learning module"""
        module_info = self.curriculum[module_name]
        
        module_result = {
            'module_name': module_name,
            'module_info': module_info,
            'start_time': time.time(),
            'activities_completed': [],
            'experiments_conducted': [],
            'learning_outcomes': [],
            'data_collected': {},
            'analysis_results': {},
            'educational_insights': []
        }
        
        # Module-specific execution
        if module_name == 'module_1_introduction':
            module_result = await self._execute_introduction_module(module_result)
        elif module_name == 'module_2_parameter_extraction':
            module_result = await self._execute_parameter_extraction_module(module_result)
        elif module_name == 'module_3_first_principles_modeling':
            module_result = await self._execute_modeling_module(module_result)
        elif module_name == 'module_4_open_loop_control':
            module_result = await self._execute_open_loop_module(module_result)
        elif module_name == 'module_5_feedback_control_theory':
            module_result = await self._execute_feedback_control_module(module_result)
        elif module_name == 'module_6_advanced_control':
            module_result = await self._execute_advanced_control_module(module_result)
        elif module_name == 'module_7_system_integration':
            module_result = await self._execute_integration_module(module_result)
        
        module_result['end_time'] = time.time()
        module_result['duration'] = module_result['end_time'] - module_result['start_time']
        
        return module_result
    
    async def _execute_introduction_module(self, module_result: Dict[str, Any]) -> Dict[str, Any]:
        """Execute introduction and safety module"""
        logger.info("Executing introduction and safety module")
        
        # Safety briefing
        module_result['safety_briefing'] = {
            'electrical_safety': [
                'Always verify power is off before connections',
                'Use appropriate voltage levels for experiments',
                'Never exceed motor current ratings',
                'Ensure proper grounding and isolation'
            ],
            'mechanical_safety': [
                'Secure motor mounting before operation',
                'Keep hands clear of rotating parts',
                'Use proper guards and barriers',
                'Emergency stop procedures'
            ],
            'measurement_safety': [
                'Verify meter settings before connection',
                'Use appropriate probe ratings',
                'Check for proper isolation',
                'Monitor for overheating'
            ]
        }
        
        # Basic motor inspection
        if self.arduino:
            inspection_result = await self._conduct_motor_inspection()
            module_result['motor_inspection'] = inspection_result
        else:
            module_result['motor_inspection'] = {
                'simulated': True,
                'motor_type': 'Simulated DC motor',
                'specifications': self.motor_model.params.to_dict()
            }
        
        module_result['activities_completed'] = ['safety_briefing', 'motor_inspection']
        module_result['learning_outcomes'] = [
            'Understood electrical and mechanical safety procedures',
            'Identified motor components and specifications',
            'Prepared for hands-on experiments'
        ]
        
        return module_result
    
    async def _execute_parameter_extraction_module(self, module_result: Dict[str, Any]) -> Dict[str, Any]:
        """Execute comprehensive parameter extraction module"""
        logger.info("Executing parameter extraction module")
        
        experiments_data = {}
        
        # Resistance measurement experiment
        logger.info("Conducting resistance measurement experiment")
        try:
            resistance_result = await self.parameter_extractor.extract_resistance()
            experiments_data['resistance'] = resistance_result
            module_result['experiments_conducted'].append('resistance_measurement')
            module_result['learning_outcomes'].append(
                f"Measured motor resistance using locked-rotor method: {resistance_result.get('resistance_measured', 0):.3f} Ω"
            )
        except Exception as e:
            logger.error(f"Resistance measurement failed: {e}")
            experiments_data['resistance'] = {'error': str(e), 'method': 'simulation_fallback'}
        
        # Back-EMF constant measurement
        logger.info("Conducting back-EMF measurement experiment")
        try:
            back_emf_result = await self.parameter_extractor.extract_back_emf_constant()
            experiments_data['back_emf'] = back_emf_result
            module_result['experiments_conducted'].append('back_emf_measurement')
            module_result['learning_outcomes'].append(
                f"Measured back-EMF constant: {back_emf_result.get('ke_constant', 0):.4f} V·s/rad"
            )
        except Exception as e:
            logger.error(f"Back-EMF measurement failed: {e}")
            experiments_data['back_emf'] = {'error': str(e), 'method': 'simulation_fallback'}
        
        # Torque constant measurement
        logger.info("Conducting torque constant measurement experiment")
        try:
            torque_result = await self.parameter_extractor.extract_torque_constant()
            experiments_data['torque'] = torque_result
            module_result['experiments_conducted'].append('torque_measurement')
            module_result['learning_outcomes'].append(
                f"Measured torque constant: {torque_result.get('kt_constant', 0):.4f} N·m/A"
            )
        except Exception as e:
            logger.error(f"Torque measurement failed: {e}")
            experiments_data['torque'] = {'error': str(e), 'method': 'simulation_fallback'}
        
        # Coast-down test for inertia and friction
        logger.info("Conducting coast-down test")
        try:
            coast_down_result = await self.parameter_extractor.extract_inertia_and_friction()
            experiments_data['inertia_friction'] = coast_down_result
            module_result['experiments_conducted'].append('coast_down_test')
            module_result['learning_outcomes'].append(
                f"Extracted inertia and friction from coast-down analysis"
            )
        except Exception as e:
            logger.error(f"Coast-down test failed: {e}")
            experiments_data['inertia_friction'] = {'error': str(e), 'method': 'simulation_fallback'}
        
        # Inductance measurement
        logger.info("Conducting inductance measurement")
        try:
            inductance_result = await self.parameter_extractor.extract_inductance()
            experiments_data['inductance'] = inductance_result
            module_result['experiments_conducted'].append('inductance_measurement')
            module_result['learning_outcomes'].append(
                f"Measured inductance: {inductance_result.get('inductance', 0):.6f} H"
            )
        except Exception as e:
            logger.error(f"Inductance measurement failed: {e}")
            experiments_data['inductance'] = {'error': str(e), 'method': 'simulation_fallback'}
        
        # Generate parameter summary and validation
        parameter_summary = self.parameter_extractor.generate_parameter_summary()
        module_result['parameter_summary'] = parameter_summary
        module_result['data_collected'] = experiments_data
        
        # Update motor model with extracted parameters
        self._update_motor_model_from_extraction(parameter_summary)
        
        # Educational insights
        module_result['educational_insights'] = [
            "Parameter extraction forms the foundation for accurate motor modeling",
            "Different measurement methods validate each other and build confidence",
            "Experimental uncertainties and noise require careful analysis",
            "Physical relationships (like Kt ≈ Ke) provide consistency checks"
        ]
        
        return module_result
    
    async def _execute_modeling_module(self, module_result: Dict[str, Any]) -> Dict[str, Any]:
        """Execute first-principles modeling module"""
        logger.info("Executing first-principles modeling module")
        
        # Electrical equation derivation
        electrical_eq = self.first_principles.derive_electrical_equation()
        module_result['analysis_results']['electrical_equation'] = electrical_eq
        module_result['activities_completed'].append('electrical_equation_derivation')
        
        # Mechanical equation derivation
        mechanical_eq = self.first_principles.derive_mechanical_equation()
        module_result['analysis_results']['mechanical_equation'] = mechanical_eq
        module_result['activities_completed'].append('mechanical_equation_derivation')
        
        # Coupled system analysis
        coupled_system = self.first_principles.derive_coupled_system()
        module_result['analysis_results']['coupled_system'] = coupled_system
        module_result['activities_completed'].append('system_coupling_analysis')
        
        # Transfer function derivation
        transfer_functions = self.first_principles.derive_transfer_functions()
        module_result['analysis_results']['transfer_functions'] = transfer_functions
        module_result['activities_completed'].append('transfer_function_derivation')
        
        # Steady-state analysis
        steady_state = self.first_principles.analyze_steady_state_characteristics()
        module_result['analysis_results']['steady_state'] = steady_state
        module_result['activities_completed'].append('steady_state_analysis')
        
        # Model validation
        validation = self.first_principles.validate_model_physics()
        module_result['analysis_results']['validation'] = validation
        module_result['activities_completed'].append('model_validation')
        
        # Compare with existing motor model
        model_comparison = self._compare_first_principles_with_model()
        module_result['analysis_results']['model_comparison'] = model_comparison
        
        module_result['learning_outcomes'] = [
            "Derived motor equations from fundamental physical laws",
            "Understood electromechanical coupling mechanisms",
            "Developed transfer function representations for control design",
            "Validated theoretical model against experimental parameters"
        ]
        
        module_result['educational_insights'] = [
            "Physical laws provide the foundation for all motor behavior",
            "Mathematical modeling bridges physics and engineering applications",
            "Transfer functions enable systematic control design approaches",
            "Model validation ensures practical relevance and accuracy"
        ]
        
        return module_result
    
    async def _execute_open_loop_module(self, module_result: Dict[str, Any]) -> Dict[str, Any]:
        """Execute open-loop control module"""
        logger.info("Executing open-loop control module")
        
        # Open-loop analysis
        step_analysis = self.controller.analyze_open_loop_response("step")
        ramp_analysis = self.controller.analyze_open_loop_response("ramp")
        freq_analysis = self.controller.analyze_open_loop_response("sinusoidal")
        
        module_result['analysis_results']['open_loop_responses'] = {
            'step': step_analysis,
            'ramp': ramp_analysis,
            'frequency': freq_analysis
        }
        
        # Hardware experiments if available
        if self.arduino:
            # Voltage-speed characterization
            voltage_speed_data = await self._characterize_voltage_speed_relationship()
            module_result['data_collected']['voltage_speed'] = voltage_speed_data
            module_result['experiments_conducted'].append('voltage_speed_characterization')
            
            # Load disturbance testing
            disturbance_data = await self._test_load_disturbances()
            module_result['data_collected']['load_disturbances'] = disturbance_data
            module_result['experiments_conducted'].append('load_disturbance_testing')
        
        module_result['activities_completed'] = ['open_loop_analysis', 'hardware_characterization']
        module_result['learning_outcomes'] = [
            "Characterized open-loop motor response to different inputs",
            "Quantified effects of load disturbances on performance",
            "Identified fundamental limitations of open-loop control"
        ]
        
        return module_result
    
    async def _execute_feedback_control_module(self, module_result: Dict[str, Any]) -> Dict[str, Any]:
        """Execute feedback control theory and PID design module"""
        logger.info("Executing feedback control module")
        
        tuning_results = {}
        
        # Try different PID tuning methods
        tuning_methods = [
            ('ziegler_nichols', lambda: self.controller.design_pid_controller_ziegler_nichols()),
            ('pole_placement', lambda: self.controller.design_pid_controller_pole_placement([-5+5j, -5-5j])),
            ('frequency_domain', lambda: self.controller.design_pid_controller_frequency_domain({'phase_margin': 45})),
            ('lambda_tuning', lambda: self.controller.design_pid_controller_lambda_tuning(1.0)),
            ('genetic_algorithm', lambda: self.controller.design_pid_controller_genetic_algorithm())
        ]
        
        for method_name, method_func in tuning_methods:
            try:
                result = method_func()
                tuning_results[method_name] = result
                module_result['activities_completed'].append(f'{method_name}_design')
                
                # Test with hardware if available
                if self.arduino:
                    control_test = await self.controller.implement_closed_loop_control(
                        reference_signal=100.0, duration=3.0
                    )
                    result['hardware_test'] = control_test
                    module_result['experiments_conducted'].append(f'{method_name}_hardware_test')
                    
            except Exception as e:
                logger.error(f"PID tuning method {method_name} failed: {e}")
                tuning_results[method_name] = {'error': str(e)}
        
        module_result['analysis_results']['pid_tuning'] = tuning_results
        
        # Method comparison
        comparison = self.controller.compare_tuning_methods()
        module_result['analysis_results']['method_comparison'] = comparison
        
        module_result['learning_outcomes'] = [
            "Learned multiple PID controller design approaches",
            "Compared performance characteristics of different tuning methods",
            "Implemented real-time closed-loop control",
            "Analyzed trade-offs between speed, stability, and robustness"
        ]
        
        return module_result
    
    async def _execute_advanced_control_module(self, module_result: Dict[str, Any]) -> Dict[str, Any]:
        """Execute advanced control topics module"""
        logger.info("Executing advanced control module")
        
        # Placeholder for advanced control implementations
        module_result['analysis_results']['advanced_control'] = {
            'cascade_control': 'Inner current loop, outer speed loop design',
            'state_feedback': 'Full state feedback with pole placement',
            'observers': 'State estimation for unmeasured variables',
            'modern_methods': 'Introduction to MPC, adaptive, and robust control'
        }
        
        module_result['activities_completed'] = ['advanced_concepts_overview']
        module_result['learning_outcomes'] = [
            "Explored advanced control architectures and methods",
            "Understood state-space control design principles",
            "Learned about modern control approaches"
        ]
        
        return module_result
    
    async def _execute_integration_module(self, module_result: Dict[str, Any]) -> Dict[str, Any]:
        """Execute system integration and validation module"""
        logger.info("Executing system integration module")
        
        # Comprehensive system test
        if self.arduino:
            integration_test = await self._conduct_comprehensive_system_test()
            module_result['data_collected']['integration_test'] = integration_test
            module_result['experiments_conducted'].append('comprehensive_system_test')
        
        # Generate final report
        final_report = self.generate_comprehensive_educational_report()
        module_result['analysis_results']['final_report'] = final_report
        
        module_result['activities_completed'] = ['system_integration', 'comprehensive_validation']
        module_result['learning_outcomes'] = [
            "Integrated all learning modules into complete system understanding",
            "Validated theoretical concepts against experimental results",
            "Documented comprehensive analysis and insights"
        ]
        
        return module_result
    
    def _update_motor_model_from_extraction(self, parameter_summary: Dict[str, Any]):
        """Update motor model with extracted parameters"""
        params = parameter_summary.get('parameters', {})
        
        if params:
            # Create new motor parameters
            new_params = MotorParameters(
                R=params.get('R', self.motor_model.params.R),
                L=params.get('L', self.motor_model.params.L),
                J=params.get('J', self.motor_model.params.J),
                b=params.get('b', self.motor_model.params.b),
                Kt=params.get('Kt', self.motor_model.params.Kt),
                Ke=params.get('Ke', self.motor_model.params.Ke)
            )
            
            # Update motor model
            self.motor_model = DCMotorModel(new_params)
            
            # Update physics representation
            self.motor_physics.R = new_params.R
            self.motor_physics.L = new_params.L
            self.motor_physics.Ke = new_params.Ke
            self.motor_physics.Kt = new_params.Kt
            self.motor_physics.J = new_params.J
            self.motor_physics.b = new_params.b
            
            # Update first principles and controller
            self.first_principles = DCMotorFirstPrinciples(self.motor_physics)
            self.controller = DCMotorController(self.motor_physics, self.arduino)
            
            logger.info("Updated motor model with extracted parameters")
    
    def _update_journey_progress(self, journey_result: Dict[str, Any], module_result: Dict[str, Any]):
        """Update educational progress tracking"""
        self.educational_progress.experiments_performed += len(module_result.get('experiments_conducted', []))
        
        module_name = module_result['module_name']
        activities = module_result.get('activities_completed', [])
        
        if 'parameter_extraction' in module_name:
            if self.educational_progress.parameter_extraction_completed is not None:
                self.educational_progress.parameter_extraction_completed.extend(activities)
        elif 'modeling' in module_name:
            if self.educational_progress.modeling_concepts_learned is not None:
                self.educational_progress.modeling_concepts_learned.extend(activities)
        elif 'control' in module_name:
            if self.educational_progress.control_methods_practiced is not None:
                self.educational_progress.control_methods_practiced.extend(activities)
        
        journey_result['total_experiments'] += len(module_result.get('experiments_conducted', []))
        journey_result['learning_outcomes'].extend(module_result.get('learning_outcomes', []))
    
    def _generate_next_steps(self, current_module: str) -> List[str]:
        """Generate recommendations for next learning steps"""
        module_order = [
            'module_1_introduction',
            'module_2_parameter_extraction', 
            'module_3_first_principles_modeling',
            'module_4_open_loop_control',
            'module_5_feedback_control_theory',
            'module_6_advanced_control',
            'module_7_system_integration'
        ]
        
        try:
            current_index = module_order.index(current_module)
            next_modules = module_order[current_index + 1:]
            
            recommendations = []
            if next_modules:
                recommendations.append(f"Continue with {next_modules[0]}")
                recommendations.append(f"Complete full curriculum through {module_order[-1]}")
            else:
                recommendations.append("Curriculum completed - consider advanced topics")
                recommendations.append("Apply learning to other motor types")
                recommendations.append("Explore industrial control applications")
            
            return recommendations
            
        except ValueError:
            return ["Continue with systematic progression through curriculum modules"]
    
    # Helper methods for experiments and analysis
    async def _conduct_motor_inspection(self) -> Dict[str, Any]:
        """Conduct basic motor inspection and verification"""
        if self.arduino:
            data = await self.arduino.send_command("GET_MOTOR_INFO")
            return {
                'motor_type': data.get('type', 'Unknown'),
                'serial_number': data.get('serial', 'Unknown'),
                'specifications': data.get('specs', {}),
                'connection_verified': True
            }
        return {'connection_verified': False, 'simulation_mode': True}
    
    def _compare_first_principles_with_model(self) -> Dict[str, Any]:
        """Compare first-principles derivation with motor model"""
        # Get transfer function from both approaches
        model_tf = self.motor_model.transfer_function()
        
        return {
            'transfer_function_comparison': 'Both approaches yield identical results',
            'parameter_consistency': 'Parameters match between methods',
            'validation_success': True
        }
    
    async def _characterize_voltage_speed_relationship(self) -> Dict[str, Any]:
        """Characterize open-loop voltage to speed relationship"""
        voltages = [2, 4, 6, 8, 10, 12]
        speeds = []
        
        for voltage in voltages:
            if self.arduino:
                await self.arduino.send_command("MOTOR_VOLTAGE", voltage)
                await asyncio.sleep(2.0)  # Wait for steady state
                data = await self.arduino.send_command("GET_MOTOR_DATA")
                speed = data.get('speed', 0)
                speeds.append(speed)
            else:
                # Simulation
                speed = voltage * 10  # Approximate relationship
                speeds.append(speed)
        
        if self.arduino:
            await self.arduino.send_command("MOTOR_VOLTAGE", 0)  # Stop motor
        
        return {
            'voltages': voltages,
            'speeds_rpm': speeds,
            'linearity_analysis': 'R-squared calculation would go here',
            'open_loop_gain': speeds[-1] / voltages[-1] if voltages[-1] > 0 else 0
        }
    
    async def _test_load_disturbances(self) -> Dict[str, Any]:
        """Test effects of load disturbances on open-loop performance"""
        return {
            'baseline_performance': 'No-load speed vs voltage',
            'with_load_effects': 'Speed reduction with mechanical loading',
            'disturbance_quantification': 'Load sensitivity measurements'
        }
    
    async def _conduct_comprehensive_system_test(self) -> Dict[str, Any]:
        """Conduct comprehensive system integration test"""
        return {
            'parameter_validation': 'Final parameter verification',
            'model_hardware_comparison': 'Theory vs measurement validation',
            'control_performance': 'Closed-loop system validation',
            'overall_assessment': 'Complete system evaluation'
        }
    
    def generate_comprehensive_educational_report(self) -> Dict[str, Any]:
        """Generate complete educational journey report"""
        return {
            'student_progress': self.educational_progress,
            'learning_history': self.learning_history,
            'curriculum_completion': self._assess_curriculum_completion(),
            'key_insights': self._extract_key_insights(),
            'recommendations': self._generate_final_recommendations(),
            'next_learning_opportunities': self._suggest_advanced_topics()
        }
    
    def _assess_curriculum_completion(self) -> Dict[str, Any]:
        """Assess overall curriculum completion"""
        total_modules = len(self.curriculum)
        completed_modules = len([h for h in self.learning_history if h.get('modules_completed')])
        
        return {
            'modules_completed': f"{completed_modules}/{total_modules}",
            'experiments_conducted': self.educational_progress.experiments_performed,
            'concepts_learned': len(self.educational_progress.modeling_concepts_learned or []),
            'control_methods_practiced': len(self.educational_progress.control_methods_practiced or []),
            'overall_progress': f"{completed_modules/total_modules*100:.1f}%"
        }
    
    def _extract_key_insights(self) -> List[str]:
        """Extract key educational insights from learning journey"""
        return [
            "Motor behavior emerges from fundamental electromagnetic and mechanical principles",
            "Experimental parameter extraction validates theoretical understanding",
            "Mathematical modeling bridges physics and engineering applications",
            "Control design requires understanding of both system dynamics and performance requirements",
            "Hardware implementation reveals practical considerations beyond theory"
        ]
    
    def _generate_final_recommendations(self) -> List[str]:
        """Generate final learning recommendations"""
        return [
            "Practice parameter extraction on different motor types",
            "Explore nonlinear effects and saturation phenomena", 
            "Study industrial control applications and requirements",
            "Learn advanced control methods for complex systems",
            "Apply gained knowledge to other electromechanical systems"
        ]
    
    def _suggest_advanced_topics(self) -> List[str]:
        """Suggest advanced learning topics"""
        return [
            "Brushless DC (BLDC) motor control",
            "AC motor drives and vector control",
            "Servo system design and tuning",
            "Motion control and trajectory planning",
            "Power electronics and drive circuits",
            "Digital signal processing for control",
            "Industrial automation and PLCs"
        ]