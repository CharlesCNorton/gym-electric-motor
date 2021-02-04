from gym_electric_motor.core import ElectricMotorEnvironment, ReferenceGenerator, RewardFunction, \
    ElectricMotorVisualization
from gym_electric_motor.physical_systems.physical_systems import DcMotorSystem
from gym_electric_motor.visualization import MotorDashboard
from gym_electric_motor.reference_generators import WienerProcessReferenceGenerator, MultipleReferenceGenerator
from gym_electric_motor import physical_systems as ps
from gym_electric_motor.reward_functions import WeightedSumOfErrors
from gym_electric_motor.utils import initialize


class FiniteSpeedControlDcExternallyExcitedMotorEnv(ElectricMotorEnvironment):
    """
        Description:
            Environment to simulate a finite control set speed controlled externally excited DC Motor

        Key:
            `Finite-SC-ExtExDc-v0`

        Default Components:
            Supply: IdealVoltageSupply
            Converter: FiniteMultiConverter(FiniteFourQuadrantConverter, FiniteOneQuadrantConverter)
            Motor: DcExternallyExcitedMotor
            Load: PolynomialStaticLoad
            Ode-Solver: EulerSolver
            Noise: None

            Reference Generator:
                WienerProcessReferenceGenerator
                    Reference Quantity. 'omega'

            Reward Function:
                WeightedSumOfErrors: reward_weights 'omega' = 1

            Visualization:
                MotorDashboard: omega and action plots

            Constraints:
                Current Limit on 'i_a' and 'i_e'

        Control Cycle Time:
            tau = 1e-5 seconds

        State Variables:
            ``['omega' , 'torque', 'i_a', 'i_e', 'u_a', 'u_e', 'u_sup']``

        Observation Space:
            Type: Tuple(State_Space, Reference_Space)

        State Space:
            Box(low=[-1, -1, -1, -1, -1, -1, 0], high=[1, 1, 1, 1, 1, 1, 1])

        Reference Space:
            Box(low=[-1], high=[1])

        Action Space:
            Type: Discrete(8)

        Starting State:
            Zeros on all state variables.

        Episode Termination:
            Termination if current limits are violated.
        """
    def __init__(self, supply=None, converter=None, motor=None, load=None, ode_solver=None, noise_generator=None,
                 reward_function=None, reference_generator=None, visualization=None, state_filter=None, callbacks=(),
                 constraints=('i_a', 'i_e'), calc_jacobian=True, tau=1e-5):
        """
        Args:
            supply(env-arg): Specification of the supply to be used in the environment
            converter(env-arg): Specification of the converter to be used in the environment
            motor(env-arg): Specification of the motor to be used in the environment
            load(env-arg): Specification of the load to be used in the environment
            ode_solver(env-arg): Specification of the ode_solver to be used in the environment
            noise_generator(env-arg): Specification of the noise_generator to be used in the environment
            reward_function(env-arg: Specification of the reward_function to be used in the environment
            reference_generator(env-arg): Specification of the reference generator to be used in the environment
            visualization(env-arg): Specification of the visualization to be used in the environment
            constraints(iterable(str/Constraint)): All Constraints of the environment.
                - str: A LimitConstraints for states (episode terminates, if the quantity exceeds the limit)
                 can be directly specified by passing the state name here (e.g. 'i', 'omega')
                 - instance of Constraint: More complex constraints (e.g. the SquaredConstraint can be initialized and
                 passed to the environment.
            calc_jacobian(bool): Flag, if the jacobian of the environment shall be taken into account during the
                simulation. This may lead to speed improvements. Default: True
            tau(float): Duration of one control step in seconds. Default: 1e-5.
            state_filter(list(str)): List of states that shall be returned to the agent. Default: None (no filter)
            callbacks(list(Callback)): Callbacks for user interaction.

        Note on the env-arg type:
            All parameters of type env-arg can be selected as one of the following types:
                - instance: Pass an already instantiated object derived from the corresponding base class
                    (e.g. reward_function=MyRewardFunction()). This is directly used in the environment.
                - dict: Pass a dict to update the default parameters of the default type.
                    (e.g. visualization=dict(state_plots=('omega', 'u')))
                - str: Pass a string out of the registered classes to select a different class for the component.
                    This class is then initialized with its default parameters.
                    The available strings can be looked up in the documentation. (e.g. converter='Disc-2QC')
        """
        default_subconverters = (ps.FiniteFourQuadrantConverter(), ps.FiniteOneQuadrantConverter)

        physical_system = DcMotorSystem(
            supply=initialize(ps.VoltageSupply, supply, ps.IdealVoltageSupply, dict(u_nominal=420.0)),
            converter=initialize(
                ps.PowerElectronicConverter,
                converter,
                ps.FiniteMultiConverter,
                dict(subconverters=default_subconverters)),
            motor=initialize(ps.ElectricMotor, motor, ps.DcExternallyExcitedMotor, dict()),
            load=initialize(ps.MechanicalLoad, load, ps.PolynomialStaticLoad, dict(
                load_parameter=dict(a=0.01, b=0.01, c=0.0)
            )),
            ode_solver=initialize(ps.OdeSolver, ode_solver, ps.EulerSolver, dict()),
            noise_generator=initialize(ps.NoiseGenerator, noise_generator, ps.NoiseGenerator, dict()),
            calc_jacobian=calc_jacobian,
            tau=tau
        )
        reference_generator = initialize(
            ReferenceGenerator, reference_generator, WienerProcessReferenceGenerator, dict(reference_state='omega')
        )
        reward_function = initialize(
            RewardFunction, reward_function, WeightedSumOfErrors, dict(reward_weights=dict(omega=1.0))
        )
        visualization = initialize(
            ElectricMotorVisualization, visualization, MotorDashboard, dict(state_plots=('omega',), action_plots=(0,)))
        super().__init__(
            physical_system=physical_system, reference_generator=reference_generator, reward_function=reward_function,
            constraints=constraints, visualization=visualization, state_filter=state_filter, callbacks=callbacks
        )


