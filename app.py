"""
This module is the GUI frontend using Tkinter
for viewing and interacting with the quantum simulation.

The GUI is inspired by the 1-Dimensional Particle States Applet
by Paul Falstad and Quantum Bound States by PhET Colorado,
both originally written in Java.
"""
import numpy as np
from qm import UnitaryOperator1D, Wavefunction1D
from qm.constants import Constants
from matplotlib.backends import backend_tkagg
from animation import QuantumAnimation, scale
import tkinter as tk
from typing import Tuple

np.seterr(all='raise')
# Make numpy raise errors instead of warnings.


class App(QuantumAnimation):
    """
    Interactive QM GUI object using Tkinter and Matplotlib.

    Attributes:
    window [tkinter.Tk]
    canvas [matplotlib.backends.backend_tkagg.FigureCanvasTkAgg]
    menu [tk.Menu]
    measurement_label[tk.Label]
    measure_position_button [tk.Button]
    measure_momentum_button [tk.Button]
    measure_energy_button [tk.Buton]
    mouse_menu_label [tk.Label]
    mouse_menu_tuple [tuple]
    mouse_menu_string [tk.StinrgVar]
    mouse_menu [tk.OptionMenu]
    enter_function_label [tk.Label]
    enter_function [tk.Entry]
    update_wavefunction_button [tk.Button]
    clear_wavefunction_button [tk.Button]
    potential_menu_dict [dict]
    potential_menu_string [tk.StringVar]
    previous_potential_menu_string [str]
    potential_menu [tk.OptionMenu]
    enter_potential_label [tk.Label]
    enter_potential [tk.Entry]
    update_potential_button [tk.Button]
    slider_speed_label [tk.LabelFrame]
    slider_speed [tk.Scale]
    quit_button [tk.Button]
    fpi_before_pause [None, int]
    scale_y [float]
    potential_is_reshaped [bool]
    """

    # For those methods that pause the time evolution
    # while receiving mouse input, the fpi_before_pause
    # attribute records the number of time evolutions
    # per animation frame or fpi right before the pause.
    # This is then used to set the fpi to its original state
    # when the mouse button is released. This attribute, as well
    # as the inherited fpi attribute, should not be changed
    # at all if the mouse is only clicked once.
    #
    # The scale_y attribute scales the y mouse input values
    # in order to match the proper scaling of the potential V(x).
    #
    # The potential_is_reshaped bool attribute notifies
    # the method update_potential_by_sketch whether the potential
    # has been already changed through mouse input. This is
    # so that the potential is not rescaled (through changing
    # the scale_y attribute) whenever the update_potential_by_sketch
    # is called more than once. This attribute must be set to false
    # whenever update_potential_by_preset or update_potential_by_name
    # is called.
    #
    # The attribute potential_menu_string is changed to
    # "Choose Preset Potential V(x)" whenever a method that changes
    # the potential without using a preset is called.

    def __init__(self) -> None:
        """
        Initializer.
        """

        self.window = tk.Tk()
        self.window.title("Bounded Wavefunction in 1D BY FAYSSAL CHOKRI REVONS DEVELOPERS V 1.0")

        # Thanks to StackOverflow user rudivonstaden for
        # giving a way to get the colour of the tkinter widgets:
        # https://stackoverflow.com/questions/11340765/
        # default-window-colour-tkinter-and-hex-colour-codes
        #
        #     https://stackoverflow.com/q/11340765
        #     [Question by user user2063:
        #      https://stackoverflow.com/users/982297/user2063]
        #
        #     https://stackoverflow.com/a/11342481
        #     [Answer by user rudivonstaden:
        #      https://stackoverflow.com/users/1453643/rudivonstaden]
        #
        colour = self.window.cget('bg')
        if colour == 'SystemButtonFace':
            colour = "#F0F0F0"

        # Set plot resolution
        # width = self.window.winfo_screenwidth()
        # print(width)
        # dpi = 250

        C = Constants()
        x = np.linspace(C.x0, C.L + C.x0, C.N)

        # Defaults
        V = "(x)**2/2"
        psi = np.exp(-0.5*((x-0.25)/0.05)**2)

        # Other
        # V = rect(8*x)
        # psi = np.exp(-0.5*((x-0.25)/0.05)**2 - 160j*x*np.pi)

        # Initialize the inherited animation object
        QuantumAnimation.__init__(self, function=psi, potential=V)

        # Canvas

        # A quick example of how to integrate a matplotlib animation into a
        # tkinter gui is given by this Stack Overflow question and answer:

        # https://stackoverflow.com/q/21197728
        # [Question by user3208454:
        # https://stackoverflow.com/users/3208454/user3208454]

        # https://stackoverflow.com/a/21198403
        # [Answer by HYRY:
        # https://stackoverflow.com/users/772649/hyry]

        self.canvas = backend_tkagg.FigureCanvasTkAgg(
            self.figure,
            master=self.window
            )
        self.canvas.get_tk_widget().grid(
            row=0,
            column=0,
            rowspan=20,
            columnspan=2
            )
        self.canvas.get_tk_widget().bind(
                "<B1-Motion>",
                self.sketch)
        self.canvas.get_tk_widget().bind(
                "<ButtonRelease-1>",
                self.sketch)
        self.canvas.get_tk_widget().bind(
                "<MouseWheel>",
                self.mouse_wheel_handler)
        self.canvas.get_tk_widget().bind(
                "<Button-4>",
                self.mouse_wheel_handler)
        self.canvas.get_tk_widget().bind(
                "<Button-5>",
                self.mouse_wheel_handler)

        # Thanks to StackOverflow user user1764386 for
        # giving a way to change the background colour of a plot.
        #
        #    https://stackoverflow.com/q/14088687
        #    [Question by user user1764386:
        #     https://stackoverflow.com/users/1764386/user1764386]
        #
        self.figure.patch.set_facecolor(colour)

        # Show Probability Distribution/Wavefunction
        # TODO: Don't use a long and unnecessary lambda function
        b = tk.Button(self.window,
                      text='View Probability Distribution',
                      command=lambda:
                          [self.display_probability(),
                           self.change_view.config(
                                   text='View Wavefunction')] if (
                                         self._display_probs is False) else [
                                              self.display_wavefunction(),
                                              self.change_view.config(
                                                    text='View '
                                                         'Probability'
                                                         ' Distribution')])
        self.change_view = b
        self.change_view.grid(row=1, column=3, columnspan=2, padx=(10, 10))

        # Show Wavefunction in Position/Momentum Basis
        b2 = tk.Button(self.window,
                      text='View in Momentum Basis',
                      command=lambda:
                          [self.display_momentum(),
                           self.change_view2.config(
                                   text='View in Position Basis')] if (
                                         self._show_p is False) else [
                                              self.display_position(),
                                              self.change_view2.config(
                                                    text='View in Momentum'
                                                         ' Basis')])
        self.change_view2 = b2
        self.change_view2.grid(row=2, column=3, columnspan=2, padx=(10, 10))

        # Measurement label
        self.measurement_label = tk.Label(self.window, text="Measure:")
        self.measurement_label.grid(row=3, column=3, columnspan=3,
                                    sticky=tk.E + tk.W + tk.S,
                                    padx=(10, 10)
                                    )

        # Measure position button
        self.measure_position_button = tk.Button(
            self.window,
            text='Position',
            command=self.measure_position
            )
        self.measure_position_button.grid(
            row=4,
            column=3,
            columnspan=2,
            sticky=tk.E + tk.W + tk.N + tk.S,
            padx=(10, 10)
            )

        # Measure momentum button
        self.measure_momentum_button = tk.Button(
            self.window,
            text='Momentum',
            command=self.measure_momentum
            )
        self.measure_momentum_button.grid(
            row=5,
            column=3,
            columnspan=2,
            sticky=tk.E + tk.W + tk.N + tk.S,
            padx=(10, 10)
            )

        # Measure energy button
        self.measure_energy_button = tk.Button(
            self.window,
            text='Energy',
            command=self.measure_energy
            )
        self.measure_energy_button.grid(
            row=6,
            column=3,
            columnspan=2,
            sticky=tk.E + tk.W + tk.N,
            padx=(10, 10)
            )

        # Mouse menu dropdown
        self.mouse_menu_label = tk.Label(
            self.window,
            text="Mouse:"
            )
        self.mouse_menu_label.grid(
            row=7,
            column=3,
            sticky=tk.W + tk.E + tk.S,
            padx=(10, 10),
            columnspan=2
            )
        # Mouse menu tuple
        self.mouse_menu_tuple = (
            "Reshape Wavefunction",
            "Reshape Wavefunction in Real Time",
            "Select Energy Level",
            "Reshape Potential V(x)"
            )
        # Mouse menu string
        self.mouse_menu_string = tk.StringVar(self.window)
        self.mouse_menu_string.set("Reshape Wavefunction")
        self.mouse_menu = tk.OptionMenu(
            self.window,
            self.mouse_menu_string,
            *self.mouse_menu_tuple,
            command=self.mouse_menu_handler
            )
        self.mouse_menu.grid(row=8, column=3,
            columnspan=2,
            sticky=tk.W + tk.E + tk.N,
            padx=(10, 10)
            )

        # Wavefunction entry field
        self.enter_function_label = tk.Label(
                self.window,
                text="Enter Wavefunction \u03C8(x)"
                )

        self.enter_function_label.grid(row=9, column=3,
                                       columnspan=2,
                                       sticky=tk.E + tk.W + tk.S,
                                       padx=(10, 10))
        self.enter_function = tk.Entry(self.window)
        self.enter_function.bind(
            "<Return>",
            self.update_wavefunction_by_name
            )
        self.enter_function.grid(row=10, column=3,
                                 columnspan=2,
                                 sticky=tk.W + tk.E + tk.N + tk.S,
                                 padx=(11, 11)
                                 )

        # Update wavefunction button
        b2 = tk.Button(self.window, text='OK',
                       command=self.update_wavefunction_by_name)
        self.update_wavefunction_button = b2
        self.update_wavefunction_button.grid(row=11, column=3,
                                             columnspan=2,
                                             sticky=tk.N + tk.W + tk.E,
                                             padx=(10, 10)
                                             )

        # Right click Menu
        self.menu = tk.Menu(self.window, tearoff=0)
        self.menu.add_command(label="Measure Position",
                              command=self.measure_position)
        self.menu.add_command(label="Measure Momentum",
                              command=self.measure_momentum)
        self.menu.insert_separator(3)
        self.menu.add_command(label="Reshape Wavefunction",
                              command=self.rightclick_reshape_wavefunction)
        self.menu.add_command(label="Reshape Potential",
                              command=self.rightclick_reshape_potential)
        self.menu.add_command(label="Select Energy Level",
                              command=self.rightclick_select_energylevel)
        self.menu.insert_separator(7)
        self.menu.add_command(label="Toggle Show Energy Levels",
                              command=self.rightclick_toggle_energylevel)
        self.menu.add_command(label="Toggle Expectation Values",
                              command=self.toggle_expectation_values)
        self.menu.insert_separator(9)
        self.menu.add_command(label="Higher Stationary State",
                              command=self.higher_energy_eigenstate)
        self.menu.add_command(label="Lower Stationary State",
                              command=self.lower_energy_eigenstate)
        self.window.bind("<ButtonRelease-3>", self.popup_menu)
        self.window.bind("<Up>", self.higher_energy_eigenstate)
        self.window.bind("<Down>", self.lower_energy_eigenstate)
        # self.window.bind("<Control>", lambda *arg: print("ctrl printed"))

        self.sliders1 = []
        self.sliders1_count = -1
        self.sliders2 = []
        self.sliders2_count = -1
        self.clear_wavefunction_button = None
        self.potential_menu_dict = {
            "Infinite Square Well": "0",
            "Simple Harmonic Oscillator": "x**2/2",
            "Barrier in SHO": "x**2 + rect(150*x)/10",
            # "Potential Barrier": "10*rect(32*x)",
            # "Double stepped potential": 
            # "1/4 - (Sum(rect(4*b*a*(x-0.07)), "
            # "(b, 1, 5)) + Sum(rect(4*b*a*(x+0.07))," 
            # "(b, 1, 5)))/20",
            "Potential Well": "-rect(4*x)/2",
            # "Potential Well and Barrier":
            # "-2*rect(16*(x+1/4)) + 2*rect(16*(x-1/4))",
            # "Coulomb": "-1/(100*sqrt(x**2))",
            "Double Well":
                "(1-rect((21/10)*(x-1/4))-rect((21/10)*(x+1/4)))/10",
            # "Double Well 2": "(1-rect(2*x)+rect(50*x)/10)/5",
            # "Double Well 3": "1/10-a*rect(2*k1*x)/10 + b*rect(50*x)/15",
            # "Many Wells": "a*(1/60)*Sum(rect(150*b*(x-i*0.1+0.5)), (i, 0, 10))",
            "Many Wells": "a*0.017*Sum(rect(150*b*(x-i*0.1+0.5)), (i, 0, 10))",
            # "Simple Harmonic Oscillators": 
            #     "Sum(rect(int(4*l)*(x+0.8725 - j/int(4*l)))*"
            #     "(2*(x+0.8725 - j/int(4*l)))**2, (j, 1, 10))",
            "Triangular Well": "sqrt(x**2)"
            }
        self.potential_menu_string = tk.StringVar(self.window)
        self.potential_menu_string.set("Choose Preset Potential V(x)")
        self.previous_potential_menu_string = "Choose Preset Potential V(x)"
        self.potential_menu = None
        self.enter_potential_label = None
        self.enter_potential = None
        self.update_potential_button = None
        self.slider_speed_label = None
        self.slider_speed = None
        self.quit_button = None
        self.set_widgets_after_enter_wavefunction(init_call=True)

        self.animation_loop()

        # Store the animation speed before a pause
        self.fpi_before_pause = None

        self.scale_y = 0.0
        self.potential_is_reshaped = False

        # self.toggle_energy_levels()

    def destroy_wavefunction_sliders(self) -> None:
        """
        Destroy the wavefunction parameter sliders.
        """
        for slider in self.sliders1:
            slider.destroy()
        self.sliders1 = []
        self.sliders1_count = 0

    def set_widgets_after_enter_wavefunction(self, init_call=False) -> None:
        """
        Set the widgets after the enter wavefunction button.
        """
        prev_sliders1_count = self.sliders1_count
        self.destroy_wavefunction_sliders()

        if len(self.psi_params) > 0:
            for i in range(len(self.psi_params)):
                self.sliders1.append(
                    tk.Scale(self.window, 
                             label="change %s: " % str(self.psi_params[i][0]),
                             from_=-2, to=2,
                             resolution=0.01,
                             orient=tk.HORIZONTAL,
                             length=200,
                             command=self.update_wavefunction_by_slider
                            )
                )
                self.sliders1[i].grid(
                    row=12 + self.sliders1_count, 
                    column=3, columnspan=2, 
                    sticky=tk.N+tk.W+tk.E, padx=(10, 10)
                )
                self.sliders1[i].set(self.psi_params[i][1])
                self.sliders1_count += 1

        if prev_sliders1_count != self.sliders1_count:
            self.set_widgets_after_wavefunction_sliders(init_call)

    def set_widgets_after_wavefunction_sliders(self, init_call) -> None:
        """
        Set widgets after wavefunction sliders.
        """
        # Clear wavefunction button
        if self.clear_wavefunction_button is not None:
            self.clear_wavefunction_button.destroy()
        b3 = tk.Button(self.window,
                       text='Clear Wavefunction',
                       command=self.clear_wavefunction
                       )
        self.clear_wavefunction_button = b3
        self.clear_wavefunction_button.grid(row=12 + self.sliders1_count, 
                                            column=3,
                                            columnspan=2,
                                            sticky=tk.W + tk.E,
                                            padx=(10, 10)
                                            )
        # Drop down for preset potentials
        if self.potential_menu is not None:
            self.potential_menu.destroy()
        self.potential_menu = tk.OptionMenu(
            self.window,
            self.potential_menu_string,
            *tuple(key for key in self.potential_menu_dict),
            command=self.update_potential_by_preset
            )
        self.potential_menu.grid(row=13 + self.sliders1_count,
                                 column=3,
                                 sticky=tk.W + tk.E,
                                 padx=(10, 10)
                                )

        # Potential function entry field
        if self.enter_potential_label is not None:
            self.enter_potential_label.destroy()
        self.enter_potential_label = tk.Label(
                self.window, text="Enter Potential V(x)")
        self.enter_potential_label.grid(
            row=14 + self.sliders1_count,
            column=3,
            sticky=tk.W + tk.E + tk.S,
            padx=(10, 10))
        if self.enter_potential is not None:
            self.enter_potential.destroy()
        self.enter_potential = tk.Entry(self.window)
        self.enter_potential.bind("<Return>", self.update_potential_by_name)
        self.enter_potential.grid(row=15 + self.sliders1_count, 
                                  column=3, columnspan=3,
                                  sticky=tk.W + tk.E + tk.N + tk.S,
                                  padx=(10, 10)
                                 )
        if self.update_potential_button is not None:
            self.update_potential_button.destroy()
        b4 = tk.Button(self.window,
                       text='OK',
                       command=self.update_potential_by_name)
        self.update_potential_button = b4
        self.update_potential_button.grid(row=16 + self.sliders1_count, 
                                          column=3,
                                          columnspan=2,
                                          sticky=tk.N + tk.W + tk.E,
                                          padx=(10, 10)
                                          )
        if not init_call:
            # TODO: refactor the code within this if block,
            # which deals with resetting potential function parameter
            # sliders after the wavefunction parameter sliders are
            # changed.
            params = [self.sliders2[i].get() 
                    for i in range(len(self.sliders2))]
            self.destroy_potential_sliders()
            self.set_potential_sliders()
            self.set_widgets_after_potential_sliders()
            if len(params) != 0:
                for i in range(len(params)):
                    self.sliders2[i].set(params[i])
                self.V = lambda x: self.V_base(x, *params)
                self.V_x = scale(self.V(self.x), 15)
                self.U_t = UnitaryOperator1D(self.V)
                self.lines[4].set_ydata(self.V_x/self.scale_y)
                self.update_energy_levels()
        else:
            self.set_widgets_after_enter_potential()

    def set_widgets_after_enter_potential(self) -> None:
        """
        Set the widgets after the enter potential button.
        """
        prev_sliders2_count = self.sliders2_count
        self.destroy_potential_sliders()
        if len(self.V_params) > 0:
            self.set_potential_sliders()

        if prev_sliders2_count != self.sliders2_count:
            self.set_widgets_after_potential_sliders()

    def destroy_potential_sliders(self) -> None:
        """
        Destroy the potential sliders
        """
        for slider in self.sliders2:
            slider.destroy()
        self.sliders2 = []
        self.sliders2_count = 0

    def set_potential_sliders(self) -> None:
        """
        Set the sliders for the parameters that control
        the potential function.
        """
        for i in range(len(self.V_params)):
            self.sliders2.append(
                tk.Scale(self.window, 
                         label="change %s: " % str(self.V_params[i][0]),
                         from_=-2, to=2,
                         resolution=0.01,
                         orient=tk.HORIZONTAL,
                         length=200,
                         command=self.update_potential_by_slider
                         )
            )
            self.sliders2[i].grid(
                row=17 + self.sliders2_count + self.sliders1_count, 
                column=3, columnspan=2, 
                sticky=tk.N+tk.W+tk.E, padx=(10, 10)
            )
            self.sliders2[i].set(self.V_params[i][1])
            self.sliders2_count += 1

    def set_widgets_after_potential_sliders(self) -> None:
        """
        Set the widgets after the parameter sliders for the potential
        """
        total_sliders_count = self.sliders2_count + self.sliders1_count
        # Animation speed slider
        if self.slider_speed_label is not None:
            self.slider_speed_label.destroy()
        self.slider_speed_label = tk.LabelFrame(
                self.window, text="Animation Speed")
        self.slider_speed_label.grid(row=17 + total_sliders_count, 
                                        column=3, padx=(10, 10))
        if self.slider_speed is not None:
            self.slider_speed.destroy()
        self.slider_speed = tk.Scale(self.slider_speed_label,
                                        from_=0, to=10,
                                        orient=tk.HORIZONTAL,
                                        length=200,
                                        command=self.change_animation_speed
                                        )
        self.slider_speed.grid(row=18 + total_sliders_count,
                                column=3, padx=(10, 10))
        self.slider_speed.set(1)
        # Quit button
        if self.quit_button is not None:
            self.quit_button.destroy()
        self.quit_button = tk.Button(
                self.window, text='QUIT', command=self.quit)
        self.quit_button.grid(row=19  + total_sliders_count, 
                                column=3)

    def update_wavefunction_by_slider(self, *event: tk.Event) -> None:
        """
        Update the wavefunction by sliders.
        """
        params = [self.sliders1[i].get() 
                  for i in range(len(self.sliders1))]
        psi_func = lambda x: self.psi_base(x, *params)
        self.psi = Wavefunction1D(psi_func)
        self.psi.normalize()
        self.update_expected_energy_level()

    def update_potential_by_slider(self, *event: tk.Event) -> None:
        """
        Update the potential by sliders.
        """
        if not self.potential_is_reshaped:
            if np.amax(self.V_x > 0):
                self.scale_y = np.amax(self.V_x[1:-2])/(
                    self.bounds[-1]*0.95)
            elif np.amax(self.V_x < 0):
                self.scale_y = np.abs(np.amin(self.V_x[1:-2]))/(
                    self.bounds[-1]*0.95)
            else:
                self.scale_y = 1.0
            self.potential_is_reshaped = True
        params = []
        for i in range(len(self.sliders2)):
            params.append(self.sliders2[i].get())
        self.V = lambda x: self.V_base(x, *params)
        self.V_x = scale(self.V(self.x), 15)
        self.U_t = UnitaryOperator1D(self.V)
        # Re-draw the potential
        self.lines[4].set_ydata(self.V_x/self.scale_y)
        self.update_energy_levels()

    def mouse_wheel_handler(self, event: tk.Event) -> None:
        """
        Handle mouse wheel input. When the mouse is over the canvas
        this controls how the drawing of the potential is scaled.
        """
        if event.delta == -120 or event.num == 5:
            self.rescale_potential_graph(1.1)
        elif event.delta == 120 or event.num == 4:
            self.rescale_potential_graph(0.9)

    def rescale_potential_graph(self, scale_y: float) -> None:
        """
        Rescale the graph of the potential
        """
        if not self.potential_is_reshaped:
            if np.amax(self.V_x > 0):
                self.scale_y = np.amax(self.V_x[1:-2])/(
                    self.bounds[-1]*0.95)
            elif np.amax(self.V_x < 0):
                self.scale_y = np.abs(np.amin(self.V_x[1:-2]))/(
                    self.bounds[-1]*0.95)
            else:
                self.scale_y = 1.0
            self.potential_is_reshaped = True
        self.scale_y *= scale_y
        V_max = self.bounds[-1]*0.95*self.scale_y*self._scale
        self.lines[9].set_text("E = %.0f" % (V_max))
        self.lines[10].set_text("E = %.0f" % (-V_max))
        self.lines[4].set_ydata(self.V_x/self.scale_y)
        self.update_energy_levels()

    def popup_menu(self, event: tk.Event) -> None:
        """
        popup menu upon right click.
        """
        self.menu.tk_popup(event.x_root, event.y_root, 0)

    def rightclick_reshape_potential(self, *event: tk.Event) -> None:
        """
        This function is called if reshape wavefunction has been set.
        """
        self.mouse_menu_string.set(self.mouse_menu_tuple[3])
        if self.show_energy_levels():
            self.toggle_energy_levels()

    def rightclick_reshape_wavefunction(self, *event: tk.Event) -> None:
        """
        This function is called if reshape wavefunction has been set.
        """
        self.mouse_menu_string.set(self.mouse_menu_tuple[0])
        if self.show_energy_levels():
            self.toggle_energy_levels()

    def rightclick_select_energylevel(self, *event: tk.Event) -> None:
        """
        This function is called
        if the option select energy level has been selected from right click.
        """
        if not self.show_energy_levels():
            self.mouse_menu_string.set(self.mouse_menu_tuple[2])
            self.toggle_energy_levels()
        elif self.show_energy_levels():
            self.mouse_menu_string.set(self.mouse_menu_tuple[2])

    def rightclick_toggle_energylevel(self, *event: tk.Event) -> None:
        """
        This function is called
        if toggle energy level has been selected from right click.
        """
        if self.show_energy_levels():
            self.mouse_menu_string.set("Reshape Wavefunction")
        self.toggle_energy_levels()

    def mouse_menu_handler(self, *event: tk.Event) -> None:
        """
        Mouse menu handler.
        """
        if (str(self.mouse_menu_string.get()) == self.mouse_menu_tuple[2]
                and not self.show_energy_levels()):
            self.toggle_energy_levels()
        elif self.show_energy_levels() and (
                str(self.mouse_menu_string.get()) != self.mouse_menu_tuple[2]):
            self.toggle_energy_levels()

    def sketch(self, event: tk.Event) -> None:
        """
        Respond to mouse interaction on the canvas.
        """
        if str(self.mouse_menu_string.get()) == self.mouse_menu_tuple[0]:
            self.update_wavefunction_by_sketch_while_paused(event)
        elif str(self.mouse_menu_string.get()) == self.mouse_menu_tuple[1]:
            self.update_wavefunction_by_sketch(event)
        elif str(self.mouse_menu_string.get()) == self.mouse_menu_tuple[2]:
            self.update_wavefunction_to_eigenstate(event)
        elif str(self.mouse_menu_string.get()) == self.mouse_menu_tuple[3]:
            self.update_potential_by_sketch(event)

    def update_wavefunction_by_name(self, *event: tk.Event) -> None:
        """
        Update the wavefunction given entry input.
        """
        self.set_wavefunction(self.enter_function.get())
        self.update_expected_energy_level()
        self.set_widgets_after_enter_wavefunction()

    def _update_wavefunction_by_sketch(self, x: float, y: float) -> None:
        """
        Helper function for update_wavefunction_by_sketch
        and update_wavefunction_by_sketch_while_paused.
        """
        if not self._show_p:
            if self._display_probs:
                psi2_new = change_array(
                    self.x, self.psi.x*np.conj(self.psi.x)/3, x, y)
                self.set_wavefunction(np.sqrt(3*psi2_new),
                                    normalize=False)
            else:
                self.set_wavefunction(change_array(
                    self.x, self.psi.x, x, y), normalize=False)
        else:
            if (x > self.x[self.N//4] and x < self.x[3*self.N//4]):
                # y = y*np.exp(-(x - self.x[self.N//2])**2/(
                # 2*((self.x[3*self.N//4] - self.x[self.N//4])/2)**2))
                if self._display_probs:
                    phases = np.angle(self.psi.p)
                    psi2_new = change_array(
                        self.x, self.psi.p*np.conj(self.psi.p)/3, x, y)
                    psi_new = np.sqrt(3*psi2_new)*np.exp(1.0j*phases)
                    self.set_wavefunction(np.copy(np.fft.ifft(
                                          np.fft.ifftshift((psi_new)*(self.N/10)))), 
                                          normalize=False)
                else: 
                    new_p = change_array(self.x, self.psi.p, x, y)
                    self.set_wavefunction(np.copy(np.fft.ifft(
                        np.fft.ifftshift((new_p)*(self.N/10)))), normalize=False)

    def update_wavefunction_by_sketch(self, event: tk.Event) -> None:
        """
        Update the wavefunction using the mouse.
        """
        x, y = self.locate_mouse(event)
        self._update_wavefunction_by_sketch(x, y)
        self.update_expected_energy_level()


    def update_wavefunction_to_eigenstate(self, event: tk.Event) -> None:
        """
        Update the wavefunction to an eigenstate.
        """
        x, y = self.locate_mouse(event)
        if not self.potential_is_reshaped:
            if np.amax(self.V_x > 0):
                self.scale_y = np.amax(self.V_x[1:-2])/(
                    self.bounds[-1]*0.95)
            elif np.amax(self.V_x < 0):
                self.scale_y = np.abs(np.amin(self.V_x[1:-2]))/(
                    self.bounds[-1]*0.95)
            else:
                self.scale_y = 1.0
        energy = y*self.scale_y*self.U_t._scale
        self.set_to_eigenstate(energy, self.scale_y)
        self.update_expected_energy_level()

    def update_wavefunction_by_sketch_while_paused(
            self, event: tk.Event) -> None:
        """
        Update the wavefunction with the mouse, while pausing
        the  time evolution.
        """

        x, y = self.locate_mouse(event)

        # Set the animation speed
        # Later versions of Tkinter have full support for event.type.
        # This is not the case in older versions of Tkinter,
        # but there is something similar called event.num. Therefore we use
        # both event.type and event.num.
        if (str(event.type) == "Motion" or event.num != 1) and (
                self.fpi_before_pause is None):
            self.fpi_before_pause = self.fpi
            self.fpi = 0
        elif (str(event.type) == "ButtonRelease" or event.num == 1) and (
                self.fpi_before_pause is not None):
            self.fpi = self.fpi_before_pause
            self.fpi_before_pause = None
        self._update_wavefunction_by_sketch(x, y)
        self.update_expected_energy_level()

    def clear_wavefunction(self, *args: tk.Event) -> None:
        """
        Set the wavefunction to zero.
        """
        self.set_wavefunction("0")
        self.update_expected_energy_level()

    def update_potential_by_name(self, *event: tk.Event) -> None:
        """
        Update the potential using the potential entry input.
        """
        self.potential_is_reshaped = False
        self.potential_menu_string.set("Choose Preset Potential V(x)")
        self.previous_potential_menu_string = "Choose Preset Potential V(x)"
        no_prev_param_sliders = True if len(self.V_params) == 0 else False
        self.set_unitary(self.enter_potential.get())
        self.update_energy_levels()
        if not no_prev_param_sliders or len(self.V_params) > 0:
            self.set_widgets_after_enter_potential()

    def update_potential_by_preset(self, name: str) -> None:
        """
        Update the potential from the dropdown menu.
        """
        self.potential_is_reshaped = False
        no_prev_param_sliders = True if len(self.V_params) == 0 else False
        if self.previous_potential_menu_string != name:
            if (name == "Potential Barrier" or
                name == "Potential Well and Barrier"):
                self.set_wavefunction("0")
                self.set_unitary(self.potential_menu_dict[name])
                # elif (name == "0"):
                # self.set_unitary(self.potential_menu_dict[name])
            else:
                self.set_unitary(self.potential_menu_dict[name])
            self.previous_potential_menu_string = name
        self.update_energy_levels()
        if not no_prev_param_sliders or len(self.V_params) > 0:
            self.set_widgets_after_enter_potential()
        if (name == "Infinite Square Well"):
            self.rescale_potential_graph(0.0125)
        if (name == "Barrier in SHO"):
            self.rescale_potential_graph(0.5)

    def update_potential_by_sketch(self, event: tk.Event) -> None:
        """
        Update the potential using the mouse.
        """

        if not self._show_p:
            x, y = self.locate_mouse(event)

            # print(np.amax(self.V_x[1:-2]))
            # print (str(event.state))

            # This code block is reached right
            # when the mouse is clicked and held down
            if (str(event.type) == "Motion" or event.num != 1) and (
                    self.fpi_before_pause is None):

                # Get a scale for the y-coordinates in order
                # for it to match up with the potential
                if not self.potential_is_reshaped:
                    if np.amax(self.V_x > 0):
                        self.scale_y = np.amax(self.V_x[1:-2])/(
                            self.bounds[-1]*0.95)
                    elif np.amax(self.V_x < 0):
                        self.scale_y = np.abs(np.amin(self.V_x[1:-2]))/(
                            self.bounds[-1]*0.95)
                    else:
                        self.scale_y = 1.0
                    self.potential_is_reshaped = True

                # Set the animation speed zero
                self.fpi_before_pause = self.fpi
                self.fpi = 0

                # Change the potential name to V(x)
                self.V_name = "V(x)"
                self.V_latex = "$V(x)$"
                self.lines[5].set_text(
                        "$H = %s + $%s, \n%s" % (self._KE_ltx,
                                                self.V_latex, self._lmts_str))
                self._main_msg = self.lines[5].get_text()

            # This code block is run right after the mouse has been held down
            elif (str(event.type) == "ButtonRelease" or event.num == 1) and (
                    self.fpi_before_pause is not None):
                # self.V_x = change_array(
                #     self.x, self.V_x, x, y, gradual=False)
                self.U_t = UnitaryOperator1D(np.copy(self.V_x))
                self.potential_menu_string.set("Choose Preset Potential V(x)")
                tmp_str = "Choose Preset Potential V(x)"
                self.previous_potential_menu_string = tmp_str

                # Resume the animation speed
                self.fpi = self.fpi_before_pause
                self.fpi_before_pause = None

            # This elif handles the case when mouse is clicked only once
            elif (str(event.type) == "ButtonRelease"
                or event.num == 1) and (self.fpi_before_pause is None):

                # note that code within this elif statement is copied
                # from other places in this function

                # Get a scale for the y-coordinates
                # in order for it to match up with the potential
                if not self.potential_is_reshaped:
                    if np.amax(self.V_x > 0):
                        self.scale_y = np.amax(self.V_x[1:-2])/(
                            self.bounds[-1]*0.95)
                    elif np.amax(self.V_x < 0):
                        self.scale_y = np.abs(np.amin(self.V_x[1:-2]))/(
                            self.bounds[-1]*0.95)
                    else:
                        self.scale_y = 1.0
                    self.potential_is_reshaped = True

                self.V_x = change_array(
                    self.x, self.V_x, x, y, gradual=False)
                self.V_name = "V(x)"
                self.V_latex = "$V(x)$"
                self.U_t = UnitaryOperator1D(np.copy(self.V_x))
                self.lines[5].set_text(
                        "$H = %s + $%s, \n%s" % (self._KE_ltx,
                                                self.V_latex, self._lmts_str))
                self._main_msg = self.lines[5].get_text()
                self.potential_menu_string.set("Choose Preset Potential V(x)")
                tmp_str = "Choose Preset Potential V(x)"
                self.previous_potential_menu_string = tmp_str

            # Re-draw the potential
            y *= self.scale_y
            self.V_x = change_array(
                    self.x, self.V_x, x, y, gradual=False)
            if np.amax(self.V_x > 0):
                self.lines[4].set_ydata(self.V_x/self.scale_y)
            elif np.amax(self.V_x < 0):
                self.lines[4].set_ydata(self.V_x/self.scale_y)
            else:
                self.lines[4].set_ydata(self.x*0.0)
            self.update_energy_levels()

    def change_animation_speed(self, event: tk.Event) -> None:
        """
        Change the animation speed.
        """
        self.fpi = self.slider_speed.get()

    def locate_mouse(self, event: tk.Event) -> Tuple[float, float]:
        """
        Locate the position of the mouse with respect to the
        coordinates displayed on the plot axes.
        """
        ax = self.figure.get_axes()[0]
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        pixel_xlim = [ax.bbox.xmin, ax.bbox.xmax]
        pixel_ylim = [ax.bbox.ymin, ax.bbox.ymax]
        height = self.canvas.get_tk_widget().winfo_height()
        mx = (xlim[1] - xlim[0])/(pixel_xlim[1] - pixel_xlim[0])
        my = (ylim[1] - ylim[0])/(pixel_ylim[1] - pixel_ylim[0])
        x = (event.x - pixel_xlim[0])*mx + xlim[0]
        y = (height - event.y - pixel_ylim[0])*my + ylim[0]
        return x, y

    def quit(self, *event: tk.Event) -> None:
        """
        Quit the application.
        Simply calling self.window.quit() only quits the application
        in the command line, while the GUI itself still runs.
        On the other hand, simply calling self.window.destroy()
        destroys the GUI but doesn't give back control of the command
        line. Therefore both need to be called.
        """
        self.window.quit()
        self.window.destroy()


def change_array(x_arr: np.ndarray, y_arr: np.ndarray,
                 x: float, y: float, gradual=True) -> np.ndarray:
    """
    Given a location x that maps to a value y,
    and an array x_arr which maps to array y_arr, find the closest
    element in x_arr to x. Then, change its corresponding
    element in y_arr with y.
    """

    if (x < x_arr[0]) or (x > x_arr[-1]):
        return y_arr
    closest_index = np.argmin(np.abs(x_arr - x))
    y_arr[closest_index] = y
    n = 1
    if len(x_arr) > 100:
        n = 4 if gradual else 3
    if (closest_index - n >= -1 and 
        closest_index + n <= len(x_arr)):
        for i in range(n):
            if i < n - 1:
                y_arr[closest_index+i] = y
                y_arr[closest_index-i] = y
            elif i == n - 1:
                if gradual:
                    y_arr[closest_index+i] = (y + y_arr[closest_index+i])/2.0
                    y_arr[closest_index-i] = (y + y_arr[closest_index-i])/2.0
                else:
                    y_arr[closest_index+i] = y
                    y_arr[closest_index-i] = y

    return y_arr


if __name__ == "__main__":
    # from matplotlib.pyplot import xkcd
    # with xkcd():
    run = App()
    tk.mainloop()