class ContSpeedControlDcExternallyExcitedMotorEnv(ElectricMotorEnvironment):
    """
        Description:
            Environment to simulate a continuously speed controlled externally excited DC Motor
1
        Key:
            `Cont-SC-ExtExDc-v0`

        Default Components:
            Supply: IdealVoltageSupply
            Converter: ContMultiConverter(ContFourQuadrantConverter, ContOneQuadrantConverter)
            Motor: DcExternallyExcitedMotor
            Load: PolynomialStaticLoad
            Ode-Solver: EulerSolver
            Noise: None

            Reference Generator:
                WienerProcessReferenceGenerator
                    Reference Quantity. 'omega'

            Reward Function:
                WeightedSumOfErrors: reward_weights 'omega' = 1

            Visualization:
                MotorDashboard: omega and action plots

            Constraints:
                Current Limit on 'i_a' and 'i_e'

        Control Cycle Time:
            tau = 1e-4 seconds

        State Variables:
            ``['omega' , 'torque', 'i_a', 'i_e', 'u_a', 'u_e', 'u_sup']``

        Observation Space:
            Type: Tuple(State_Space, Reference_Space)

        State Space:
            Box(low=[-1, -1, -1, -1, -1, -1, 0], high=[1, 1, 1, 1, 1, 1, 1])

        Reference Space:
            Box(low=[-1], high=[1])

        Action Space:
            Box(low=[-1, 0], high=[1, 1])

        Starting State:
            Zeros on all state variables.

        Episode Termination:
            Termination if current limits are violated.
        """
    def __init__(self, supply=None, converter=None, motor=None, load=None, ode_solver=None, noise_generator=None,
                 reward_function=None, reference_generator=None, visualization=None, state_filter=None, callbacks=(),
                 constraints=('i_a', 'i_e'), calc_jacobian=True, tau=1e-4):
        """
        Args:
            supply(env-arg): Specification of the supply to be used in the environment
            converter(env-arg): Specification of the converter to be used in the environment
            motor(env-arg): Specification of the motor to be used in the environment
            load(env-arg): Specification of the load to be used in the environment
            ode_solver(env-arg): Specification of the ode_solver to be used in the environment
            noise_generator(env-arg): Specification of the noise_generator to be used in the environment
            reward_function(env-arg: Specification of the reward_function to be used in the environment
            reference_generator(env-arg): Specification of the reference generator to be used in the environment
            visualization(env-arg): Specification of the visualization to be used in the environment
            constraints(iterable(str/Constraint)): All Constraints of the environment.
                - str: A LimitConstraints for states (episode terminates, if the quantity exceeds the limit)
                 can be directly specified by passing the state name here (e.g. 'i_a', 'omega')
                 - instance of Constraint: More complex constraints (e.g. the SquaredConstraint can be initialized and
                 passed to the environment.
            calc_jacobian(bool): Flag, if the jacobian of the environment shall be taken into account during the
                simulation. This may lead to speed improvements. Default: True
            tau(float): Duration of one control step in seconds. Default: 1e-4.
            state_filter(list(str)): List of states that shall be returned to the agent. Default: None (no filter)
            callbacks(list(Callback)): Callbacks for user interaction.

        Note on the env-arg type:
            All parameters of type env-arg can be selected as one of the following types:
                - instance: Pass an already instantiated object derived from the corresponding base class
                    (e.g. reward_function=MyRewardFunction()). This is directly used in the environment.
                - dict: Pass a dict to update the default parameters of the default type.
                    (e.g. visualization=dict(state_plots=('omega', 'u_a')))
                - str: Pass a string out of the registered classes to select a different class for the component.
                    This class is then initialized with its default parameters.
                    The available strings can be looked up in the documentation. (e.g. converter='Disc-2QC')
        """
        default_subconverters = (ps.ContFourQuadrantConverter(), ps.ContOneQuadrantConverter())
        physical_system = DcMotorSystem(
            supply=initialize(ps.VoltageSupply, supply, ps.IdealVoltageSupply, dict(u_nominal=420.0)),
            converter=initialize(
                ps.PowerElectronicConverter,
                converter,
                ps.ContMultiConverter,
                dict(subconverters=default_subconverters)),
            motor=initialize(ps.ElectricMotor, motor, ps.DcExternallyExcitedMotor, dict()),
            load=initialize(ps.MechanicalLoad, load, ps.PolynomialStaticLoad, dict(
                load_parameter=dict(a=0.01, b=0.01, c=0.0)
            )),
            ode_solver=initialize(ps.OdeSolver, ode_solver, ps.EulerSolver, dict()),
            noise_generator=initialize(ps.NoiseGenerator, noise_generator, ps.NoiseGenerator, dict()),
            calc_jacobian=calc_jacobian,
            tau=tau
        )
        reference_generator = initialize(
            ReferenceGenerator, reference_generator, WienerProcessReferenceGenerator, dict(reference_state='omega')
        )
        reward_function = initialize(
            RewardFunction, reward_function, WeightedSumOfErrors, dict(reward_weights=dict(omega=1.0))
        )
        visualization = initialize(
            ElectricMotorVisualization, visualization, MotorDashboard, dict(state_plots=('omega',), action_plots=(0,)))
        super().__init__(
            physical_system=physical_system, reference_generator=reference_generator, reward_function=reward_function,
            constraints=constraints, visualization=visualization, state_filter=state_filter, callbacks=callbacks
        )


class FiniteTorqueControlDcExternallyExcitedMotorEnv(ElectricMotorEnvironment):
    """
        Description:
            Environment to simulate a finite control set torque controlled externally excited DC Motor

        Key:
            `Finite-TC-ExtExDc-v0`

        Default Components:
            - Supply: IdealVoltageSupply
            - Converter: FiniteMultiConverter(FiniteFourQuadrantConverter, FiniteOneQuadrantConverter)
            - Motor: DcExternallyExcitedMotor
            - Load: ConstantSpeedLoad
            - Ode-Solver: EulerSolver
            - Noise: None

            Reference Generator:
                WienerProcessReferenceGenerator
                    Reference Quantity. 'torque'

            Reward Function:
                WeightedSumOfErrors: reward_weights 'torque' = 1

            Visualization:
                MotorDashboard: torque and action plots

            Constraints:
                Current Limit on 'i_a' and 'i_e'

        Control Cycle Time:
            tau = 1e-5 seconds

        State Variables:
            ``['omega' , 'torque', 'i_a', 'i_e', 'u_a', 'u_e', 'u_sup']``

        Observation Space:
            Type: Tuple(State_Space, Reference_Space)

        State Space:
            Box(low=[-1, -1, -1, -1, -1, -1, 0], high=[1, 1, 1, 1, 1, 1, 1])

        Reference Space:
            Box(low=[-1], high=[1])

        Action Space:
            Discrete(8)

        Starting State:
            Zeros on all state variables.

        Episode Termination:
            Termination if current limits are violated.
        """
    def __init__(self, supply=None, converter=None, motor=None, load=None, ode_solver=None, noise_generator=None,
                 reward_function=None, reference_generator=None, visualization=None, state_filter=None, callbacks=(),
                 constraints=('i_a', 'i_e'), calc_jacobian=True, tau=1e-5):
        """
        Args:
            supply(env-arg): Specification of the supply to be used in the environment
            converter(env-arg): Specification of the converter to be used in the environment
            motor(env-arg): Specification of the motor to be used in the environment
            load(env-arg): Specification of the load to be used in the environment
            ode_solver(env-arg): Specification of the ode_solver to be used in the environment
            noise_generator(env-arg): Specification of the noise_generator to be used in the environment
            reward_function(env-arg: Specification of the reward_function to be used in the environment
            reference_generator(env-arg): Specification of the reference generator to be used in the environment
            visualization(env-arg): Specification of the visualization to be used in the environment
            constraints(iterable(str/Constraint)): All Constraints of the environment. \n
                - str: A LimitConstraints for states (episode terminates, if the quantity exceeds the limit) can
                 be directly specified by passing the state name here (e.g. 'i', 'omega') \n
                - instance of Constraint: More complex constraints (e.g. the SquaredConstraint) can be initialized and
                 passed to the environment.
            calc_jacobian(bool): Flag, if the jacobian of the environment shall be taken into account during the
                simulation. This may lead to speed improvements. Default: True
            tau(float): Duration of one control step in seconds. Default: 1e-5.
            state_filter(list(str)): List of states that shall be returned to the agent. Default: None (no filter)
            callbacks(list(Callback)): Callbacks for user interaction.

        Note on the env-arg type:
            All parameters of type env-arg can be selected as one of the following types:
                - instance: Pass an already instantiated object derived from the corresponding base class
                    (e.g. reward_function=MyRewardFunction()). This is directly used in the environment.
                - dict: Pass a dict to update the default parameters of the default type.
                    (e.g. visualization=dict(state_plots=('omega', 'u')))
                - str: Pass a string out of the registered classes to select a different class for the component.
                    This class is then initialized with its default parameters.
                    The available strings can be looked up in the documentation. (e.g. converter='Disc-2QC')
        """
        default_subconverters = (ps.FiniteFourQuadrantConverter(), ps.FiniteOneQuadrantConverter())

        physical_system = DcMotorSystem(
            supply=initialize(ps.VoltageSupply, supply, ps.IdealVoltageSupply, dict(u_nominal=420.0)),
            converter=initialize(
                ps.PowerElectronicConverter,
                converter,
                ps.FiniteMultiConverter,
                dict(subconverters=default_subconverters)),
            motor=initialize(ps.ElectricMotor, motor, ps.DcExternallyExcitedMotor, dict()),
            load=initialize(ps.MechanicalLoad, load, ps.ConstantSpeedLoad, dict(omega_fixed=100.0)),
            ode_solver=initialize(ps.OdeSolver, ode_solver, ps.EulerSolver, dict()),
            noise_generator=initialize(ps.NoiseGenerator, noise_generator, ps.NoiseGenerator, dict()),
            calc_jacobian=calc_jacobian,
            tau=tau
        )
        reference_generator = initialize(
            ReferenceGenerator, reference_generator, WienerProcessReferenceGenerator, dict(reference_state='torque')
        )
        reward_function = initialize(
            RewardFunction, reward_function, WeightedSumOfErrors, dict(reward_weights=dict(torque=1.0))
        )
        visualization = initialize(
            ElectricMotorVisualization, visualization, MotorDashboard, dict(state_plots=('torque',), action_plots=(0,)))
        super().__init__(
            physical_system=physical_system, reference_generator=reference_generator, reward_function=reward_function,
            constraints=constraints, visualization=visualization, state_filter=state_filter, callbacks=callbacks
        )


class ContTorqueControlDcExternallyExcitedMotorEnv(ElectricMotorEnvironment):
    """
    Description:
        Environment to simulate a continuous control set torque controlled externally excited DC Motor

    Key:
        `Cont-TC-ExtExDc-v0`

    Default Components:
        - Supply: IdealVoltageSupply
        - Converter: ContMultiConverter(ContFourQuadrantConverter, ContOneQuadrantConverter)
        - Motor: DcExternallyExcitedMotor
        - Load: ConstantSpeedLoad
        - Ode-Solver: EulerSolver
        - Noise: None

        Reference Generator:
            WienerProcessReferenceGenerator
                Reference Quantity. 'torque'

        Reward Function:
            WeightedSumOfErrors: reward_weights 'torque' = 1

        Visualization:
            MotorDashboard: torque and action plots

        Constraints:
            Current Limit on 'i_a' and 'i_e'

    Control Cycle Time:
        tau = 1e-4 seconds

    State Variables:
        ``['omega' , 'torque', 'i_a', 'i_e', 'u_a', 'u_e', 'u_sup']``

    Observation Space:
        Type: Tuple(State_Space, Reference_Space)

    State Space:
        Box(low=[-1, -1, -1, -1, -1, -1, 0], high=[1, 1, 1, 1, 1, 1, 1])

    Reference Space:
        Box(low=[-1], high=[1])

    Action Space:
        Box(low=[-1,0], high=[1,1])

    Starting State:
        Zeros on all state variables.

    Episode Termination:
        Termination if current limits are violated.
    """

    def __init__(self, supply=None, converter=None, motor=None, load=None, ode_solver=None, noise_generator=None,
                 reward_function=None, reference_generator=None, visualization=None, state_filter=None, callbacks=(),
                 constraints=('i_a', 'i_e',), calc_jacobian=True, tau=1e-4):
        """
        Args:
            supply(env-arg): Specification of the supply to be used in the environment
            converter(env-arg): Specification of the converter to be used in the environment
            motor(env-arg): Specification of the motor to be used in the environment
            load(env-arg): Specification of the load to be used in the environment
            ode_solver(env-arg): Specification of the ode_solver to be used in the environment
            noise_generator(env-arg): Specification of the noise_generator to be used in the environment
            reward_function(env-arg: Specification of the reward_function to be used in the environment
            reference_generator(env-arg): Specification of the reference generator to be used in the environment
            visualization(env-arg): Specification of the visualization to be used in the environment
            constraints(iterable(str/Constraint)): All Constraints of the environment.
                - str: A LimitConstraints for states (episode terminates, if the quantity exceeds the limit)
                 can be directly specified by passing the state name here (e.g. 'i', 'omega')
                 - instance of Constraint: More complex constraints (e.g. the SquaredConstraint can be initialized and
                 passed to the environment.
            calc_jacobian(bool): Flag, if the jacobian of the environment shall be taken into account during the
                simulation. This may lead to speed improvements. Default: True
            tau(float): Duration of one control step in seconds. Default: 1e-5.
            state_filter(list(str)): List of states that shall be returned to the agent. Default: None (no filter)
            callbacks(list(Callback)): Callbacks for user interaction.

        Note on the env-arg type:
            All parameters of type env-arg can be selected as one of the following types:
                - instance: Pass an already instantiated object derived from the corresponding base class
                    (e.g. reward_function=MyRewardFunction()). This is directly used in the environment.
                - dict: Pass a dict to update the default parameters of the default type.
                    (e.g. visualization=dict(state_plots=('omega', 'u')))
                - str: Pass a string out of the registered classes to select a different class for the component.
                    This class is then initialized with its default parameters.
                    The available strings can be looked up in the documentation. (e.g. converter='Finite-2QC')
        """
        default_subconverters = (ps.ContFourQuadrantConverter(), ps.ContOneQuadrantConverter())
        physical_system = DcMotorSystem(
            supply=initialize(ps.VoltageSupply, supply, ps.IdealVoltageSupply, dict(u_nominal=420.0)),
            converter=initialize(
                ps.PowerElectronicConverter,
                converter,
                ps.ContMultiConverter,
                dict(subconverters=default_subconverters)
            ),
            motor=initialize(ps.ElectricMotor, motor, ps.DcPermanentlyExcitedMotor, dict()),
            load=initialize(ps.MechanicalLoad, load, ps.ConstantSpeedLoad, dict(omega_fixed=100.0)),
            ode_solver=initialize(ps.OdeSolver, ode_solver, ps.EulerSolver, dict()),
            noise_generator=initialize(ps.NoiseGenerator, noise_generator, ps.NoiseGenerator, dict()),
            calc_jacobian=calc_jacobian,
            tau=tau
        )
        reference_generator = initialize(
            ReferenceGenerator, reference_generator, WienerProcessReferenceGenerator, dict(reference_state='torque')
        )
        reward_function = initialize(
            RewardFunction, reward_function, WeightedSumOfErrors, dict(reward_weights=dict(torque=1.0))
        )
        visualization = initialize(
            ElectricMotorVisualization, visualization, MotorDashboard, dict(state_plots=('torque',), action_plots=(0,)))
        super().__init__(
            physical_system=physical_system, reference_generator=reference_generator, reward_function=reward_function,
            constraints=constraints, visualization=visualization, state_filter=state_filter, callbacks=callbacks
        )


class FiniteCurrentControlDcExternallyExcitedMotorEnv(ElectricMotorEnvironment):
    """
        Description:
            Environment to simulate a finite control set current controlled externally excited DC Motor

        Key:
            `Finite-CC-ExtExDc-v0`

        Default Components:
            - Supply: IdealVoltageSupply
            - Converter: FiniteMultiConverter(FiniteFourQuadrantConverter, FiniteOneQuadrantConverter)
            - Motor: DcExternallyExcitedMotor
            - Load: ConstantSpeedLoad
            - Ode-Solver: EulerSolver
            - Noise: None

            Reference Generator:
                WienerProcessReferenceGenerator
                    Reference Quantity. 'i_a', 'i_e'

            Reward Function:
                WeightedSumOfErrors: reward_weights 'i_a' = 'i_e' = 0.5

            Visualization:
                MotorDashboard: currents and action plots

            Constraints:
                Current Limit on 'i_a' and 'i_e'

        Control Cycle Time:
            tau = 1e-5 seconds

        State Variables:
            ``['omega' , 'torque', 'i_a', 'i_e', 'u_a', 'u_e', 'u_sup']``

        Observation Space:
            Type: Tuple(State_Space, Reference_Space)

        State Space:
            Box(low=[-1, -1, -1, -1, -1, -1, 0], high=[1, 1, 1, 1, 1, 1, 1])

        Reference Space:
            Box(low=[-1, -1], high=[1, 1])

        Action Space:
            Discrete(8)

        Starting State:
            Zeros on all state variables.

        Episode Termination:
            Termination if current limits are violated.
    """
    def __init__(self, supply=None, converter=None, motor=None, load=None, ode_solver=None, noise_generator=None,
                 reward_function=None, reference_generator=None, visualization=None, state_filter=None, callbacks=(),
                 constraints=('i_a', 'i_e'), calc_jacobian=True, tau=1e-5):
        """
        Args:
            supply(env-arg): Specification of the supply to be used in the environment
            converter(env-arg): Specification of the converter to be used in the environment
            motor(env-arg): Specification of the motor to be used in the environment
            load(env-arg): Specification of the load to be used in the environment
            ode_solver(env-arg): Specification of the ode_solver to be used in the environment
            noise_generator(env-arg): Specification of the noise_generator to be used in the environment
            reward_function(env-arg: Specification of the reward_function to be used in the environment
            reference_generator(env-arg): Specification of the reference generator to be used in the environment
            visualization(env-arg): Specification of the visualization to be used in the environment
            constraints(iterable(str/Constraint)): All Constraints of the environment.
                - str: A LimitConstraints for states (episode terminates, if the quantity exceeds the limit)
                 can be directly specified by passing the state name here (e.g. 'i', 'omega')
                 - instance of Constraint: More complex constraints (e.g. the SquaredConstraint can be initialized and
                 passed to the environment.
            calc_jacobian(bool): Flag, if the jacobian of the environment shall be taken into account during the
                simulation. This may lead to speed improvements. Default: True
            tau(float): Duration of one control step in seconds. Default: 1e-5.
            state_filter(list(str)): List of states that shall be returned to the agent. Default: None (no filter)
            callbacks(list(Callback)): Callbacks for user interaction.

        Note on the env-arg type:
            All parameters of type env-arg can be selected as one of the following types:
                - instance: Pass an already instantiated object derived from the corresponding base class
                    (e.g. reward_function=MyRewardFunction()). This is directly used in the environment.
                - dict: Pass a dict to update the default parameters of the default type.
                    (e.g. visualization=dict(state_plots=('omega', 'u')))
                - str: Pass a string out of the registered classes to select a different class for the component.
                    This class is then initialized with its default parameters.
                    The available strings can be looked up in the documentation. (e.g. converter='Disc-2QC')
        """
        default_subconverters = (ps.FiniteFourQuadrantConverter(), ps.FiniteOneQuadrantConverter())
        physical_system = DcMotorSystem(
            supply=initialize(ps.VoltageSupply, supply, ps.IdealVoltageSupply, dict(u_nominal=420.0)),
            converter=initialize(
                ps.PowerElectronicConverter,
                converter,
                ps.FiniteMultiConverter,
                dict(subconverters=default_subconverters)
            ),
            motor=initialize(ps.ElectricMotor, motor, ps.DcPermanentlyExcitedMotor, dict()),
            load=initialize(ps.MechanicalLoad, load, ps.ConstantSpeedLoad, dict(omega_fixed=100.0)),
            ode_solver=initialize(ps.OdeSolver, ode_solver, ps.EulerSolver, dict()),
            noise_generator=initialize(ps.NoiseGenerator, noise_generator, ps.NoiseGenerator, dict()),
            calc_jacobian=calc_jacobian,
            tau=tau
        )
        sub_generators = (
            WienerProcessReferenceGenerator(reference_state='i_a'),
            WienerProcessReferenceGenerator(reference_state='i_e')
        )
        reference_generator = initialize(
            ReferenceGenerator, reference_generator, MultipleReferenceGenerator, dict(sub_generators=sub_generators)
        )
        reward_function = initialize(
            RewardFunction, reward_function, WeightedSumOfErrors, dict(reward_weights=dict(i_a=0.5, i_e=0.5))
        )
        visualization = initialize(
            ElectricMotorVisualization, visualization, MotorDashboard,
            dict(state_plots=('i_a', 'i_e',), action_plots=(0, 1)))
        super().__init__(
            physical_system=physical_system, reference_generator=reference_generator, reward_function=reward_function,
            constraints=constraints, visualization=visualization, state_filter=state_filter, callbacks=callbacks
        )


class ContCurrentControlDcExternallyExcitedMotorEnv(ElectricMotorEnvironment):
    """
        Description:
            Environment to simulate a continuously current controlled externally excited DC Motor

        Key:
            `Cont-CC-ExtExDc-v0`

        Default Components:
            - Supply: IdealVoltageSupply
            - Converter: ContMultiConverter(ContFourQuadrantConverter, ContOneQuadrantConverter)
            - Motor: DcExternallyExcitedMotor
            - Load: ConstantSpeedLoad
            - Ode-Solver: EulerSolver
            - Noise: None

            Reference Generator:
                WienerProcessReferenceGenerator
                    Reference Quantity. 'i_a', 'i_e'

            Reward Function:
                WeightedSumOfErrors: reward_weights 'i_a' = 0.5, 'i_e' = 0.5

            Visualization:
                MotorDashboard: current and action plots

            Constraints:
                Current Limit on 'i_a' and 'i_e'

        Control Cycle Time:
            tau = 1e-4 seconds

        State Variables:
            ``['omega' , 'torque', 'i_a', 'i_e', 'u_a', 'u_e', 'u_sup']``

        Observation Space:
            Type: Tuple(State_Space, Reference_Space)

        State Space:
            Box(low=[-1, -1, -1, -1, -1, -1, 0], high=[1, 1, 1, 1, 1, 1, 1])

        Reference Space:
            Box(low=[-1, -1], high=[1, 1])

        Action Space:
            Box(low=[-1, 0], high=[1, 1])

        Starting State:
            Zeros on all state variables.

        Episode Termination:
            Termination if current limits are violated.
    """
    def __init__(self, supply=None, converter=None, motor=None, load=None, ode_solver=None, noise_generator=None,
                 reward_function=None, reference_generator=None, visualization=None, state_filter=None, callbacks=(),
                 constraints=('i_a', 'i_e'), calc_jacobian=True, tau=1e-4):
        """
        Args:
            supply(env-arg): Specification of the supply to be used in the environment
            converter(env-arg): Specification of the converter to be used in the environment
            motor(env-arg): Specification of the motor to be used in the environment
            load(env-arg): Specification of the load to be used in the environment
            ode_solver(env-arg): Specification of the ode_solver to be used in the environment
            noise_generator(env-arg): Specification of the noise_generator to be used in the environment
            reward_function(env-arg: Specification of the reward_function to be used in the environment
            reference_generator(env-arg): Specification of the reference generator to be used in the environment
            visualization(env-arg): Specification of the visualization to be used in the environment
            constraints(iterable(str/Constraint)): All Constraints of the environment.
                - str: A LimitConstraints for states (episode terminates, if the quantity exceeds the limit)
                 can be directly specified by passing the state name here (e.g. 'i', 'omega')
                 - instance of Constraint: More complex constraints (e.g. the SquaredConstraint can be initialized and
                 passed to the environment.
            calc_jacobian(bool): Flag, if the jacobian of the environment shall be taken into account during the
                simulation. This may lead to speed improvements. Default: True
            tau(float): Duration of one control step in seconds. Default: 1e-4.
            state_filter(list(str)): List of states that shall be returned to the agent. Default: None (no filter)
            callbacks(list(Callback)): Callbacks for user interaction.

        Note on the env-arg type:
            All parameters of type env-arg can be selected as one of the following types:
                - instance: Pass an already instantiated object derived from the corresponding base class
                    (e.g. reward_function=MyRewardFunction()). This is directly used in the environment.
                - dict: Pass a dict to update the default parameters of the default type.
                    (e.g. visualization=dict(state_plots=('omega', 'u')))
                - str: Pass a string out of the registered classes to select a different class for the component.
                    This class is then initialized with its default parameters.
                    The available strings can be looked up in the documentation. (e.g. converter='Disc-2QC')
        """

        physical_system = DcMotorSystem(
            supply=initialize(ps.VoltageSupply, supply, ps.IdealVoltageSupply, dict(u_nominal=420.0)),
            converter=initialize(ps.PowerElectronicConverter, converter, ps.ContFourQuadrantConverter, dict()),
            motor=initialize(ps.ElectricMotor, motor, ps.DcPermanentlyExcitedMotor, dict()),
            load=initialize(ps.MechanicalLoad, load, ps.ConstantSpeedLoad, dict(omega_fixed=100)),
            ode_solver=initialize(ps.OdeSolver, ode_solver, ps.EulerSolver, dict()),
            noise_generator=initialize(ps.NoiseGenerator, noise_generator, ps.NoiseGenerator, dict()),
            calc_jacobian=calc_jacobian,
            tau=tau
        )
        sub_generators = (
            WienerProcessReferenceGenerator(reference_state = 'i_a'),
            WienerProcessReferenceGenerator(reference_state='i_e')
        )
        reference_generator = initialize(
            ReferenceGenerator, reference_generator, MultipleReferenceGenerator, dict(sub_generators=sub_generators)
        )
        reward_function = initialize(
            RewardFunction, reward_function, WeightedSumOfErrors, dict(reward_weights=dict(i_a=0.5, i_e=0.5))
        )
        visualization = initialize(
            (ElectricMotorVisualization, list, tuple),
            visualization, MotorDashboard, dict(state_plots=('i_a, i_e',), action_plots=(0, 1)))
        super().__init__(
            physical_system=physical_system, reference_generator=reference_generator, reward_function=reward_function,
            constraints=constraints, visualization=visualization, state_filter=state_filter, callbacks=callbacks
        )
